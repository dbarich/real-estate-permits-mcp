# Commit Proposal — Rate-limit (429) handling + token onboarding fix

**Date:** 2026-06-02
**Proposed by:** Cowork session (agent proposes; human ratifies)
**Status:** READY TO RATIFY (soft-warn approach confirmed; edits applied in working tree; commit/push from host terminal)
**Release:** v0.2.2-alpha (bug/UX fix; one behavior change — new 429 error branch)

## Why
First external tester (engineer, installed cross-platform Mac→PC) ran the
`dearborn-market-pull` skill without setting `SOCRATA_APP_TOKEN` and got a
"query error." Diagnosis: the skill fires 15+ Socrata queries in quick
succession; anonymous (no-token) requests share Seattle's throttled pool and
the burst trips **HTTP 429 (Too Many Requests)**. Single-tool queries stayed
under the anonymous ceiling and worked — only the high-volume skill failed.

Two compounding gaps:
1. The token is documented as "optional," but the flagship skills effectively
   require it. Onboarding never tells the user that.
2. The error handler lumps 429 in with all HTTP errors and blames "the Seattle
   data portal" (server lines 152–156), so the tester had no way to connect the
   failure back to the token he skipped.

The tester also asked for "a couple user-flow guides/examples."

## Proposed commit message
```
v0.2.2-alpha: handle Socrata 429 with actionable token guidance; mark token prerequisite for skills
```

## Recommended approach
**Graceful degradation + actionable 429, not a hard token gate.** Tools keep
working tokenless for low-volume use (the curious-first-query path that worked
for the tester). The fixes target the two real gaps: make a 429 say exactly
what to do, and make onboarding flag the token as a prerequisite *before* a
user runs a multi-query skill. The skill itself adds a soft pre-check that warns
(does not refuse) if no token is set.

## Files changed — what and why
| File | Change | Rationale |
|------|--------|-----------|
| `src/seattle_permits_server.py` | Add a dedicated 429 branch to Socrata error handling (centralize in/around `query_socrata` so all 8 tools inherit it, rather than editing 8 duplicated `except` blocks) | A 429 is user-fixable; the message must name the cause ("you're being rate-limited") and the fix ("set `SOCRATA_APP_TOKEN`, free — <link>"), distinct from a real portal outage |
| `QUICKSTART.md` | Promote the token from "optional" to a prerequisite step *before* running any skill; add the ~2-min signup link inline | Closes the "optional but actually required" gap that bit the tester |
| `README.md` | One-line note near the token section: tools work tokenless; skills need a token to avoid throttling | Sets expectations at the top of the funnel |
| `skills/dearborn-market-pull/SKILL.md` | Add a soft pre-flight check: if `SOCRATA_APP_TOKEN` is unset, warn and recommend setting it before the 15+ query run | Fail-soft at the exact point the burst happens, without blocking experimentation |
| `pyproject.toml`, `src/...__version__`, `CHANGELOG.md` | Bump to v0.2.2-alpha + changelog entry | Keep the three version sources in sync per CLAUDE.md |

## Alternatives considered
- **Hard token gate (skill refuses to run without a token)** vs. graceful
  degradation. Rejected hard gate as the default: it adds friction for a curious
  first-time user and forces every current/future skill to implement a check.
  Soft warning at the skill level plus a clear 429 message gets the same
  protection without blocking exploration. (If Devin prefers fail-fast, this is
  the one-line flip — flagged as the open decision below.)
- **Edit the `except httpx.HTTPStatusError` block in all 8 tools individually**
  vs. centralize 429 handling in `query_socrata` / a shared formatter. Chose
  centralize: 8 near-identical edits is error-prone and drifts; one shared path
  is the cleaner change and the smaller diff. (If centralizing turns out to
  reshape how every tool returns errors, that is architectural — promote to an
  ADR per CLAUDE.md before landing.)
- **Auto-retry with backoff on 429** vs. just reporting it. Deferred: backoff
  adds latency and complexity, and the right fix for a 15-query skill is a token,
  not slow retries. Revisit only if tokenless use is a real requirement.
- **Write the full user-flow guides now** vs. defer until after the live call.
  Deferred (see below): the upcoming tester call will reshape what the guides
  should cover, so writing them now risks rework.

## Not included (deliberate)
- **Full user-flow guides/examples** — deferred until after the live tester
  call, which should surface the real points of confusion to document. Shipping
  the unambiguous token + 429 fixes now; letting the call inform the guides.
- No change to King County / ArcGIS error paths (unaffected by Socrata throttling).

## Decision (resolved)
Soft warn (graceful), confirmed by Devin 2026-06-02. The skill warns when no
token is set but does not refuse to run; the new 429 error path backs it up with
actionable guidance if a tokenless run does get throttled.

## Verification done
- `python3 -m py_compile` passes.
- All 7 `HTTPStatusError` blocks now delegate to `_http_error()`.
- Unit-checked `_http_error()`: Seattle 429 includes the token fix + signup link;
  King County 429 omits the token (a Socrata token wouldn't help GIS); non-429
  stays a generic outage message.

## Ratify steps (host terminal)
```bash
cd ~/Real-Estate-Permits-MCP
./precommit-unlock.sh
git add src/seattle_permits_server.py QUICKSTART.md README.md \
        skills/dearborn-market-pull/SKILL.md pyproject.toml CHANGELOG.md \
        commit-proposals/2026-06-02-token-429-onboarding.md
git commit -m "v0.2.2-alpha: handle Socrata 429 with actionable token guidance; mark token prerequisite for skills"
git tag v0.2.2-alpha
git push origin main --tags
```
