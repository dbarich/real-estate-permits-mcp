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
from datetime import datetime, timedelta

# Initialize MCP server
mcp = FastMCP("seattle-permits")

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

async def query_socrata(dataset_id: str, where_clause: str = "", limit: int = 50) -> list:
    """Query Seattle's Socrata API."""
    url = f"{SEATTLE_BASE_URL}/{dataset_id}.json"
    params = {"$limit": limit, "$order": "issueddate DESC"}
    if where_clause:
        params["$where"] = where_clause
    
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
    cutoff = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    where = f"originaladdress1 like '%{street_name.upper()}%' AND issueddate > '{cutoff}'"
    
    try:
        results = await query_socrata(SEATTLE_DATASETS["building_permits"], where, limit=100)
        
        if not results:
            return f"No permits found for '{street_name}' in the last {days_back} days."
        
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
    
    except Exception as e:
        return f"Error searching permits: {str(e)}"


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
    cutoff = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    where = f"zip like '{zip_code}%' AND issueddate > '{cutoff}'"
    
    if permit_type:
        where += f" AND permittype like '%{permit_type.upper()}%'"
    
    try:
        results = await query_socrata(SEATTLE_DATASETS["building_permits"], where, limit=100)
        
        if not results:
            return f"No permits found in ZIP {zip_code} for the last {days_back} days."
        
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
    
    except Exception as e:
        return f"Error searching permits: {str(e)}"


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
            return f"No multifamily permits found in the last {days_back} days."
        
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
    
    except Exception as e:
        return f"Error fetching multifamily permits: {str(e)}"


@mcp.tool()
async def get_permit_details(permit_number: str) -> str:
    """
    Look up details for a specific permit by permit number.

    Args:
        permit_number: The permit number (e.g., "6808042-CN")

    Returns:
        Detailed permit information
    """
    where = f"permitnum = '{permit_number}'"
    
    try:
        results = await query_socrata(SEATTLE_DATASETS["building_permits"], where, limit=1)
        
        if not results:
            return f"No permit found with number '{permit_number}'."
        
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
    
    except Exception as e:
        return f"Error fetching permit: {str(e)}"


# =============================================================================
# KING COUNTY ASSESSOR QUERIES (Corrected)
# =============================================================================

async def query_kc_layer(layer: int, where_clause: str) -> dict:
    """Query a King County PropertyInfo MapServer layer."""
    url = f"{KC_PROPERTY_INFO}/{layer}/query"
    params = {
        "where": where_clause,
        "outFields": "*",
        "returnGeometry": "false",
        "f": "json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def format_sale_date(timestamp_ms: int) -> str:
    """Convert millisecond timestamp to readable date."""
    if not timestamp_ms:
        return "N/A"
    try:
        return datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d")
    except:
        return "N/A"


@mcp.tool()
async def get_parcel_by_address(address: str) -> str:
    """
    Look up King County parcel information by address.
    Returns PIN, assessed value, lot size, and other property details.

    Args:
        address: Property address (e.g., "2412 S Dearborn St")

    Returns:
        Parcel information from King County Assessor
    """
    # Search Layer 3 (sales) which has address field
    # Use LIKE for flexible matching
    search_addr = address.upper().replace("'", "''")
    where = f"address LIKE '%{search_addr}%'"
    
    try:
        data = await query_kc_layer(3, where)
        features = data.get("features", [])
        
        if not features:
            # Try partial match on street name
            parts = address.upper().split()
            for part in parts:
                if len(part) > 3 and not part.isdigit():
                    where = f"address LIKE '%{part}%'"
                    data = await query_kc_layer(3, where)
                    features = data.get("features", [])
                    if features:
                        break
        
        if not features:
            return f"No parcel found for address: {address}"
        
        output = [f"Found {len(features)} parcel(s) matching '{address}':\n"]
        
        for f in features[:5]:
            a = f.get("attributes", {})
            output.append(f"Address: {a.get('address', 'N/A').strip()}")
            output.append(f"PIN: {a.get('PIN', 'N/A')}")
            output.append(f"Sale Price: ${a.get('SalePrice', 0):,}")
            output.append(f"Sale Date: {format_sale_date(a.get('SaleDate'))}")
            output.append(f"Property Type: {a.get('Property_Type', 'N/A')}")
            output.append(f"Principal Use: {a.get('Principal_Use', 'N/A')}")
            output.append(f"Property Class: {a.get('Property_Class', 'N/A').strip()}")
            output.append(f"Lot Area: {a.get('shape.STArea()', 0):,.0f} sq ft")
            output.append("---")
        
        return "\n".join(output)
    
    except httpx.HTTPStatusError as e:
        return f"HTTP error querying King County: {e.response.status_code}"
    except Exception as e:
        return f"Error querying King County parcel data: {str(e)}"


@mcp.tool()
async def get_parcel_by_pin(pin: str) -> str:
    """
    Look up King County parcel information by Parcel ID Number (PIN).

    Args:
        pin: The parcel ID number (e.g., "6362900036")

    Returns:
        Detailed parcel information
    """
    try:
        # Query Layer 0 for zoning/use info
        parcel_data = await query_kc_layer(0, f"PIN = '{pin}'")
        parcel_features = parcel_data.get("features", [])
        
        # Query Layer 3 for sales info
        sales_data = await query_kc_layer(3, f"PIN = '{pin}'")
        sales_features = sales_data.get("features", [])
        
        if not parcel_features and not sales_features:
            return f"No parcel found with PIN: {pin}"
        
        output = [f"=== Parcel Details for PIN {pin} ===\n"]
        
        # Add parcel info (Layer 0)
        if parcel_features:
            p = parcel_features[0].get("attributes", {})
            output.append("--- Parcel Information ---")
            output.append(f"Property Type: {p.get('PROPTYPE', 'N/A')} ({'Residential' if p.get('PROPTYPE') == 'R' else 'Other'})")
            output.append(f"KC Zoning: {p.get('KCA_ZONING', 'N/A')}")
            output.append(f"Acres: {p.get('KCA_ACRES', 0):.4f}")
            output.append(f"Present Use Code: {p.get('PREUSE_CODE', 'N/A')}")
            output.append(f"Present Use: {p.get('PREUSE_DESC', 'N/A').strip()}")
            output.append(f"Lot Area: {p.get('Shape.STArea()', 0):,.0f} sq ft")
            output.append("")
        
        # Add sales info (Layer 3)
        if sales_features:
            s = sales_features[0].get("attributes", {})
            output.append("--- Sales Information ---")
            output.append(f"Address: {s.get('address', 'N/A').strip()}")
            output.append(f"Last Sale Price: ${s.get('SalePrice', 0):,}")
            output.append(f"Sale Date: {format_sale_date(s.get('SaleDate'))}")
            output.append(f"Buyer: {s.get('buyername', 'N/A').strip()}")
            output.append(f"Seller: {s.get('Sellername', 'N/A').strip()}")
            output.append(f"Property Class: {s.get('Property_Class', 'N/A').strip()}")
            output.append(f"Principal Use: {s.get('Principal_Use', 'N/A')}")
        
        return "\n".join(output)
    
    except httpx.HTTPStatusError as e:
        return f"HTTP error querying King County: {e.response.status_code}"
    except Exception as e:
        return f"Error querying parcel by PIN: {str(e)}"


@mcp.tool()
async def get_nearby_parcels(address: str, property_type: str = "") -> str:
    """
    Find parcels near a given address for comparable analysis.
    Note: This is a simplified version - for production, would use spatial query.

    Args:
        address: Starting address (e.g., "2412 S Dearborn St")
        property_type: Optional filter (e.g., "Residential", "Commercial")

    Returns:
        List of nearby parcels with valuations
    """
    # Extract street name from address for searching
    parts = address.upper().split()
    street_name = None
    for part in parts:
        if part not in ["N", "S", "E", "W", "NE", "NW", "SE", "SW", "ST", "AVE", "BLVD", "DR", "RD", "WAY", "PL", "CT"] and not part.isdigit():
            street_name = part
            break
    
    if not street_name:
        return "Could not extract street name from address"
    
    where = f"address LIKE '%{street_name}%'"
    if property_type:
        where += f" AND Principal_Use LIKE '%{property_type.upper()}%'"
    
    try:
        data = await query_kc_layer(3, where)
        features = data.get("features", [])
        
        if not features:
            return f"No nearby parcels found for: {address}"
        
        output = [f"Found {len(features)} parcels on '{street_name}':\n"]
        
        # Sort by sale price descending for relevance
        sorted_features = sorted(features, key=lambda x: x.get("attributes", {}).get("SalePrice", 0), reverse=True)
        
        for f in sorted_features[:15]:
            a = f.get("attributes", {})
            addr = a.get('address', 'N/A').strip()
            pin = a.get('PIN', 'N/A')
            price = a.get('SalePrice', 0)
            date = format_sale_date(a.get('SaleDate'))
            lot = a.get('shape.STArea()', 0)
            
            output.append(f"- {addr}")
            output.append(f"  PIN: {pin} | Sale: ${price:,} ({date}) | Lot: {lot:,.0f} sq ft")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error finding nearby parcels: {str(e)}"


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
    output = [f"=== Development Comparables for {address} ===\n"]
    
    # Extract street name for permit search
    parts = address.upper().split()
    street_name = None
    for part in parts:
        if part not in ["N", "S", "E", "W", "NE", "NW", "SE", "SW", "ST", "AVE", "BLVD", "DR", "RD", "WAY", "PL", "CT"] and not part.isdigit():
            street_name = part
            break
    
    if street_name:
        output.append("--- Recent Permit Activity ---")
        permit_results = await search_permits(street_name, days_back)
        output.append(permit_results)
        output.append("")
    
    output.append("--- Recent Property Sales ---")
    parcel_results = await get_nearby_parcels(address)
    output.append(parcel_results)
    
    return "\n".join(output)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    mcp.run()
