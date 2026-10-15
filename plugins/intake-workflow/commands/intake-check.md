---
description: Report the SHARED-INTAKE block version and project lines in one or more repos.
argument-hint: "<repo dir> [<repo dir> ...] [--expect-project NAME]"
---

Check which repos carry the intake rules and whether they are current. Arguments: $ARGUMENTS

1. No directories given → use the current directory.
2. Run `python3 "$SKILL_DIR/scripts/intake_block.py" check <dirs>` and print its output unchanged.
3. For every line that is not `ok`, say in one sentence what to run to fix it (`/adopt-intake` for missing or outdated blocks; a rename needs the steps in the skill's Recipe 4).
4. Do not edit any file.
