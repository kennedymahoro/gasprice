import urllib.request
import re
import json
import time
import os

def fetch_map_data(map_id):
    url = f"https://gasprices.aaa.com/index.php?premiumhtml5map_js_data=true&map_id={map_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        # Extract map_data JSON object
        match = re.search(r'map_data\s*:\s*(\{.*?\})\s*,groups', html, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception as e:
        print(f"Error fetching map_id {map_id}: {e}")
    return None

def main():
    print("Starting AAA Gas Price Scraper...")
    all_county_data = {}
    
    # Iterate through plausible map IDs
    for map_id in range(1, 60):
        print(f"Fetching map {map_id}...")
        data = fetch_map_data(map_id)
        if data:
            # Check if this map contains counties. County maps usually have >20 regions.
            # But wait, Rhode Island has 5 counties, Delaware has 3.
            # We will just collect everything that looks like a county (has 'comment': '$x.xxx')
            for key, region in data.items():
                name = region.get("name", "")
                price_str = region.get("comment", "")
                
                # Check if it has a valid price
                if price_str.startswith("$"):
                    try:
                        price = float(price_str.replace("$", ""))
                        if name not in all_county_data:
                            all_county_data[name] = []
                        all_county_data[name].append(price)
                    except ValueError:
                        pass
        time.sleep(0.5) # Rate limiting
        
    print(f"Extracted {len(all_county_data)} distinct county names.")
    
    # Save raw data for analysis
    with open("county_prices_raw.json", "w") as f:
        json.dump(all_county_data, f, indent=2)
        
if __name__ == "__main__":
    main()
