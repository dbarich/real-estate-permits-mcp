"""
Seattle Permits MCP Server (v2 - Corrected)
Exposes Seattle Open Data permit queries and King County assessor data
as tools for Claude Desktop.

Corrected in v2:
- Uses KingCo_PropertyInfo service (not KingCo_Parcels)
- Layer 0 for parcel info (zoning, use)
- Layer 3 for sales data (address, sale price, date)

Setup:
    pip install mcp httpx

Usage:
    Add to claude_desktop_config.json and restart Claude Desktop
"""

from mcp.server.fastmcp import FastMCP
import httpx
import os
import re
import sys
from datetime import datetime, timedelta

# Package version. Keep in sync with the `version` field in pyproject.toml
# and the latest entry in CHANGELOG.md when cutting a release.
__version__ = "0.2.2-alpha"

# Initialize MCP server
mcp = FastMCP("seattle-permits")

# Debug logging (stderr only — never stdout, which is the MCP transport).
# Enable with SEATTLE_PERMITS_DEBUG=1 to see the actual WHERE clauses
# being sent to the King County ArcGIS API.
DEBUG = os.environ.get("SEATTLE_PERMITS_DEBUG", "").lower() in ("1", "true", "yes", "on")

# Optional Socrata app token — unauthenticated requests are throttled by Seattle's API.
SOCRATA_APP_TOKEN = os.environ.get("SOCRATA_APP_TOKEN", "")


def _debug(msg: str) -> None:
    if DEBUG:
        print(f"[seattle-permits] {msg}", file=sys.stderr)


def _sanitize_soql(value: str) -> str:
    """Escape single quotes for safe interpolation into SoQL/ArcGIS WHERE clauses.

    Socrata SoQL and ArcGIS WHERE clauses both use single-quote string literals.
    A bare apostrophe in user input (e.g., "O'Brien") will break the query or —
    worse — allow clause injection. SQL convention is to double the quote.
    """
    return value.replace("'", "''")


_DAYS_MAX = 3650  # 10 years
_LIMIT_MAX = 200
_ZIP_RE = re.compile(r"^\d{5}$")
_PIN_RE = re.compile(r"^\d{10}$")
_PERMIT_NUM_RE = re.compile(r"^[A-Za-z0-9\-]+$")

# =============================================================================
# CONFIGURATION
# =============================================================================

# Seattle Open Data
SEATTLE_BASE_URL = "https://data.seattle.gov/resource"
SEATTLE_DATASETS = {
    "building_permits": "76t5-zqzr",
    "land_use_permits": "kkzf-ntnu",
}

# King County ArcGIS - PropertyInfo service
KC_PROPERTY_INFO = "https://gismaps.kingcounty.gov/arcgis/rest/services/Property/KingCo_PropertyInfo/MapServer"
# Layer 0 = Parcels (PIN, zoning, acreage, present use)
# Layer 3 = Property sales in last 3 years (address, sale price, buyer/seller)


# =============================================================================
# SEATTLE PERMIT QUERIES (Existing)
# =============================================================================

def _http_error(status_code: int, source: str) -> str:
    """Format an HTTP error returned by an upstream API.

    A 429 is user-fixable (rate limiting), not an outage — so it gets its own
    actionable message. For Seattle/Socrata the fix is a free app token; the
    most common trigger is a multi-query skill run without one.
    """
    if status_code == 429:
        msg = (
            f"Rate limited (HTTP 429): {source} is throttling requests because too "
            f"many arrived in a short window. This is the usual cause when a "
            f"multi-query skill stalls partway through."
        )
        if "Seattle" in source:
            msg += (
                " Unauthenticated requests share a throttled pool. Set a free "
                "SOCRATA_APP_TOKEN to raise the limit: get one at "
                "https://data.seattle.gov/profile/app_tokens, add it to your MCP "
                "server config under env (SOCRATA_APP_TOKEN), and restart Claude Desktop."
            )
        return msg
    return (
        f"API error: {source} returned HTTP {status_code}. "
        f"{source} may be experiencing issues."
    )


async def query_socrata(dataset_id: str, where_clause: str = "", limit: int = 50) -> list:
    """Query Seattle's Socrata API."""
    url = f"{SEATTLE_BASE_URL}/{dataset_id}.json"
    params = {"$limit": limit, "$order": "issueddate DESC"}
    if where_clause:
        params["$where"] = where_clause
    if SOCRATA_APP_TOKEN:
        params["$$app_token"] = SOCRATA_APP_TOKEN

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def search_permits(street_name: str, days_back: int = 365) -> str:
    """
    Search building permits by street name.

    Args:
        street_name: Street name to search (e.g., "DEARBORN", "RAINIER")
        days_back: How many days of history to search (default 365)

    Returns:
        Summary of matching permits
    """
    if not street_name or not street_name.strip():
        return "Error: street_name is required"
    street_name = street_name.strip()
    if len(street_name) < 2:
        return (
            f"Error: street_name '{street_name}' is too short — "
            f"use at least 2 characters"
        )
    days_back = max(1, min(days_back, _DAYS_MAX))

    cutoff = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    safe_street = _sanitize_soql(street_name.upper())
    where = f"originaladdress1 like '%{safe_street}%' AND issueddate > '{cutoff}'"

    try:
        results = await query_socrata(SEATTLE_DATASETS["building_permits"], where, limit=100)

        if not results:
            return (
                f"No permits found for '{street_name}' in the last {days_back} days. "
                f"Try a shorter street name or a longer time window."
            )

        output = [f"Found {len(results)} permits near {street_name}:\n"]
        for p in results[:20]:
            addr = p.get("originaladdress1", "Unknown")
            ptype = p.get("permittype", "Unknown")
            issued = p.get("issueddate", "")[:10]
            value = p.get("estprojectcost", "N/A")
            status = p.get("statuscurrent", "Unknown")
            output.append(f"- {addr}: {ptype} ({status}) - ${value} - Issued {issued}")

        if len(results) > 20:
            output.append(f"\n... and {len(results) - 20} more permits")

        return "\n".join(output)

    except httpx.TimeoutException:
        return (
            "Request timed out querying Seattle permit data. "
            "Try narrowing your search or retry in a few minutes."
        )
    except httpx.HTTPStatusError as e:
        return _http_error(e.response.status_code, "Seattle data portal")
    except Exception as e:
        return f"Unexpected error querying permits: {str(e)}"


@mcp.tool()
async def search_permits_by_zip(zip_code: str, permit_type: str = "", days_back: int = 180) -> str:
    """
    Search building permits by ZIP code, optionally filtered by permit type.

    Args:
        zip_code: 5-digit ZIP code (e.g., "98144")
        permit_type: Optional filter like "New", "Addition", "DADU" (default: all types)
        days_back: How many days of history to search (default 180)

    Returns:
        Summary of matching permits
    """
    if not zip_code or not _ZIP_RE.match(zip_code.strip()):
        return "Error: zip_code must be a 5-digit ZIP code (e.g., '98144')"
    zip_code = zip_code.strip()
    days_back = max(1, min(days_back, _DAYS_MAX))

    cutoff = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    safe_zip = _sanitize_soql(zip_code)
    where = f"zip like '{safe_zip}%' AND issueddate > '{cutoff}'"

    if permit_type:
        safe_type = _sanitize_soql(permit_type.strip().upper())
        where += f" AND permittype like '%{safe_type}%'"
    
    try:
        results = await query_socrata(SEATTLE_DATASETS["building_permits"], where, limit=100)

        if not results:
            return (
                f"No permits found in ZIP {zip_code} for the last {days_back} days. "
                f"Try removing the permit type filter or extending the time window."
            )

        output = [f"Found {len(results)} permits in ZIP {zip_code}:\n"]
        for p in results[:20]:
            addr = p.get("originaladdress1", "Unknown")
            ptype = p.get("permittype", "Unknown")
            issued = p.get("issueddate", "")[:10]
            value = p.get("estprojectcost", "N/A")
            output.append(f"- {addr}: {ptype} - ${value} - Issued {issued}")

        if len(results) > 20:
            output.append(f"\n... and {len(results) - 20} more permits")

        return "\n".join(output)

    except httpx.TimeoutException:
        return (
            "Request timed out querying Seattle permit data. "
            "Try narrowing your search or retry in a few minutes."
        )
    except httpx.HTTPStatusError as e:
        return _http_error(e.response.status_code, "Seattle data portal")
    except Exception as e:
        return f"Unexpected error querying permits: {str(e)}"


@mcp.tool()
async def get_multifamily_permits(days_back: int = 365, limit: int = 50) -> str:
    """
    Get recent multifamily/multi-unit building permits citywide.
    Useful for finding comparable projects.

    Args:
        days_back: How many days of history to search (default 365)
        limit: Maximum results to return (default 50)

    Returns:
        Summary of multifamily permits
    """
    days_back = max(1, min(days_back, _DAYS_MAX))
    limit = max(1, min(limit, _LIMIT_MAX))

    cutoff = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    # Search for multi-unit keywords in description
    where = f"""issueddate > '{cutoff}' AND (
        description like '%MULTI%' OR 
        description like '%DUPLEX%' OR 
        description like '%TRIPLEX%' OR 
        description like '%TOWNHOUSE%' OR
        description like '%APARTMENT%' OR
        description like '%UNIT%'
    )"""
    
    try:
        results = await query_socrata(SEATTLE_DATASETS["building_permits"], where, limit=limit)

        if not results:
            return (
                f"No multifamily permits found in the last {days_back} days. "
                f"Try extending the time window."
            )

        output = [f"Found {len(results)} multifamily/multi-unit permits:\n"]
        for p in results[:25]:
            addr = p.get("originaladdress1", "Unknown")
            ptype = p.get("permittype", "Unknown")
            desc = p.get("description", "")[:60]
            issued = p.get("issueddate", "")[:10]
            value = p.get("estprojectcost", "N/A")
            output.append(f"- {addr}: {ptype}")
            output.append(f"  {desc}...")
            output.append(f"  ${value} - Issued {issued}\n")

        return "\n".join(output)

    except httpx.TimeoutException:
        return (
            "Request timed out querying Seattle permit data. "
            "Try narrowing your search or retry in a few minutes."
        )
    except httpx.HTTPStatusError as e:
        return _http_error(e.response.status_code, "Seattle data portal")
    except Exception as e:
        return f"Unexpected error fetching multifamily permits: {str(e)}"


@mcp.tool()
async def get_permit_details(permit_number: str) -> str:
    """
    Look up details for a specific permit by permit number.

    Args:
        permit_number: The permit number (e.g., "6808042-CN")

    Returns:
        Detailed permit information
    """
    if not permit_number or not permit_number.strip():
        return "Error: permit_number is required"
    permit_number = permit_number.strip()
    if not _PERMIT_NUM_RE.match(permit_number):
        return (
            f"Error: permit_number '{permit_number}' contains invalid characters "
            f"(allowed: letters, digits, hyphens)"
        )

    safe_permit = _sanitize_soql(permit_number)
    where = f"permitnum = '{safe_permit}'"

    try:
        results = await query_socrata(SEATTLE_DATASETS["building_permits"], where, limit=1)

        if not results:
            return (
                f"No permit found with number '{permit_number}'. "
                f"Double-check the permit number format (e.g., '6808042-CN')."
            )

        p = results[0]
        details = [
            f"Permit: {p.get('permitnum', 'N/A')}",
            f"Address: {p.get('originaladdress1', 'N/A')}",
            f"Type: {p.get('permittype', 'N/A')}",
            f"Category: {p.get('permitcategory', 'N/A')}",
            f"Status: {p.get('statuscurrent', 'N/A')}",
            f"Description: {p.get('description', 'N/A')}",
            f"Estimated Cost: ${p.get('estprojectcost', 'N/A')}",
            f"Applied: {p.get('applieddate', 'N/A')[:10] if p.get('applieddate') else 'N/A'}",
            f"Issued: {p.get('issueddate', 'N/A')[:10] if p.get('issueddate') else 'N/A'}",
            f"Expires: {p.get('expiresdate', 'N/A')[:10] if p.get('expiresdate') else 'N/A'}",
            f"Contractor: {p.get('contractorcompanyname', 'N/A')}",
        ]
        return "\n".join(details)

    except httpx.TimeoutException:
        return (
            "Request timed out querying Seattle permit data. "
            "Try narrowing your search or retry in a few minutes."
        )
    except httpx.HTTPStatusError as e:
        return _http_error(e.response.status_code, "Seattle data portal")
    except Exception as e:
        return f"Unexpected error fetching permit: {str(e)}"


# =============================================================================
# KING COUNTY ASSESSOR QUERIES (Corrected)
# =============================================================================

async def query_kc_layer(layer: int, where_clause: str, out_fields: str = "*") -> dict:
    """Query a King County PropertyInfo MapServer layer.

    Logs the WHERE clause and feature count to stderr when
    SEATTLE_PERMITS_DEBUG is set.
    """
    url = f"{KC_PROPERTY_INFO}/{layer}/query"
    params = {
        "where": where_clause,
        "outFields": out_fields,
        "returnGeometry": "false",
        "f": "json",
    }
    _debug(f"layer {layer}  WHERE: {where_clause}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            err = data["error"]
            _debug(f"  -> API error: {err}")
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            raise RuntimeError(f"King County GIS error: {msg}")
        _debug(f"  -> {len(data.get('features', []))} features")
        return data


def format_sale_date(timestamp_ms: int) -> str:
    """Convert millisecond timestamp to readable date."""
    if not timestamp_ms:
        return "N/A"
    try:
        return datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d")
    except (ValueError, OSError, OverflowError):
        return "N/A"


# =============================================================================
# ADDRESS PARSING
# =============================================================================
# KC stores addresses uppercase with abbreviated suffixes and no punctuation,
# e.g. "2412 S DEARBORN ST" or "12821 12TH AVE S". Seattle convention puts the
# directional BEFORE the street name for E-W streets and AFTER for N-S
# avenues, so a robust LIKE query tries both orderings.

_SUFFIX_MAP = {
    "STREET": "ST", "ST": "ST",
    "AVENUE": "AVE", "AVE": "AVE", "AV": "AVE",
    "BOULEVARD": "BLVD", "BLVD": "BLVD",
    "DRIVE": "DR", "DR": "DR",
    "ROAD": "RD", "RD": "RD",
    "PLACE": "PL", "PL": "PL",
    "COURT": "CT", "CT": "CT",
    "LANE": "LN", "LN": "LN",
    "WAY": "WAY",
    "PARKWAY": "PKWY", "PKWY": "PKWY",
    "TERRACE": "TER", "TER": "TER",
    "CIRCLE": "CIR", "CIR": "CIR",
    "HIGHWAY": "HWY", "HWY": "HWY",
    "TRAIL": "TRL", "TRL": "TRL",
}
_DIRECTIONALS = {"N", "S", "E", "W", "NE", "NW", "SE", "SW"}


def _normalize_address(raw: str) -> dict:
    """Parse a free-form address into normalized parts.

    Returns dict with keys: house, leading_dir, trailing_dir, street, suffix.
    Empty dict if the input is unparseable (no tokens).
    """
    if not raw:
        return {}
    s = re.sub(r"[.,]", " ", raw.upper())
    s = re.sub(r"\s+", " ", s).strip()
    tokens = s.split()
    if not tokens:
        return {}

    house = ""
    if tokens[0][0].isdigit():
        house = tokens[0]
        tokens = tokens[1:]

    leading_dir = ""
    if tokens and tokens[0] in _DIRECTIONALS:
        leading_dir = tokens[0]
        tokens = tokens[1:]

    trailing_dir = ""
    if tokens and tokens[-1] in _DIRECTIONALS:
        trailing_dir = tokens[-1]
        tokens = tokens[:-1]

    suffix = ""
    if tokens and tokens[-1] in _SUFFIX_MAP:
        suffix = _SUFFIX_MAP[tokens[-1]]
        tokens = tokens[:-1]

    return {
        "house": house,
        "leading_dir": leading_dir,
        "trailing_dir": trailing_dir,
        "street": " ".join(tokens),
        "suffix": suffix,
    }


def _address_variants(raw: str) -> list:
    """Generate ordered list of LIKE patterns to try, most specific first."""
    p = _normalize_address(raw)
    if not p or not p.get("street"):
        return []
    house = p["house"]
    street = p["street"]
    suffix = p["suffix"]
    direction = p["leading_dir"] or p["trailing_dir"]

    candidates = []
    # Most specific: full address as parsed (leading-dir, e.g. "2412 S DEARBORN ST")
    if direction and suffix:
        candidates.append(" ".join(filter(None, [house, direction, street, suffix])))
        # Trailing-dir style, e.g. "12821 12TH AVE S"
        candidates.append(" ".join(filter(None, [house, street, suffix, direction])))
    if direction:
        candidates.append(" ".join(filter(None, [house, direction, street])))
        candidates.append(" ".join(filter(None, [house, street, direction])))
    if suffix:
        candidates.append(" ".join(filter(None, [house, street, suffix])))
    candidates.append(" ".join(filter(None, [house, street])))

    seen, out = set(), []
    for v in candidates:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _street_only(raw: str) -> str:
    """Return 'DIR STREET SUFFIX' (no house number) for nearby-parcels queries."""
    p = _normalize_address(raw)
    if not p or not p.get("street"):
        return ""
    if p["leading_dir"]:
        parts = [p["leading_dir"], p["street"], p["suffix"]]
    else:
        parts = [p["street"], p["suffix"], p["trailing_dir"]]
    return " ".join([x for x in parts if x]).strip()


# Field sets for Layer 2 (Parcels) — full ADDR_FULL, lot size, appraised values
PARCEL_FIELDS = (
    "PIN,ADDR_FULL,ADDR_HN,KCA_ZONING,KCA_ACRES,LOTSQFT,"
    "APPRLNDVAL,APPR_IMPR,PREUSE_DESC,PROPTYPE,ZIP5,POSTALCTYNAME"
)


async def _latest_sales_by_pin(features: list) -> dict:
    """For a batch of parcel features, fetch the latest Layer 3 sale per PIN."""
    pins = [f.get("attributes", {}).get("PIN") for f in features]
    pins = [p for p in pins if p][:50]  # keep WHERE clause length reasonable
    if not pins:
        return {}
    quoted = ",".join(f"'{p}'" for p in pins)
    try:
        data = await query_kc_layer(3, f"PIN IN ({quoted})", "PIN,SalePrice,SaleDate")
    except Exception as e:
        _debug(f"sales enrichment failed: {e}")
        return {}
    latest = {}
    for f in data.get("features", []):
        a = f.get("attributes", {})
        pin = a.get("PIN")
        if not pin:
            continue
        cur = latest.get(pin)
        if cur is None or (a.get("SaleDate") or 0) > (cur.get("SaleDate") or 0):
            latest[pin] = a
    return latest


@mcp.tool()
async def get_parcel_by_address(address: str) -> str:
    """
    Look up King County parcel information by address.
    Returns PIN, zoning, lot size, appraised value, and last sale (if any).

    Args:
        address: Property address (e.g., "2412 S Dearborn St")

    Returns:
        Parcel information from King County Assessor
    """
    # Input validation
    if not address or not address.strip():
        return "Error: address is required"
    if len(address.strip()) < 4:
        return f"Error: address '{address}' is too short to look up"
    if not any(c.isdigit() for c in address):
        return f"Error: address '{address}' has no house number; include the street number"

    variants = _address_variants(address)
    if not variants:
        return f"Error: could not parse a street name from '{address}'"
    _debug(f"get_parcel_by_address('{address}') -> variants: {variants}")

    tried = []
    try:
        # Layer 2 (Parcels) is the authoritative parcel layer with ADDR_FULL.
        # It covers EVERY parcel, not just those sold in the last ~3 years
        # (Layer 3). This replaces the old Layer 3 LIKE search.
        for variant in variants:
            esc = _sanitize_soql(variant)
            where = f"ADDR_FULL LIKE '%{esc}%'"
            tried.append(variant)
            data = await query_kc_layer(2, where, PARCEL_FIELDS)
            features = data.get("features", [])
            if features:
                sales = await _latest_sales_by_pin(features[:5])
                return _format_parcel_matches(address, variant, features, sales)

        # Defensive fallback: Layer 3 (sales) — catches the rare case where
        # an address was reformatted between the parcel and sales tables.
        for variant in variants:
            esc = _sanitize_soql(variant)
            where = f"address LIKE '%{esc}%'"
            data = await query_kc_layer(3, where)
            features = data.get("features", [])
            if features:
                return _format_sales_only_matches(address, variant, features)

        return (
            f"No parcel found for '{address}'. "
            f"Tried these address variants against Layer 2 (Parcels) and "
            f"Layer 3 (Sales): {', '.join(tried)}. "
            f"Check spelling, directional (N/S/E/W), and street suffix."
        )

    except httpx.TimeoutException:
        return (
            "Request timed out querying King County GIS. "
            "Try narrowing your search or retry in a few minutes."
        )
    except httpx.HTTPStatusError as e:
        return _http_error(e.response.status_code, "King County GIS")
    except Exception as e:
        return f"Unexpected error querying King County parcel data: {str(e)}"


def _format_parcel_matches(query: str, variant: str, features: list, sales: dict) -> str:
    """Render Layer 2 parcel matches with optional sales enrichment."""
    output = [
        f"Found {len(features)} parcel(s) matching '{query}' "
        f"(via variant '{variant}'):\n"
    ]
    for f in features[:5]:
        a = f.get("attributes", {})
        pin = a.get("PIN") or "N/A"
        sale = sales.get(pin, {})
        addr = (a.get("ADDR_FULL") or "").strip() or "N/A"
        zoning = a.get("KCA_ZONING") or "N/A"
        use = (a.get("PREUSE_DESC") or "").strip() or "N/A"
        lot = a.get("LOTSQFT") or 0
        land = a.get("APPRLNDVAL") or 0
        impr = a.get("APPR_IMPR") or 0
        zip5 = a.get("ZIP5") or ""

        output.append(f"Address: {addr}" + (f"  ({zip5})" if zip5 else ""))
        output.append(f"PIN: {pin}")
        output.append(f"Zoning: {zoning}")
        output.append(f"Present Use: {use}")
        output.append(f"Lot Area: {lot:,} sq ft")
        output.append(
            f"Appraised: Land ${land:,.0f} + Improvement ${impr:,.0f} "
            f"= Total ${land + impr:,.0f}"
        )
        if sale:
            output.append(
                f"Last Sale: ${sale.get('SalePrice', 0):,} on "
                f"{format_sale_date(sale.get('SaleDate'))}"
            )
        else:
            output.append("Last Sale: none in past ~3 years")
        output.append("---")
    if len(features) > 5:
        output.append(f"... and {len(features) - 5} more matches")
    return "\n".join(output)


def _format_sales_only_matches(query: str, variant: str, features: list) -> str:
    """Fallback formatter when only Layer 3 (sales) returned hits."""
    output = [
        f"Found {len(features)} sales match(es) for '{query}' "
        f"(via variant '{variant}') — parcel layer missed, "
        f"using sales layer:\n"
    ]
    for f in features[:5]:
        a = f.get("attributes", {})
        output.append(f"Address: {(a.get('address') or '').strip()}")
        output.append(f"PIN: {a.get('PIN', 'N/A')}")
        output.append(f"Sale Price: ${a.get('SalePrice', 0):,}")
        output.append(f"Sale Date: {format_sale_date(a.get('SaleDate'))}")
        output.append(f"Property Class: {(a.get('Property_Class') or '').strip()}")
        output.append("---")
    return "\n".join(output)


@mcp.tool()
async def get_parcel_by_pin(pin: str) -> str:
    """
    Look up King County parcel information by Parcel ID Number (PIN).

    Args:
        pin: The parcel ID number (e.g., "6362900036")

    Returns:
        Detailed parcel information
    """
    if not pin or not pin.strip():
        return "Error: PIN is required"
    pin = pin.strip()
    if not _PIN_RE.match(pin):
        return (
            f"Error: PIN must be a 10-digit number (e.g., '6362900036'). "
            f"Got: '{pin}'"
        )

    safe_pin = _sanitize_soql(pin)
    try:
        # Query Layer 0 for zoning/use info
        parcel_data = await query_kc_layer(0, f"PIN = '{safe_pin}'")
        parcel_features = parcel_data.get("features", [])

        # Query Layer 3 for sales info
        sales_data = await query_kc_layer(3, f"PIN = '{safe_pin}'")
        sales_features = sales_data.get("features", [])
        
        if not parcel_features and not sales_features:
            return (
                f"No parcel found with PIN: {pin}. "
                f"Verify the 10-digit Parcel ID Number from the King County Assessor."
            )
        
        output = [f"=== Parcel Details for PIN {pin} ===\n"]
        
        # Add parcel info (Layer 0)
        if parcel_features:
            p = parcel_features[0].get("attributes", {})
            output.append("--- Parcel Information ---")
            output.append(f"Property Type: {p.get('PROPTYPE', 'N/A')} ({'Residential' if p.get('PROPTYPE') == 'R' else 'Other'})")
            output.append(f"KC Zoning: {p.get('KCA_ZONING', 'N/A')}")
            output.append(f"Acres: {p.get('KCA_ACRES', 0):.4f}")
            output.append(f"Present Use Code: {p.get('PREUSE_CODE', 'N/A')}")
            output.append(f"Present Use: {(p.get('PREUSE_DESC') or 'N/A').strip()}")
            output.append(f"Lot Area: {p.get('Shape.STArea()', 0):,.0f} sq ft")
            output.append("")
        
        # Add sales info (Layer 3)
        if sales_features:
            s = sales_features[0].get("attributes", {})
            output.append("--- Sales Information ---")
            output.append(f"Address: {(s.get('address') or 'N/A').strip()}")
            output.append(f"Last Sale Price: ${s.get('SalePrice', 0):,}")
            output.append(f"Sale Date: {format_sale_date(s.get('SaleDate'))}")
            output.append(f"Buyer: {(s.get('buyername') or 'N/A').strip()}")
            output.append(f"Seller: {(s.get('Sellername') or 'N/A').strip()}")
            output.append(f"Property Class: {(s.get('Property_Class') or 'N/A').strip()}")
            output.append(f"Principal Use: {s.get('Principal_Use') or 'N/A'}")
        
        return "\n".join(output)
    
    except httpx.TimeoutException:
        return (
            "Request timed out querying King County GIS. "
            "Try narrowing your search or retry in a few minutes."
        )
    except httpx.HTTPStatusError as e:
        return _http_error(e.response.status_code, "King County GIS")
    except Exception as e:
        return f"Unexpected error querying parcel by PIN: {str(e)}"


@mcp.tool()
async def get_nearby_parcels(address: str, property_type: str = "") -> str:
    """
    Find parcels on the same street as the given address for comparable
    analysis. Uses Layer 2 (Parcels) so results include every property on the
    street, not just those sold in the last ~3 years.

    Args:
        address: Starting address (e.g., "2412 S Dearborn St")
        property_type: Optional substring match on PREUSE_DESC (e.g., "SINGLE",
            "DUPLEX", "VACANT")

    Returns:
        List of nearby parcels with valuations, sorted by total appraised value
    """
    if not address or not address.strip():
        return "Error: address is required"

    street_query = _street_only(address)
    if not street_query:
        return f"Error: could not extract a street name from '{address}'"
    _debug(f"get_nearby_parcels('{address}') -> street_query: '{street_query}'")

    esc = _sanitize_soql(street_query)
    where = f"ADDR_FULL LIKE '%{esc}%'"
    if property_type:
        safe_type = _sanitize_soql(property_type.strip().upper())
        where += f" AND PREUSE_DESC LIKE '%{safe_type}%'"

    try:
        data = await query_kc_layer(2, where, PARCEL_FIELDS)
        features = data.get("features", [])
        if not features:
            return (
                f"No parcels found on '{street_query}' for query '{address}'. "
                f"Try a different street name or drop the property type filter."
            )

        def total_value(f):
            a = f.get("attributes", {})
            return (a.get("APPRLNDVAL") or 0) + (a.get("APPR_IMPR") or 0)

        features.sort(key=total_value, reverse=True)
        top = features[:15]
        sales = await _latest_sales_by_pin(top)

        output = [f"Found {len(features)} parcels on '{street_query}':\n"]
        for f in top:
            a = f.get("attributes", {})
            pin = a.get("PIN") or "N/A"
            addr = (a.get("ADDR_FULL") or "").strip()
            zoning = a.get("KCA_ZONING") or "N/A"
            lot = a.get("LOTSQFT") or 0
            tot = total_value(f)
            line = (
                f"- {addr} | PIN {pin} | {zoning} | "
                f"Lot {lot:,} sf | Appraised ${tot:,.0f}"
            )
            sale = sales.get(pin)
            if sale:
                line += (
                    f" | Sold ${sale.get('SalePrice', 0):,} "
                    f"({format_sale_date(sale.get('SaleDate'))})"
                )
            output.append(line)
        if len(features) > 15:
            output.append(f"\n... and {len(features) - 15} more")
        return "\n".join(output)

    except httpx.TimeoutException:
        return (
            "Request timed out querying King County GIS. "
            "Try narrowing your search or retry in a few minutes."
        )
    except httpx.HTTPStatusError as e:
        return _http_error(e.response.status_code, "King County GIS")
    except Exception as e:
        return f"Unexpected error finding nearby parcels: {str(e)}"


# =============================================================================
# COMBINED ANALYSIS TOOLS
# =============================================================================

@mcp.tool()
async def get_development_comparables(address: str, days_back: int = 365) -> str:
    """
    Combined analysis: Get both permit activity and property values near an address.
    Useful for preparing bank underwriting comparables.

    Args:
        address: Target property address (e.g., "2412 S Dearborn St")
        days_back: How many days of permit history to include

    Returns:
        Combined permit and property analysis
    """
    if not address or not address.strip():
        return "Error: address is required"

    output = [f"=== Development Comparables for {address} ===\n"]

    # Use the same address parser as the parcel functions; pass the bare
    # street name to the permit search (Socrata matches it as a substring of
    # originaladdress1).
    parsed = _normalize_address(address)
    street_name = parsed.get("street") if parsed else ""

    if street_name:
        output.append("--- Recent Permit Activity ---")
        permit_results = await search_permits(street_name, days_back)
        output.append(permit_results)
        output.append("")
    else:
        output.append("--- Recent Permit Activity ---")
        output.append(f"(skipped — could not parse street name from '{address}')")
        output.append("")

    output.append("--- Nearby Parcels & Recent Sales ---")
    parcel_results = await get_nearby_parcels(address)
    output.append(parcel_results)

    return "\n".join(output)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    _debug(f"Socrata app token: {'configured' if SOCRATA_APP_TOKEN else 'not set (throttled)'}")
    mcp.run()
