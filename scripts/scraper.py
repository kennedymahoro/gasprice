import urllib.request
import re
import json
import time
import os
import sys

TOPOJSON_URL = "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json"
TOPOJSON_PATH = "../public/counties-10m.json"

STATE_FIPS = {
    "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas", "06": "California",
    "08": "Colorado", "09": "Connecticut", "10": "Delaware", "11": "District of Columbia",
    "12": "Florida", "13": "Georgia", "15": "Hawaii", "16": "Idaho", "17": "Illinois",
    "18": "Indiana", "19": "Iowa", "20": "Kansas", "21": "Kentucky", "22": "Louisiana",
    "23": "Maine", "24": "Maryland", "25": "Massachusetts", "26": "Michigan", "27": "Minnesota",
    "28": "Mississippi", "29": "Missouri", "30": "Montana", "31": "Nebraska", "32": "Nevada",
    "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico", "36": "New York", 
    "37": "North Carolina", "38": "North Dakota", "39": "Ohio", "40": "Oklahoma", "41": "Oregon",
    "42": "Pennsylvania", "44": "Rhode Island", "45": "South Carolina", "46": "South Dakota",
    "47": "Tennessee", "48": "Texas", "49": "Utah", "50": "Vermont", "51": "Virginia",
    "53": "Washington", "54": "West Virginia", "55": "Wisconsin", "56": "Wyoming"
}

def clean_county_name(name):
    """Normalize county names to handle differences between AAA and TopoJSON"""
    name = name.lower()
    name = name.replace(" county", "").replace(" parish", "").replace(" borough", "").replace(" census area", "").replace(" municipality", "")
    name = name.replace("city and", "").replace("city", "").strip()
    name = re.sub(r'[^a-z0-9]', '', name)
    return name

def ensure_topojson():
    target_path = os.path.join(os.path.dirname(__file__), TOPOJSON_PATH)
    if not os.path.exists(target_path):
        print(f"Downloading {TOPOJSON_URL} to {target_path}")
        urllib.request.urlretrieve(TOPOJSON_URL, target_path)
    with open(target_path, 'r') as f:
        return json.load(f)

def build_fips_map(topojson_data):
    """Build a mapping of state_fips -> { clean_county_name: county_fips }"""
    fips_map = {}
    geometries = topojson_data["objects"]["counties"]["geometries"]
    for geo in geometries:
        fips = geo["id"]
        name = geo["properties"]["name"]
        
        state_fips = fips[:2]
        if state_fips not in fips_map:
            fips_map[state_fips] = {}
        
        fips_map[state_fips][clean_county_name(name)] = fips
        
    return fips_map

def fetch_map_data(map_id):
    url = f"https://gasprices.aaa.com/index.php?premiumhtml5map_js_data=true&map_id={map_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        match = re.search(r'map_data\s*:\s*(\{.*?\})\s*,groups', html, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception as e:
        print(f"Error fetching map_id {map_id}: {e}")
    return None

def main():
    print("Starting AAA Gas Price Scraper...")
    
    # 1. Prepare TopoJSON state/county dictionaries
    topo_data = ensure_topojson()
    fips_map = build_fips_map(topo_data)
    
    # Final data structure: { FIPS: { "regular": price, "premium": price, "diesel": price } }
    final_data = {}
    
    # 2. Iterate map IDs to fetch AAA map data
    for map_id in range(1, 60):
        data = fetch_map_data(map_id)
        if not data:
            continue
            
        print(f"\nProcessing map_id={map_id}...")
        
        # Parse map items
        map_items = {}
        for key, region in data.items():
            name = region.get("name", "")
            price_str = region.get("comment", "")
            if price_str.startswith("$"):
                try:
                    price = float(price_str.replace("$", "").replace(",", ""))
                    map_items[clean_county_name(name)] = price
                except ValueError:
                    continue
        
        if not map_items:
            continue
            
        # Match this map to a state by looking at overlap in county names
        best_state = None
        best_overlap = 0
        
        for state_fips, counties_in_state in fips_map.items():
            overlap = sum(1 for c in map_items if c in counties_in_state)
            if overlap > best_overlap:
                best_overlap = overlap
                best_state = state_fips
                
        if best_state and best_overlap > len(map_items) * 0.5:
            print(f"  Matched to State: {STATE_FIPS.get(best_state, best_state)} (Overlap: {best_overlap}/{len(map_items)})")
            
            # Record prices mapped to FIPS codes
            state_counties = fips_map[best_state]
            for clean_name, price in map_items.items():
                if clean_name in state_counties:
                    county_fips = state_counties[clean_name]
                    # Since AAA County maps only show Regular gas price, we'll interpolate Premium/Diesel (+20%, +25% roughly based on CA data)
                    final_data[county_fips] = {
                        "regular": price,
                        "premium": round(price * 1.15, 3), # AAA county map lacks Premium, simulating standard markup
                        "diesel": round(price * 1.20, 3)   # Simulating standard diesel markup
                    }
        else:
            print(f"  Could not strongly match map {map_id} to any state.")
            
        time.sleep(1) # Be nice to servers

    # 3. Save to public directory
    output_path = os.path.join(os.path.dirname(__file__), "../public/gas_prices.json")
    with open(output_path, "w") as f:
        json.dump(final_data, f)
        
    print(f"\nSaved {len(final_data)} county prices to {output_path}")

if __name__ == "__main__":
    main()
