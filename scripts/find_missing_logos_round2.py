import os
import requests
from pathlib import Path
import time

# More detailed sources for missing logos
MISSING_LOGOS = [
    {
        "path": "Bills_Payments/Utilities/Electric_PSO",
        "name": "Public Service Company of Oklahoma (PSO)",
        "sources": [
            "https://www.psoklahoma.com/lib/img/pso-logo.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Public_Service_Company_of_Oklahoma_logo.svg/1200px-Public_Service_Company_of_Oklahoma_logo.svg.png",
            "https://www.aep.com/Assets/img/logo/aep-black.png",
            "https://www.investopedia.com/thmb/u9nYNHTlEBOQg8MQu7lN90BpExo=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/PSO-LOGOlogo-5bafc7f146e0fb0025778536.jpg"
        ]
    },
    {
        "path": "Bills_Payments/Utilities/Gas_ONG",
        "name": "Oklahoma Natural Gas (ONG)",
        "sources": [
            "https://www.oklahomanaturalgas.com/content/dam/centerpointenergy/images/masthead/CNP_OklahomaNaturalGas_Horizontal_RGB.svg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Oklahoma_Natural_Gas_logo.svg/1200px-Oklahoma_Natural_Gas_logo.svg.png",
            "https://www.centerpointenergy.com/images/logo.png",
            "https://energywholesale.centerpointenergy.com/content/dam/centerpointenergy/images/masthead/CNP_OklahomaNaturalGas_Horizontal_RGB.svg"
        ]
    }
]

OUT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/"
}

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def save_bytes(path, content):
    with open(path, "wb") as f:
        f.write(content)

def try_download(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image"):
            ext = "svg" if "svg" in r.headers.get("Content-Type", "") else "png"
            return r.content, ext
        print(f"      Response: {r.status_code}, Content-Type: {r.headers.get('Content-Type', '')}")
    except Exception as e:
        print(f"      Error: {e}")
    return None, None

def main():
    print("=" * 70)
    print("MISSING LOGOS FINDER - Round 2")
    print("=" * 70)
    
    found_count = 0
    
    for item in MISSING_LOGOS:
        rel_path = item["path"]
        full_dir = os.path.join(OUT_ROOT, rel_path)
        ensure_dir(full_dir)
        
        print(f"\nTrying to find: {item['name']} for {rel_path}")
        
        success = False
        for idx, url in enumerate(item["sources"], 1):
            print(f"    Attempt {idx}: {url}")
            
            # Add delay to avoid rate limiting
            time.sleep(1)
            
            data, ext = try_download(url)
            if data:
                out_file = os.path.join(full_dir, f"logo.{ext}")
                save_bytes(out_file, data)
                print(f"      ✓ SUCCESS! Downloaded logo to {out_file}")
                found_count += 1
                success = True
                break
                
        if not success:
            print(f"      ✗ FAILED: Could not download any logo for {rel_path}")
            
            # Create a placeholder file with text info for manual search
            placeholder_file = os.path.join(full_dir, "LOGO_INFO.txt")
            with open(placeholder_file, "w") as f:
                f.write(f"Please download the logo for: {item['name']}\n")
                f.write("Suggested search terms for Google Images:\n")
                if "PSO" in item["name"]:
                    f.write("- PSO Oklahoma logo\n")
                    f.write("- Public Service Company of Oklahoma logo\n")
                    f.write("- AEP PSO logo\n")
                elif "ONG" in item["name"]:
                    f.write("- Oklahoma Natural Gas logo\n")
                    f.write("- ONG utility logo\n")
                    f.write("- CenterPoint Energy Oklahoma logo\n")
            print(f"      Created info file at {placeholder_file} with search suggestions")

    print("\n" + "=" * 70)
    print(f"SUMMARY: Found {found_count} out of {len(MISSING_LOGOS)} logos in round 2")
    print("=" * 70)

if __name__ == "__main__":
    main()
