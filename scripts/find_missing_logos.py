import os
import requests
from pathlib import Path

# Define missing logos with their proper domains and alternative sources
MISSING_LOGOS = [
    {
        "path": "Accounts_Banking/Other_Cards/Indigo",
        "sources": [
            "https://cardsformiles.com/wp-content/uploads/2023/07/indigo-platinum-mastercard-logo.png",
            "https://www.indigocard.com/images/indigo_logo.svg",
            "https://icm.aexp-static.com/Internet/Acquisition/US_en/AppContent/OneSite/category/cardarts/platinum-card.png"
        ]
    },
    {
        "path": "Bills_Payments/Utilities/Electric_PSO",
        "sources": [
            "https://www.psoklahoma.com/lib/img/logo.png", 
            "https://www.oge.com/wps/wcm/connect/ogemaster/bc12640c-4ed1-438b-9bd4-c1102669a8cb/oge-logo.svg?MOD=AJPERES",
            "https://www.psoklahoma.com/content/dam/aep-refresh/pso/images/PSO-logo.png"
        ]
    },
    {
        "path": "Bills_Payments/Utilities/Gas_ONG",
        "sources": [
            "https://www.oklahomanaturalgas.com/images/OklahomaNaturalGas.svg",
            "https://www.oklahomanaturalgas.com/docs/default-source/default-document-library/ong_logo.png",
            "https://www.ong.com/images/OklahomaNaturalGas.svg"
        ]
    }
]

# Base directory
OUT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def save_bytes(path, content):
    with open(path, "wb") as f:
        f.write(content)

def try_download(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image"):
            ext = "svg" if "svg" in r.headers.get("Content-Type", "") else "png"
            return r.content, ext
    except Exception as e:
        print(f"      Error downloading {url}: {e}")
    return None, None

def main():
    print("=" * 70)
    print("MISSING LOGOS FINDER - Starting fetch...")
    print("=" * 70)
    
    found_count = 0
    
    for item in MISSING_LOGOS:
        rel_path = item["path"]
        full_dir = os.path.join(OUT_ROOT, rel_path)
        ensure_dir(full_dir)
        
        company_name = rel_path.split("/")[-1]
        print(f"\nTrying to find: {company_name}")
        
        success = False
        for idx, url in enumerate(item["sources"], 1):
            print(f"    Attempt {idx}: {url}")
            data, ext = try_download(url)
            if data:
                out_file = os.path.join(full_dir, f"logo.{ext}")
                save_bytes(out_file, data)
                print(f"      ✓ SUCCESS! Downloaded logo to {out_file}")
                found_count += 1
                success = True
                break
                
        if not success:
            print(f"      ✗ FAILED: Could not download any logo for {company_name}")

    print("\n" + "=" * 70)
    print(f"SUMMARY: Successfully found {found_count} out of {len(MISSING_LOGOS)} missing logos")
    print("=" * 70)

if __name__ == "__main__":
    main()
