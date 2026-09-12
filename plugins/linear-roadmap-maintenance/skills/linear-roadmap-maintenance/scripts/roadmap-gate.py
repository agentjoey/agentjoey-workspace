#!/usr/bin/env python3
"""Decide whether a Linear roadmap sync is due, and emit the git-side evidence.

The script is the deterministic half of the sync: it reads the repo's config and
sync state, measures the work delta since the last sync, and prints a "sync
brief" as JSON. All judgement (what to create, close, re-forecast) belongs to the
agent reading that brief, not here.

Usage:
  roadmap-gate.py                 # print the sync brief as JSON
  roadmap-gate.py --check         # exit 0 = sync due, 10 = not due, 1 = error
  roadmap-gate.py --force         # brief with due=true regardless of cadence
  roadmap-gate.py --record        # write state after a successful sync (HEAD, now)
  roadmap-gate.py --record --note "closed 3, created 2"

Config:  .linear-roadmap.json        (committed, hand-written)
State:   .linear-roadmap.state.json  (committed, written by --record)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

CONFIG_NAME = ".linear-roadmap.json"
STATE_NAME = ".linear-roadmap.state.json"

DEFAULT_CADENCE = {"everyDays": 7, "everyMergedPRs": 5, "everyCommits": 25}

# Tokens that look like a Linear identifier but never are.
NOT_AN_ISSUE = {
    "UTF", "SHA", "ISO", "RFC", "IPV", "HTTP", "HTTPS", "TLS", "AES", "RSA",
    "MD", "CVE", "ES", "PEP", "GPT", "LTS", "X", "NODE", "PY",
}
IDENTIFIER_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,9})-(\d{1,6})\b")


def fail(msg: str) -> "None":
    print(f"roadmap-gate: {msg}", file=sys.stderr)
    sys.exit(1)


def git(*args: str, cwd: str) -> str:
    res = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    if res.returncode != 0:
        return ""
    return res.stdout.strip()


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


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def commit_exists(root: str, sha: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=root, capture_output=True, check=False,
    ).returncode == 0


def commit_range(root: str, last_sha: str | None, fallback_days: int) -> tuple[str, str]:
    """Return (range_expr, human_label). Falls back to a time window on first run."""
    head = git("rev-parse", "HEAD", cwd=root)
    if last_sha and commit_exists(root, last_sha):
        return f"{last_sha}..HEAD", f"{last_sha[:8]}..{head[:8]}"
    since = (now() - timedelta(days=fallback_days)).strftime("%Y-%m-%d")
    return f"--since={since}", f"last {fallback_days} days"


def collect_commits(root: str, rng: str) -> list[dict]:
    sep = "\x1f"
    fmt = sep.join(["%H", "%an", "%aI", "%s", "%P"])
    raw = git("log", rng, f"--pretty=format:{fmt}", "--no-merges", cwd=root)
    merges = git("log", rng, f"--pretty=format:{fmt}", "--merges", cwd=root)
    out: list[dict] = []
    for block, is_merge in ((raw, False), (merges, True)):
        for line in block.splitlines():
            if not line.strip():
                continue
            parts = line.split(sep)
            if len(parts) < 5:
                continue
            out.append({
                "sha": parts[0][:12],
                "author": parts[1],
                "date": parts[2],
                "subject": parts[3],
                "isMerge": is_merge,
            })
    out.sort(key=lambda c: c["date"])
    return out


def changed_paths(root: str, rng: str) -> list[str]:
    raw = git("log", rng, "--name-only", "--pretty=format:", cwd=root)
    seen: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if line and line not in seen:
            seen.append(line)
    return seen


def match_projects(paths: list[str], projects: list[dict]) -> dict[str, list[str]]:
    """Map configured project -> the changed paths that belong to it."""
    import fnmatch

    hits: dict[str, list[str]] = {}
    for project in projects:
        name = project.get("name")
        patterns = project.get("paths") or ["**"]
        if not name:
            continue
        matched = [
            p for p in paths
            if any(fnmatch.fnmatch(p, pat) or p.startswith(pat.rstrip("*")) for pat in patterns)
        ]
        if matched:
            hits[name] = matched
    return hits


def find_identifiers(texts: list[str], prefixes: list[str]) -> list[str]:
    found: list[str] = []
    allow = {p.upper() for p in prefixes}
    for text in texts:
        for prefix, number in IDENTIFIER_RE.findall(text or ""):
            if allow:
                if prefix not in allow:
                    continue
            elif prefix in NOT_AN_ISSUE:
                continue
            ident = f"{prefix}-{number}"
            if ident not in found:
                found.append(ident)
    return found


def build_brief(root: str, force: bool) -> dict:
    config = load_json(os.path.join(root, CONFIG_NAME))
    state = load_json(os.path.join(root, STATE_NAME))

    cadence = {**DEFAULT_CADENCE, **(config.get("cadence") or {})}
    projects = config.get("projects") or []
    prefixes = config.get("issuePrefixes") or []

    last_sha = state.get("lastSyncedSha")
    last_at = parse_ts(state.get("lastSyncedAt"))
    rng, label = commit_range(root, last_sha, int(cadence.get("firstRunLookbackDays", 30)))

    commits = collect_commits(root, rng)
    non_merge = [c for c in commits if not c["isMerge"]]
    merged = [c for c in commits if c["isMerge"]]
    paths = changed_paths(root, rng)

    days_since = None
    if last_at:
        days_since = round((now() - last_at).total_seconds() / 86400, 2)

    reasons: list[str] = []
    if force:
        reasons.append("forced")
    if last_at is None:
        reasons.append("no previous sync recorded")
    elif days_since is not None and days_since >= cadence["everyDays"]:
        reasons.append(f"{days_since}d since last sync >= everyDays {cadence['everyDays']}")
    if len(merged) >= cadence["everyMergedPRs"]:
        reasons.append(f"{len(merged)} merges >= everyMergedPRs {cadence['everyMergedPRs']}")
    if len(non_merge) >= cadence["everyCommits"]:
        reasons.append(f"{len(non_merge)} commits >= everyCommits {cadence['everyCommits']}")

    has_work = bool(commits)
    due = bool(reasons) and (has_work or force)
    if reasons and not has_work and not force:
        reasons.append("but no new commits — nothing to reconcile")

    return {
        "due": due,
        "reasons": reasons,
        "config": {
            "present": bool(config),
            "team": config.get("team"),
            "cadence": cadence,
            "autonomy": config.get("autonomy") or {},
            "projects": [p.get("name") for p in projects],
        },
        "lastSync": {
            "sha": last_sha,
            "at": state.get("lastSyncedAt"),
            "daysSince": days_since,
            "note": state.get("lastSyncNote"),
        },
        "delta": {
            "range": label,
            "commits": len(non_merge),
            "merges": len(merged),
            "authors": sorted({c["author"] for c in commits}),
            "changedPaths": paths[:200],
            "changedPathCount": len(paths),
        },
        "projectsTouched": match_projects(paths, projects),
        "issueIdentifiersReferenced": find_identifiers(
            [c["subject"] for c in commits], prefixes
        ),
        "commits": commits[:100],
    }


def record(root: str, note: str | None) -> dict:
    head = git("rev-parse", "HEAD", cwd=root)
    if not head:
        fail("cannot resolve HEAD")
    path = os.path.join(root, STATE_NAME)
    state = load_json(path)
    history = state.get("history") or []
    if state.get("lastSyncedAt"):
        history.insert(0, {
            "sha": state.get("lastSyncedSha"),
            "at": state.get("lastSyncedAt"),
            "note": state.get("lastSyncNote"),
        })
    new_state = {
        "lastSyncedSha": head,
        "lastSyncedAt": now().replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "lastSyncNote": note or "",
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
    parser.add_argument("--record", action="store_true", help="write sync state at HEAD")
    parser.add_argument("--note", default=None, help="one-line summary stored with the state")
    args = parser.parse_args()

    root = repo_root()

    if args.record:
        print(json.dumps(record(root, args.note), indent=2, ensure_ascii=False))
        return 0

    brief = build_brief(root, args.force)
    if args.check:
        print(json.dumps({"due": brief["due"], "reasons": brief["reasons"]}, ensure_ascii=False))
        return 0 if brief["due"] else 10

    print(json.dumps(brief, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
