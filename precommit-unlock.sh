#!/usr/bin/env bash
#
# precommit-unlock.sh
#
# Clears stale git lock files that accumulate when this repo's .git directory
# is accessed through the Cowork/sandbox mount. The sandbox can stage files but
# does not reliably release locks, and the resulting stale locks cannot be
# deleted from inside the sandbox ("Operation not permitted"). They block every
# subsequent commit with errors like:
#
#     fatal: Unable to create '.git/index.lock': File exists.
#
# Run this from the host terminal (where you have permission to delete them)
# before `git add` / `git commit`. It is a no-op if no locks are present.
#
set -euo pipefail
cd "$(dirname "$0")"

locks=(.git/index.lock .git/HEAD.lock .git/refs/heads/main.lock)
removed=0
for lock in "${locks[@]}"; do
    if [[ -e "$lock" ]]; then
        rm -f "$lock" && echo "removed $lock" && removed=1
    fi
done

if [[ "$removed" -eq 0 ]]; then
    echo "No stale git locks found. Safe to commit."
else
    echo "Cleared stale git locks. Safe to commit."
fi
