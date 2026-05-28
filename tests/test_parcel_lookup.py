"""
Smoke test for the King County parcel lookup functions.

Exercises the three functions touched by the parcel-lookup bug fix against
known Judkins Park / Dearborn corridor addresses. Not a pytest — just a
runnable script that prints results so a human can eyeball them. Run with:

    SEATTLE_PERMITS_DEBUG=1 python tests/test_parcel_lookup.py

Exit code is 0 when every probe returns something other than an error / empty
result; 1 otherwise.
"""

import asyncio
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import seattle_permits_server as s  # noqa: E402


TARGET_ADDRESSES = [
    "2412 S Dearborn St",
    "2510 S Dearborn St",
    "1902 S Dearborn St",
]
TARGET_PIN = "6362900036"  # 2412 S Dearborn St — the user's own lot


def _looks_like_failure(text: str) -> bool:
    head = text.strip().splitlines()[0].lower() if text.strip() else ""
    return head.startswith(("error", "no parcel", "no nearby", "http error"))


async def _probe(label, coro):
    print(f"\n========== {label} ==========")
    try:
        out = await coro
    except Exception as e:
        print(f"!! EXCEPTION: {type(e).__name__}: {e}")
        return False
    print(out)
    return not _looks_like_failure(out)


async def main():
    failures = []

    # 1. PIN lookup — confirms the API itself works (sanity check).
    ok = await _probe(
        f"get_parcel_by_pin({TARGET_PIN!r})",
        s.get_parcel_by_pin(TARGET_PIN),
    )
    if not ok:
        failures.append("get_parcel_by_pin")

    # 2. Address lookup — the previously broken path.
    for addr in TARGET_ADDRESSES:
        ok = await _probe(
            f"get_parcel_by_address({addr!r})",
            s.get_parcel_by_address(addr),
        )
        if not ok:
            failures.append(f"get_parcel_by_address({addr})")

    # 3. Nearby parcels — the previously broken street-name extraction.
    ok = await _probe(
        f"get_nearby_parcels({TARGET_ADDRESSES[0]!r})",
        s.get_nearby_parcels(TARGET_ADDRESSES[0]),
    )
    if not ok:
        failures.append("get_nearby_parcels")

    # 4. Combined comparables — exercises both fixed paths plus permit search.
    ok = await _probe(
        f"get_development_comparables({TARGET_ADDRESSES[0]!r}, days_back=730)",
        s.get_development_comparables(TARGET_ADDRESSES[0], days_back=730),
    )
    if not ok:
        failures.append("get_development_comparables")

    # 5. Input validation — should return a helpful error, not silently fail.
    for bad in ["", "   ", "x", "Dearborn"]:
        print(f"\n========== validation: get_parcel_by_address({bad!r}) ==========")
        out = await s.get_parcel_by_address(bad)
        print(out)
        if not out.startswith("Error"):
            failures.append(f"validation should-be-error: {bad!r}")

    # 6. No-results path — error-type differentiation should produce a clear
    # "No ... found" message (not a generic error / not a timeout / not an HTTP
    # error) for queries that succeed but match nothing.
    no_results_checks = [
        (
            "search_permits('XYZNONEXISTENT123')",
            s.search_permits("XYZNONEXISTENT123", days_back=30),
            "no permits found",
        ),
        (
            "get_parcel_by_address('99999 ZZZZZ ST')",
            s.get_parcel_by_address("99999 ZZZZZ ST"),
            "no parcel found",
        ),
        (
            "get_nearby_parcels('99999 ZZZZZ ST')",
            s.get_nearby_parcels("99999 ZZZZZ ST"),
            "no parcels found",
        ),
        (
            "get_permit_details('XYZ-NONEXISTENT-999')",
            s.get_permit_details("XYZ-NONEXISTENT-999"),
            "no permit found",
        ),
    ]
    for label, coro, expected_prefix in no_results_checks:
        print(f"\n========== no-results: {label} ==========")
        out = await coro
        print(out)
        head = out.strip().lower()
        if not head.startswith(expected_prefix):
            failures.append(f"no-results expected '{expected_prefix}' prefix: {label}")
        elif "timed out" in head or "api error" in head or head.startswith("unexpected"):
            failures.append(f"no-results returned wrong error type: {label}")

    # 7. Input validation — every tool with user-controlled strings should
    # reject bad input with a clear "Error: ..." message before any API call.
    validation_cases = [
        ("search_permits empty", s.search_permits("", 365)),
        ("search_permits too short", s.search_permits("X", 365)),
        ("search_permits_by_zip non-numeric", s.search_permits_by_zip("abc")),
        ("search_permits_by_zip 4-digit", s.search_permits_by_zip("1234")),
        ("search_permits_by_zip 6-digit", s.search_permits_by_zip("123456")),
        ("get_permit_details empty", s.get_permit_details("")),
        ("get_permit_details injection", s.get_permit_details("'; DROP TABLE --")),
        ("get_parcel_by_pin empty", s.get_parcel_by_pin("")),
        ("get_parcel_by_pin non-numeric", s.get_parcel_by_pin("abc")),
        ("get_parcel_by_pin short", s.get_parcel_by_pin("123")),
    ]
    for label, coro in validation_cases:
        print(f"\n========== validation: {label} ==========")
        out = await coro
        print(out)
        if not out.startswith("Error"):
            failures.append(f"validation should-be-error: {label}")

    # 8. SoQL sanitization — apostrophe in input must not break the query or
    # surface a syntax error. Should be a no-results or successful response.
    print("\n========== sanitization: search_permits(\"O'BRIEN\") ==========")
    out = await s.search_permits("O'BRIEN", 365)
    print(out)
    head = out.strip().lower()
    if "api error" in head or head.startswith("unexpected"):
        failures.append("sanitization: apostrophe broke the query")

    print("\n" + "=" * 60)
    if failures:
        print(f"FAIL: {len(failures)} probe(s) did not pass:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS: all probes returned data")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
