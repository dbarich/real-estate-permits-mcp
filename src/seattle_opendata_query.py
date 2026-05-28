#!/usr/bin/env python3
"""
Seattle Open Data Query Script
For: 2412 S Dearborn St Development Project

This script queries Seattle's public data portal (data.seattle.gov) 
to pull permit and construction data relevant to your project.

Requirements: 
    pip install requests pandas

Usage:
    python seattle_opendata_query.py

Output:
    - building_permits_nearby.csv
    - dadu_permits_98144.csv
    - query_summary.txt
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# =============================================================================
# CONFIGURATION
# =============================================================================

# Your project details - modify these as needed
PROJECT_ZIP = "98144"
PROJECT_STREET = "DEARBORN"
SEARCH_RADIUS_DAYS = 365  # Look back 1 year for recent permits

# Seattle Open Data base URL (Socrata API)
BASE_URL = "https://data.seattle.gov/resource"

# Dataset IDs - these are the unique identifiers for each dataset
# You can find these in the URL when viewing a dataset on data.seattle.gov
DATASETS = {
    "building_permits": "76t5-zqzr",      # All building permits
    "dadu_permits": "q4q8-8w9v",          # Detached ADU permits specifically
    "issued_permits": "8tqq-u7ib",        # Issued (completed) permits
}

# Output directory
OUTPUT_DIR = "seattle_data_output"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def query_socrata(dataset_id, query_params=None, limit=1000):
    """
    Query a Socrata dataset and return the results as a list of dictionaries.
    
    How Socrata API works:
    - Each dataset has a unique ID (like "76t5-zqzr")
    - You access it at: https://data.seattle.gov/resource/{dataset_id}.json
    - You can add query parameters using SoQL (Socrata Query Language)
    - Common parameters:
        $where  = filter rows (like SQL WHERE)
        $select = choose columns (like SQL SELECT)
        $limit  = max rows to return
        $order  = sort results
    
    Args:
        dataset_id: The Socrata dataset identifier
        query_params: Dictionary of SoQL query parameters
        limit: Maximum number of records to return
    
    Returns:
        List of dictionaries (each dict is one row)
    """
    url = f"{BASE_URL}/{dataset_id}.json"
    
    # Build the request parameters
    params = {"$limit": limit}
    if query_params:
        params.update(query_params)
    
    print(f"  Querying: {url}")
    print(f"  Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        print(f"  Retrieved: {len(data)} records")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  ERROR: {e}")
        return []


def save_to_csv(data, filename):
    """
    Convert list of dictionaries to a pandas DataFrame and save as CSV.
    
    Args:
        data: List of dictionaries from API response
        filename: Output filename (will be saved in OUTPUT_DIR)
    """
    if not data:
        print(f"  No data to save for {filename}")
        return None
    
    df = pd.DataFrame(data)
    filepath = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(filepath, index=False)
    print(f"  Saved: {filepath} ({len(df)} rows, {len(df.columns)} columns)")
    return df


# =============================================================================
# QUERY FUNCTIONS
# =============================================================================

def get_building_permits_nearby():
    """
    Query 1: Building permits on or near Dearborn St
    
    This uses the $where parameter with a LIKE clause to find
    permits where the address contains "DEARBORN".
    
    SoQL syntax note:
    - Text matching uses: field like '%text%'
    - The % is a wildcard (matches any characters)
    - Single quotes around the search term
    """
    print("\n[1] Querying building permits near Dearborn St...")
    
    # Calculate date 1 year ago for filtering recent permits
    one_year_ago = (datetime.now() - timedelta(days=SEARCH_RADIUS_DAYS)).strftime("%Y-%m-%d")
    
    # Build the WHERE clause
    # We're looking for: address contains DEARBORN AND issued after one_year_ago
    where_clause = f"originaladdress1 like '%{PROJECT_STREET}%' AND issueddate > '{one_year_ago}'"
    
    query_params = {
        "$where": where_clause,
        "$order": "issueddate DESC",  # Most recent first
    }
    
    data = query_socrata(DATASETS["building_permits"], query_params)
    return save_to_csv(data, "building_permits_nearby.csv")


def get_dadu_permits_in_zip():
    """
    Query 2: DADU (Detached ADU) permits in your zip code
    
    This helps you understand ADU construction trends in your area.
    Useful for:
    - Seeing what other people are building
    - Understanding typical permit timelines
    - Finding comparable projects
    """
    print(f"\n[2] Querying DADU permits in {PROJECT_ZIP}...")
    
    # Note: The zip field name may vary by dataset
    # Common variations: zip, zipcode, zip_code
    # You may need to adjust based on actual field names
    query_params = {
        "$where": f"zip = '{PROJECT_ZIP}'",
        "$order": "issueddate DESC",
    }
    
    data = query_socrata(DATASETS["dadu_permits"], query_params)
    return save_to_csv(data, f"dadu_permits_{PROJECT_ZIP}.csv")


def get_recent_issued_permits_in_zip():
    """
    Query 3: Recently issued permits in your zip code
    
    "Issued" permits are those that have been approved and construction
    can begin. This is different from "in review" or "pending" permits.
    
    This data helps you understand:
    - Construction activity level in your area
    - Types of projects being approved
    - Typical project valuations
    """
    print(f"\n[3] Querying recently issued permits in {PROJECT_ZIP}...")
    
    one_year_ago = (datetime.now() - timedelta(days=SEARCH_RADIUS_DAYS)).strftime("%Y-%m-%d")
    
    query_params = {
        "$where": f"zip = '{PROJECT_ZIP}' AND issueddate > '{one_year_ago}'",
        "$order": "issueddate DESC",
        "$limit": 500,  # Limit to avoid huge downloads
    }
    
    data = query_socrata(DATASETS["issued_permits"], query_params)
    return save_to_csv(data, f"issued_permits_{PROJECT_ZIP}.csv")


def get_multifamily_permits():
    """
    Query 4: Multifamily construction permits citywide (recent)
    
    Since you're building a stacked flat (essentially multifamily),
    this shows comparable projects across Seattle.
    
    The permitclass or category field typically indicates project type.
    Common values: "Multifamily", "Single Family / Duplex", "Commercial"
    """
    print("\n[4] Querying recent multifamily permits citywide...")
    
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    
    # Note: Field names for permit type vary
    # This query looks for "Multifamily" in the permitclass field
    query_params = {
        "$where": f"permitclass = 'Multifamily' AND issueddate > '{six_months_ago}'",
        "$order": "issueddate DESC",
        "$limit": 200,
    }
    
    data = query_socrata(DATASETS["building_permits"], query_params)
    return save_to_csv(data, "multifamily_permits_recent.csv")


# =============================================================================
# SUMMARY REPORT
# =============================================================================

def generate_summary(dataframes):
    """
    Generate a text summary of what was retrieved.
    """
    summary_path = os.path.join(OUTPUT_DIR, "query_summary.txt")
    
    with open(summary_path, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("SEATTLE OPEN DATA QUERY SUMMARY\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Project: 2412 S Dearborn St\n")
        f.write("=" * 60 + "\n\n")
        
        for name, df in dataframes.items():
            f.write(f"\n{name}\n")
            f.write("-" * 40 + "\n")
            if df is not None:
                f.write(f"Records retrieved: {len(df)}\n")
                f.write(f"Columns: {', '.join(df.columns[:10])}")
                if len(df.columns) > 10:
                    f.write(f"... and {len(df.columns) - 10} more")
                f.write("\n")
            else:
                f.write("No data retrieved\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("NEXT STEPS\n")
        f.write("=" * 60 + "\n")
        f.write("""
1. Open the CSV files in Excel or Google Sheets
2. Review the building_permits_nearby.csv for projects on/near Dearborn
3. Check dadu_permits for ADU construction trends in 98144
4. Use multifamily_permits to find comparable stacked flat projects
5. Copy relevant data into your MCP Baseline Data Sheet (Tab 4)

For more queries, modify the query_params in each function.
Socrata documentation: https://dev.socrata.com/docs/queries/
        """)
    
    print(f"\nSummary saved to: {summary_path}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main function - runs all queries and saves results.
    """
    print("=" * 60)
    print("SEATTLE OPEN DATA QUERY SCRIPT")
    print(f"Project: 2412 S Dearborn St ({PROJECT_ZIP})")
    print("=" * 60)
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\nOutput directory: {OUTPUT_DIR}/")
    
    # Run all queries and collect results
    results = {}
    
    results["Building Permits (Dearborn St)"] = get_building_permits_nearby()
    results["DADU Permits (98144)"] = get_dadu_permits_in_zip()
    results["Issued Permits (98144)"] = get_recent_issued_permits_in_zip()
    results["Multifamily Permits (Citywide)"] = get_multifamily_permits()
    
    # Generate summary report
    generate_summary(results)
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print(f"Check the '{OUTPUT_DIR}' folder for your CSV files.")
    print("=" * 60)


# This block runs when you execute the script directly
# (as opposed to importing it as a module)
if __name__ == "__main__":
    main()
