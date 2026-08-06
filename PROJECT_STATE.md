# PROJECT_STATE — Real Estate Permits MCP
Updated: 2026-07-27 (evening) · By: Cowork session

## Shipped
- v0.2.3-alpha (pushed, tagged): fixed search_permits_by_zip — queried field
  `zip` but dataset field is `originalzip`; tool had never worked. Found during
  the full-suite end-to-end demo run; verified post-restart (100 results in 98144,
  incl. NEW find: $507K permit at 2439 S Judkins, Jun 2026 — neighborhood evidence)
- Industry-CTO meeting prep complete (call-prep doc + end-to-end demo artifacts,
  kept locally in ~/Job Hunt)
- v0.2.2-alpha (pushed, tagged): Socrata 429 rate-limit handling with actionable
  token guidance; token reframed as prerequisite for skills; bank-validation
  overclaim corrected in README (proactive-disclosure note in commit body)
- v0.2.1-alpha: CHANGELOG, version sync (pyproject + __version__), precommit-unlock.sh
- Repo relocated to ~/MCP/Real-Estate-Permits-MCP; Claude Desktop config repointed;
  server verified live from new path (both APIs answering)
- Bookstorhaus workspace (229 MB incl. sensitive loan docs) migrated OUT of repo
  tree → ~/Bookstorhaus (checksum-verified); dearborn-market-pull skill repointed
- mcp-workspace consolidation: stale server copy retired, marketplace parked as
  dormant Fork B (see ~/MCP/Realestate-Marketplace/FORK-B-STATE.md)

## In flight
| Item | Status | Blocked on |
|------|--------|-----------|
| Phase 1 gate (both testers run 3 use cases solo) | Engineer tester DONE-ish: installed on PC, tools worked, hit token wall (fixed in v0.2.2) | Live call to schedule; second tester still unscheduled |
| User-flow guides / worked examples | Deliberately deferred | Insights from live tester call |
| mcp-workspace rename commit | Folder renamed to Realestate-Marketplace outside git; deletions + untracked dir pending | Devin ratify: `cd ~/MCP && git add -A && git commit -m "Rename Realestate Analysis Server -> Realestate-Marketplace"` |

## Next
1. Commit this PROJECT_STATE.md + the mcp-workspace rename (commands above/below)
2. Schedule the live tester call (engineer); prep doc offered via call-prep skill
3. Send/schedule second-tester onboarding (package ready since May)
4. Small config tidy: add ~/MCP/Real-Estate-Permits-MCP to localAgentModeTrustedFolders;
   remove dead entries (old repo path, ~/dearborn-mcp); check SOCRATA_APP_TOKEN is
   actually set in the server's env block (config had none as of 2026-07-27)
5. Stale README claim: "No input validation" under What Doesn't Work Yet (shipped
   v0.2.0) — fix in next docs pass

## Open decisions
- Fork A validation read: engineer = positive signal ("pretty cool", cross-platform
  install worked); formal gate still open pending call + second tester
- Fork B (marketplace): parked dormant by explicit decision 2026-07-27; revisit
  only after Fork A resolves (state captured in FORK-B-STATE.md)
- FIDIC iCloud straggler: trusted folder still points at Mobile Documents copy while
  local ~/MCP/Infrastructure Analysis exists — resolve which is live when FIDIC resumes

## Standing context
- Solo dev (Devin), macOS, python3 always. Repo public: github.com/dbarich/real-estate-permits-mcp (MIT)
- Workflow: propose-then-ratify — Claude edits + writes commit-proposals/; Devin
  commits from host terminal (./precommit-unlock.sh first). Never commit from sandbox.
- Version sync triple: pyproject.toml + __version__ + CHANGELOG top entry
- Bookstorhaus files live in ~/Bookstorhaus ONLY (sensitive; never in repo tree)
- Tester relationships: engineer colleague (PC install done), plus a data scientist
  at a major real-estate platform. June 9 scheduled reminder existed for follow-up cadence.
