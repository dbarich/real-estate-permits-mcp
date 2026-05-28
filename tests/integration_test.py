"""
Integration test: Two-property full query sequence against live APIs.

Property 1: Bookstorhaus — 2412 S Dearborn St, PIN 6362900036
Property 2: PIN 1364300565 (address discovered via PIN lookup)

Runs every MCP tool against real data. Use this to validate the full
stack after code changes and to produce a second milestone snapshot.

    SEATTLE_PERMITS_DEBUG=1 python tests/integration_test.py

Exit code 0 = all probes returned data. Exit code 1 = at least one failure.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import seattle_permits_server as s  # noqa: E402

RESULTS = {}


async def run_query(label, coro):
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")
    try:
        out = await coro
        # Truncate long output for readability
        print(out[:2000] if len(out) > 2000 else out)
        is_error = out.strip().lower().startswith((
            "error", "unexpected", "request timed out", "api error"
        ))
        RESULTS[label] = {
            "status": "OK" if not is_error else "FAIL",
            "length": len(out),
            "preview": out[:300],
        }
        return out
    except Exception as e:
        print(f"!! EXCEPTION: {type(e).__name__}: {e}")
        RESULTS[label] = {"status": "EXCEPTION", "error": str(e)}
        return None


async def test_property(name, address, pin, streets):
    """Run the full query suite for a single property."""
    print(f"\n\n{'#'*70}")
    print(f"  PROPERTY: {name}")
    print(f"  Address: {address or '(discovering)'}  |  PIN: {pin}")
    print(f"{'#'*70}")

    # 1. Parcel by PIN — always works if the PIN exists
    await run_query(
        f"{name} | get_parcel_by_pin({pin})",
        s.get_parcel_by_pin(pin),
    )

    # 2. Parcel by address
    if address:
        await run_query(
            f"{name} | get_parcel_by_address({address})",
            s.get_parcel_by_address(address),
        )

    # 3. Nearby parcels (same street)
    if address:
        await run_query(
            f"{name} | get_nearby_parcels({address})",
            s.get_nearby_parcels(address),
        )

    # 4. Development comparables (combined permits + parcels)
    if address:
        await run_query(
            f"{name} | get_development_comparables({address}, 730d)",
            s.get_development_comparables(address, days_back=730),
        )

    # 5. Permit search on each street name
    for street in streets:
        await run_query(
            f"{name} | search_permits({street}, 730d)",
            s.search_permits(street, days_back=730),
        )

    # 6. Multifamily permits (citywide comps)
    await run_query(
        f"{name} | get_multifamily_permits(730d, limit=10)",
        s.get_multifamily_permits(days_back=730, limit=10),
    )


async def main():
    start = datetime.now()

    # === PROPERTY 1: Bookstorhaus ===
    await test_property(
        name="Bookstorhaus",
        address="2412 S Dearborn St",
        pin="6362900036",
        streets=["DEARBORN", "JUDKINS"],
    )

    # === PROPERTY 2: Discover address from PIN, then run full suite ===
    print(f"\n\n{'#'*70}")
    print(f"  PROPERTY 2: PIN 1364300565 — discovering address...")
    print(f"{'#'*70}")

    pin2_result = await run_query(
        "Property2 | get_parcel_by_pin(1364300565)",
        s.get_parcel_by_pin("1364300565"),
    )

    # Parse address from the PIN lookup output
    addr2 = None
    if pin2_result:
        for line in pin2_result.splitlines():
            if line.startswith("Address:"):
                candidate = line.replace("Address:", "").strip()
                if candidate and candidate != "N/A":
                    addr2 = candidate
                    break

    if addr2:
        print(f"\n  >> Discovered address: {addr2}")

        # Extract the street name for permit search
        # Parse using the server's own normalizer
        parsed = s._normalize_address(addr2)
        street_name = parsed.get("street", "") if parsed else ""
        streets2 = [street_name] if street_name else []

        await run_query(
            f"Property2 | get_parcel_by_address({addr2})",
            s.get_parcel_by_address(addr2),
        )
        await run_query(
            f"Property2 | get_nearby_parcels({addr2})",
            s.get_nearby_parcels(addr2),
        )
        await run_query(
            f"Property2 | get_development_comparables({addr2}, 730d)",
            s.get_development_comparables(addr2, days_back=730),
        )
        for st in streets2:
            await run_query(
                f"Property2 | search_permits({st}, 730d)",
                s.search_permits(st, days_back=730),
            )
        await run_query(
            f"Property2 | get_multifamily_permits(730d, limit=10)",
            s.get_multifamily_permits(days_back=730, limit=10),
        )
    else:
        print("  >> Could not discover address from PIN lookup.")
        print("  >> Only PIN-based queries available for Property 2.")

    # === VALIDATION PROBES (quick sanity checks) ===
    print(f"\n\n{'#'*70}")
    print(f"  VALIDATION PROBES")
    print(f"{'#'*70}")

    validation_cases = [
        ("empty street", s.search_permits("", 365)),
        ("bad zip", s.search_permits_by_zip("abc")),
        ("empty permit", s.get_permit_details("")),
        ("bad PIN", s.get_parcel_by_pin("abc")),
        ("injection attempt", s.get_permit_details("'; DROP TABLE --")),
        ("apostrophe sanitization", s.search_permits("O'BRIEN", 365)),
    ]
    validation_pass = 0
    for label, coro in validation_cases:
        out = await coro
        # First 5 should start with "Error", last one should NOT be an API error
        if label == "apostrophe sanitization":
            ok = "api error" not in out.lower() and not out.lower().startswith("unexpected")
        else:
            ok = out.startswith("Error")
        icon = "PASS" if ok else "FAIL"
        print(f"  [{icon}] {label}: {out[:80]}")
        if ok:
            validation_pass += 1
        RESULTS[f"validation | {label}"] = {"status": "OK" if ok else "FAIL", "preview": out[:200]}

    # === SUMMARY ===
    elapsed = (datetime.now() - start).total_seconds()
    print(f"\n\n{'='*70}")
    print(f"  INTEGRATION TEST SUMMARY")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"{'='*70}")

    ok_count = sum(1 for r in RESULTS.values() if r["status"] == "OK")
    fail_count = sum(1 for r in RESULTS.values() if r["status"] != "OK")
    print(f"  {ok_count} passed / {fail_count} failed / {len(RESULTS)} total\n")

    for label, r in RESULTS.items():
        icon = "PASS" if r["status"] == "OK" else "FAIL"
        print(f"  [{icon}] {label}")

    # Save JSON results for snapshot diffing
    results_path = REPO_ROOT / "tests" / "integration_results.json"
    with open(results_path, "w") as f:
        json.dump({
            "timestamp": start.isoformat(),
            "elapsed_s": round(elapsed, 1),
            "pass": ok_count,
            "fail": fail_count,
            "results": RESULTS,
        }, f, indent=2)
    print(f"\n  Results saved to: {results_path}")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
