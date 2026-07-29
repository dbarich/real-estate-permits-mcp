# Commit Proposal — v0.2.3-alpha: fix search_permits_by_zip field name

**Date:** 2026-07-27
**Proposed by:** Cowork session (agent proposes; human ratifies)
**Status:** READY TO RATIFY
**Release:** v0.2.3-alpha (one-line bug fix)

## Why
During a full-suite end-to-end demo run (all 8 tools, prep for the Vontive CTO
call), `search_permits_by_zip("98144")` returned HTTP 400 on every call. Root
cause: the SoQL WHERE clause queried field `zip`, but Seattle dataset
`76t5-zqzr`'s actual field is `originalzip` — verified against a live record
(`"originaladdress1": ..., "originalzip":"98125"`). The tool has likely never
worked; nothing else queries that field.

## Proposed commit message
```
v0.2.3-alpha: fix search_permits_by_zip — dataset field is originalzip, not zip
```

## Files changed — what and why
| File | Change | Rationale |
|------|--------|-----------|
| `src/seattle_permits_server.py` | WHERE clause `zip like` → `originalzip like`; `__version__` → 0.2.3-alpha | The fix + version sync |
| `pyproject.toml` | version → 0.2.3-alpha | Version sync |
| `CHANGELOG.md` | New `[0.2.3-alpha]` entry; also moved the docs-correction entry from `[Unreleased]` into `[0.2.2-alpha]` where it actually shipped | Accuracy: the docs fix went out in the v0.2.2 commit |

## Alternatives considered
- **Verify fix before committing** vs. ratify now: the running MCP server loads
  code at Claude Desktop startup, so the fix can't be exercised until a restart.
  Recommended: ratify, restart Desktop, then run
  `search_permits_by_zip("98144")` once as the post-ship check. If it still
  fails, it's a revert-able one-liner.
- **Add a regression test**: the integration suite hits live APIs; a zip-search
  probe would be a good addition but touches test scope beyond a hotfix. Noted
  for the next test pass instead.

## Not included (deliberate)
- No other tool touches; no docs changes beyond CHANGELOG.

## Ratify steps (host terminal)
```bash
cd ~/MCP/Real-Estate-Permits-MCP
./precommit-unlock.sh
git add src/seattle_permits_server.py pyproject.toml CHANGELOG.md \
        commit-proposals/2026-07-27-fix-zip-field-0.2.3.md
git commit -m "v0.2.3-alpha: fix search_permits_by_zip — dataset field is originalzip, not zip"
git tag v0.2.3-alpha
git push origin main --tags
```
Post-ship check: restart Claude Desktop, then ask Claude to
"find permits in ZIP 98144 from the last 6 months" — expect results, not HTTP 400.
