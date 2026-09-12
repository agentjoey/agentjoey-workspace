#!/usr/bin/env python3
"""Decide whether a Linear repair/roadmap pass is worth running, and why.

The work loop (pull an issue -> claim -> build -> close) keeps Linear in sync for
free, because the agent starts from the issue and its identifier ends up in the
commit. This script exists for the work that skipped the loop: human hotfixes,
another agent's push, an emergency commit.

So it classifies every commit since the last sync as:
  ticketed   - carries an issue identifier; the loop handled it, nothing to do
  trivial    - chore/docs/ci/revert; deliberately never ticketed
  unticketed - the only work a repair pass has any reason to look at

No unticketed work -> not due -> the agent stops without loading any Linear
state at all. That no-op is the point: upkeep should cost nothing when the loop
is working.

Usage:
  roadmap-gate.py                  # compact brief as JSON (default; cheap to read)
  roadmap-gate.py --verbose        # add full commit list and changed paths
  roadmap-gate.py --check          # exit 0 = due, 10 = not due (prints one line)
  roadmap-gate.py --force          # due regardless of cadence
  roadmap-gate.py --record --note "closed AGT-45; 1 recorded"
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

CONFIG_NAME = ".linear-roadmap.json"
STATE_NAME = ".linear-roadmap.state.json"

DEFAULT_CADENCE = {
    "everyDays": 7,
    "everyUnticketedMerges": 3,
    "everyUnticketedCommits": 10,
    "roadmapReviewDays": 14,
    "firstRunLookbackDays": 30,
}
# Accepted for compatibility with the older, git-reconciliation-shaped config.
CADENCE_ALIASES = {
    "everyMergedPRs": "everyUnticketedMerges",
    "everyCommits": "everyUnticketedCommits",
}

DEFAULT_TRIVIAL = [
    r"^(chore|docs|style|ci|build|test)(\(.+\))?!?:",
    r"^Revert ",
    r"^Merge branch ",
    r"^bump ",
]

# Tokens shaped like a Linear identifier that never are one.
NOT_AN_ISSUE = {
    "UTF", "SHA", "ISO", "RFC", "IPV", "HTTP", "HTTPS", "TLS", "AES", "RSA",
    "MD", "CVE", "ES", "PEP", "GPT", "LTS", "X", "NODE", "PY", "HTML", "CSS",
}
IDENTIFIER_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,9})-(\d{1,6})\b")

REC, FLD = "\x1e", "\x1f"


def fail(msg: str) -> None:
    print(f"roadmap-gate: {msg}", file=sys.stderr)
    sys.exit(1)


def git(*args: str, cwd: str) -> str:
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    return res.stdout.strip() if res.returncode == 0 else ""


def repo_root() -> str:
    root = git("rev-parse", "--show-toplevel", cwd=os.getcwd())
    if not root:
        fail("not inside a git repository")
    return root


def load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as exc:
        fail(f"cannot read {os.path.basename(path)}: {exc}")
    return {}


def now() -> datetime:
    return datetime.now(timezone.utc)


def parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def commit_exists(root: str, sha: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=root, capture_output=True, check=False,
    ).returncode == 0


def commit_range(root: str, last_sha, fallback_days: int):
    """Return (range_expr, human_label). Falls back to a time window on first run."""
    head = git("rev-parse", "HEAD", cwd=root)
    if last_sha and commit_exists(root, last_sha):
        return f"{last_sha}..HEAD", f"{last_sha[:8]}..{head[:8]}"
    since = (now() - timedelta(days=fallback_days)).strftime("%Y-%m-%d")
    return f"--since={since}", f"last {fallback_days} days"


def identifiers_in(text: str, prefixes) -> list:
    allow = {p.upper() for p in prefixes}
    out = []
    for prefix, number in IDENTIFIER_RE.findall(text or ""):
        if allow:
            if prefix not in allow:
                continue
        elif prefix in NOT_AN_ISSUE:
            continue
        ident = f"{prefix}-{number}"
        if ident not in out:
            out.append(ident)
    return out


def collect_commits(root: str, rng: str, prefixes, trivial_patterns) -> list:
    """One git call. Body included so `Closes AGT-45` in a PR body still counts."""
    fmt = FLD.join(["%H", "%an", "%aI", "%P", "%s", "%b"]) + REC
    raw = git("log", rng, f"--pretty=format:{fmt}", cwd=root)
    trivial_res = [re.compile(p, re.I) for p in trivial_patterns]
    commits = []
    for block in raw.split(REC):
        block = block.strip("\n")
        if not block.strip():
            continue
        parts = block.split(FLD)
        if len(parts) < 5:
            continue
        sha, author, date, parents, subject = parts[:5]
        body = parts[5] if len(parts) > 5 else ""
        idents = identifiers_in(f"{subject}\n{body}", prefixes)
        if idents:
            kind = "ticketed"
        elif any(rx.search(subject) for rx in trivial_res):
            kind = "trivial"
        else:
            kind = "unticketed"
        commits.append({
            "sha": sha[:12],
            "author": author,
            "date": date,
            "subject": subject,
            "isMerge": len(parents.split()) > 1,
            "kind": kind,
            "identifiers": idents,
        })
    commits.sort(key=lambda c: c["date"])
    return commits


def changed_paths(root: str, rng: str) -> list:
    raw = git("log", rng, "--name-only", "--pretty=format:", cwd=root)
    seen = []
    for line in raw.splitlines():
        line = line.strip()
        if line and line not in seen:
            seen.append(line)
    return seen


def match_projects(paths, projects) -> dict:
    hits = {}
    for project in projects:
        name = project.get("name")
        if not name:
            continue
        patterns = project.get("paths") or ["**"]
        matched = [
            p for p in paths
            if any(fnmatch.fnmatch(p, pat) or p.startswith(pat.rstrip("*")) for pat in patterns)
        ]
        if matched:
            hits[name] = matched
    return hits


def build_brief(root: str, force: bool, verbose: bool) -> dict:
    config = load_json(os.path.join(root, CONFIG_NAME))
    state = load_json(os.path.join(root, STATE_NAME))

    cadence = dict(DEFAULT_CADENCE)
    for key, value in (config.get("cadence") or {}).items():
        cadence[CADENCE_ALIASES.get(key, key)] = value

    projects = config.get("projects") or []
    prefixes = config.get("issuePrefixes") or []
    trivial_patterns = config.get("ignoreCommitPatterns") or DEFAULT_TRIVIAL

    last_sha = state.get("lastSyncedSha")
    last_at = parse_ts(state.get("lastSyncedAt"))
    last_review = parse_ts(state.get("lastRoadmapReviewAt")) or last_at

    rng, label = commit_range(root, last_sha, int(cadence["firstRunLookbackDays"]))
    commits = collect_commits(root, rng, prefixes, trivial_patterns)

    unticketed = [c for c in commits if c["kind"] == "unticketed"]
    ticketed = [c for c in commits if c["kind"] == "ticketed"]
    trivial = [c for c in commits if c["kind"] == "trivial"]
    unticketed_merges = [c for c in unticketed if c["isMerge"]]

    days_since = round((now() - last_at).total_seconds() / 86400, 2) if last_at else None
    days_since_review = (
        round((now() - last_review).total_seconds() / 86400, 2) if last_review else None
    )

    # Repair mode: only unticketed work justifies it; cadence decides when to batch.
    repair_reasons = []
    if unticketed:
        if last_at is None:
            repair_reasons.append("no previous sync recorded")
        elif days_since is not None and days_since >= cadence["everyDays"]:
            repair_reasons.append(
                f"{days_since}d since last sync >= everyDays {cadence['everyDays']}"
            )
        if len(unticketed_merges) >= cadence["everyUnticketedMerges"]:
            repair_reasons.append(
                f"{len(unticketed_merges)} unticketed merges >= "
                f"everyUnticketedMerges {cadence['everyUnticketedMerges']}"
            )
        if len(unticketed) >= cadence["everyUnticketedCommits"]:
            repair_reasons.append(
                f"{len(unticketed)} unticketed commits >= "
                f"everyUnticketedCommits {cadence['everyUnticketedCommits']}"
            )

    review_due = (
        cadence["roadmapReviewDays"] > 0
        and (days_since_review is None or days_since_review >= cadence["roadmapReviewDays"])
        and bool(commits)
    )

    if force:
        mode, reasons = "repair", ["forced"]
    elif repair_reasons:
        mode, reasons = "repair", repair_reasons
    elif review_due:
        mode = "roadmap-review"
        elapsed = f"{days_since_review}d" if days_since_review is not None else "never reviewed"
        reasons = [
            f"{elapsed} since last roadmap review "
            f">= roadmapReviewDays {cadence['roadmapReviewDays']}"
        ]
    else:
        mode = None
        reasons = []
        if not commits:
            reasons.append("no new commits since last sync")
            if cadence["roadmapReviewDays"] > 0 and (
                days_since_review is None
                or days_since_review >= cadence["roadmapReviewDays"]
            ):
                reasons.append("a roadmap review is owed but there is nothing new to review")
        elif not unticketed:
            one = len(ticketed) == 1
            plural, verb = ("", "carries") if one else ("s", "carry")
            reasons.append(
                f"all {len(ticketed)} substantive commit{plural} {verb} an issue identifier "
                f"({len(trivial)} trivial) — the work loop kept Linear in sync"
            )
        else:
            plural = "" if len(unticketed) == 1 else "s"
            reasons.append(
                f"{len(unticketed)} unticketed commit{plural}, "
                "under cadence thresholds — batching"
            )

    paths = changed_paths(root, rng) if (mode or verbose) else []

    brief = {
        "due": mode is not None,
        "mode": mode,
        "reasons": reasons,
        "config": {
            "present": bool(config),
            "team": config.get("team"),
            "projects": [p.get("name") for p in projects],
            "cadence": cadence,
            "autonomy": config.get("autonomy") or {},
            "workLoop": config.get("workLoop") or {},
        },
        "lastSync": {
            "sha": (last_sha or "")[:12] or None,
            "at": state.get("lastSyncedAt"),
            "daysSince": days_since,
            "note": state.get("lastSyncNote"),
        },
        "delta": {
            "range": label,
            "ticketed": len(ticketed),
            "trivial": len(trivial),
            "unticketed": len(unticketed),
            "unticketedMerges": len(unticketed_merges),
            "changedPathCount": len(paths),
        },
        # The only commits a repair pass should look at.
        "unticketedCommits": [
            {"sha": c["sha"], "subject": c["subject"], "author": c["author"], "date": c["date"][:10]}
            for c in unticketed[:25]
        ],
        "issueIdentifiersReferenced": sorted({i for c in ticketed for i in c["identifiers"]}),
        "projectsTouched": {k: len(v) for k, v in match_projects(paths, projects).items()},
    }

    if verbose:
        brief["commits"] = commits
        brief["changedPaths"] = paths
        brief["projectsTouchedPaths"] = match_projects(paths, projects)
    return brief


def record(root: str, note, mode) -> dict:
    head = git("rev-parse", "HEAD", cwd=root)
    if not head:
        fail("cannot resolve HEAD")
    path = os.path.join(root, STATE_NAME)
    state = load_json(path)
    history = state.get("history") or []
    if state.get("lastSyncedAt"):
        history.insert(0, {
            "sha": (state.get("lastSyncedSha") or "")[:12],
            "at": state.get("lastSyncedAt"),
            "note": state.get("lastSyncNote"),
        })
    stamp = now().replace(microsecond=0).isoformat().replace("+00:00", "Z")
    new_state = {
        "lastSyncedSha": head,
        "lastSyncedAt": stamp,
        "lastSyncNote": note or "",
        "lastRoadmapReviewAt": (
            stamp if mode in (None, "roadmap-review")
            else state.get("lastRoadmapReviewAt") or stamp
        ),
        "history": history[:20],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(new_state, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return new_state


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--check", action="store_true", help="exit 0 if due, 10 if not")
    parser.add_argument("--force", action="store_true", help="report due regardless of cadence")
    parser.add_argument("--verbose", action="store_true", help="include every commit and path")
    parser.add_argument("--record", action="store_true", help="write sync state at HEAD")
    parser.add_argument("--note", default=None, help="one-line summary stored with the state")
    parser.add_argument("--mode", default=None, choices=["repair", "roadmap-review"],
                        help="with --record: which pass just completed")
    args = parser.parse_args()

    root = repo_root()

    if args.record:
        print(json.dumps(record(root, args.note, args.mode), indent=2, ensure_ascii=False))
        return 0

    brief = build_brief(root, args.force, args.verbose)
    if args.check:
        print(json.dumps(
            {"due": brief["due"], "mode": brief["mode"], "reasons": brief["reasons"]},
            ensure_ascii=False,
        ))
        return 0 if brief["due"] else 10

    print(json.dumps(brief, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
