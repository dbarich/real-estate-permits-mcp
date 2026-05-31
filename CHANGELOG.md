# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
While in alpha (`0.x`), the public tool surface (tool names and parameters) may
change between minor versions without deprecation.

## [Unreleased]

- Phase 1 gate pending: both testers install, configure, and run 3 use cases
  without author assistance.

## [0.2.1-alpha] — 2026-05-31

Version-control hygiene. No behavior changes to the server or tools.

### Added
- This CHANGELOG (Keep a Changelog / semver), backfilled across all releases.
- `__version__` in `src/seattle_permits_server.py`, kept in sync with `pyproject.toml`.
- `precommit-unlock.sh` — clears stale git lock files that accumulate when the
  `.git` directory is accessed through the Cowork/sandbox mount.

### Changed
- Bumped `pyproject.toml` version to match the release tag (was stuck at `0.1.0-alpha`).
- Refreshed ROADMAP.md to reflect completed v0.2.0-alpha hardening.
- Added `skills/surgical-build/` to `.gitignore` (kept local, not published).

## [0.2.0-alpha] — 2026-05-28

Hardening release. All eight tools made reliable and testable enough to hand
to an external tester.

### Added
- Input validation on all 8 tools: ZIP (5-digit), PIN (10-digit), and permit-number
  regex; minimum street-name length; bounds clamping on `days_back` and `limit`.
- SoQL sanitization helper `_sanitize_soql()` that escapes single quotes in all
  user input before it is interpolated into a WHERE clause.
- Optional Socrata app token support via the `SOCRATA_APP_TOKEN` environment
  variable to avoid rate limiting on Seattle's Open Data API.
- Quick-start onboarding: `setup.sh` auto-installer and `QUICKSTART.md` with
  evaluation questions for testers.
- Integration test (`tests/integration_test.py`) covering 2 properties plus
  validation probes; full suite now 14/14 passing.

### Changed
- All 8 tools now return three-tier error differentiation — no-results vs.
  API error vs. timeout — with actionable user-facing messages.

### Fixed
- `get_parcel_by_pin` crashed with a `NoneType` error on null King County API
  fields (surfaced on PIN 1364300565); fixed with the `(value or 'N/A')` pattern.

## [0.1.1-alpha] — 2026-05-24

### Fixed
- Rewrote King County parcel address lookup: ArcGIS Layer 2 (Parcels) as the
  primary source with Layer 3 (Sales) as fallback.

### Added
- Address normalization (`_normalize_address()`) and format permutations
  (`_address_variants()`) to match King County's address formatting.
- Debug logging via the `SEATTLE_PERMITS_DEBUG=1` environment variable.

## [0.1.0-alpha] — 2026-05-24

Initial public alpha.

### Added
- MCP server (`src/seattle_permits_server.py`) exposing 8 tools over Seattle's
  Socrata building-permits API and King County's ArcGIS parcel/sales data.
- Standalone bulk query script (`src/seattle_opendata_query.py`) with CSV export.
- Smoke tests (`tests/test_parcel_lookup.py`).
- Public GitHub repository under the MIT license, with README, CONTRIBUTING,
  and full PM documentation (`docs/00-07/`).

[Unreleased]: https://github.com/dbarich/real-estate-permits-mcp/compare/v0.2.1-alpha...HEAD
[0.2.1-alpha]: https://github.com/dbarich/real-estate-permits-mcp/compare/v0.2.0-alpha...v0.2.1-alpha
[0.2.0-alpha]: https://github.com/dbarich/real-estate-permits-mcp/compare/v0.1.1-alpha...v0.2.0-alpha
[0.1.1-alpha]: https://github.com/dbarich/real-estate-permits-mcp/compare/v0.1.0-alpha...v0.1.1-alpha
[0.1.0-alpha]: https://github.com/dbarich/real-estate-permits-mcp/releases/tag/v0.1.0-alpha
