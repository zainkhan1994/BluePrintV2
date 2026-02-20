import os
import re
import requests
from pathlib import Path

COMPANIES = [
    ("Accounts_Banking/Bank_of_America", "bankofamerica.com", "bankofamerica"),
    ("Accounts_Banking/Wells_Fargo", "wellsfargo.com", "wellsfargo"),
    ("Accounts_Banking/Chase", "chase.com", "chase"),
    ("Accounts_Banking/American_Express", "americanexpress.com", "americanexpress"),
    ("Accounts_Banking/Other_Cards/Credit_One", "creditonebank.com", "creditone"),
    ("Accounts_Banking/Other_Cards/Indigo", "indigocard.com", "indigocard"),
    ("Accounts_Banking/Other_Cards/Nordstrom", "nordstrom.com", "nordstrom"),
    ("Accounts_Banking/Other_Cards/Synchrony", "synchrony.com", "synchrony"),
    ("Bills_Payments/Car_HondaFS", "hondafinancialservices.com", "honda"),
    ("Bills_Payments/Utilities/Water_Minol", "minol.com", "minol"),
    ("Bills_Payments/Utilities/Electric_PSO", "psoenergia.com", "pso"),
    ("Bills_Payments/Utilities/Gas_ONG", "ong.com.ar", "ong"),
    ("Bills_Payments/Phone_ATT", "att.com", "att"),
    ("Bills_Payments/Insurance_Allstate", "allstate.com", "allstate"),
    ("Credit_Debt/Loans/HondaFS", "hondafinancialservices.com", "honda"),
    ("Credit_Debt/Loans/Citizens_Apple", "citizensbank.com", "citizensbank"),
    ("Credit_Debt/Credit_Repair/Lexington_Law", "lexingtonlaw.com", "lexingtonlaw"),
    ("Refunds_Service_Logs/Walmart", "walmart.com", "walmart"),
    ("Refunds_Service_Logs/Target", "target.com", "target"),
    ("Refunds_Service_Logs/AT&T", "att.com", "att"),
    ("Refunds_Service_Logs/Apple", "apple.com", "apple"),
    ("Refunds_Service_Logs/Nike_Ross_HandAndStone/Nike", "nike.com", "nike"),
    ("Refunds_Service_Logs/Nike_Ross_HandAndStone/Ross", "rossstores.com", "rossstores"),
    ("Financial_Tools/RocketMoney", "rocketmoney.com", "rocketmoney"),
    ("Financial_Tools/Plaid", "plaid.com", "plaid"),
    ("Financial_Tools/Zelle", "zellepay.com", "zelle"),
    ("Financial_Tools/PayPal", "paypal.com", "paypal"),
    ("Financial_Tools/Venmo", "venmo.com", "venmo"),
    ("Financial_Tools/CashApp", "cash.app", "cashapp"),
    ("Financial_Tools/SquareUp", "squareup.com", "square"),
    ("Assets_Inventory/Electronics/MacBook", "apple.com", "apple"),
    ("Assets_Inventory/Electronics/iPhone15", "apple.com", "apple"),
    ("Assets_Inventory/Electronics/Apple_Watch", "apple.com", "apple"),
    ("Timeline/Travel/Emirates", "emirates.com", "emirates"),
    ("Timeline/Travel/Delta", "delta.com", "delta"),
    ("Timeline/Travel/United", "united.com", "united"),
    ("Timeline/Travel/Airbnb", "airbnb.com", "airbnb"),
    ("Daily_Life_Digital_Presence/Email_Accounts/Apple_IDs", "apple.com", "apple"),
    ("Daily_Life_Digital_Presence/Email_Accounts/Gmail", "google.com", "gmail"),
    ("Daily_Life_Digital_Presence/Email_Accounts/Outlook", "outlook.com", "microsoft"),
    ("Daily_Life_Digital_Presence/Email_Accounts/Yahoo", "yahoo.com", "yahoo"),
    ("Daily_Life_Digital_Presence/Social_Media/Instagram", "instagram.com", "instagram"),
    ("Daily_Life_Digital_Presence/Social_Media/TikTok", "tiktok.com", "tiktok"),
    ("Daily_Life_Digital_Presence/Social_Media/Facebook", "facebook.com", "facebook"),
    ("Daily_Life_Digital_Presence/Social_Media/LinkedIn", "linkedin.com", "linkedin"),
    ("Daily_Life_Digital_Presence/Social_Media/Snapchat", "snapchat.com", "snapchat"),
    ("Daily_Life_Digital_Presence/Shopping/Amazon", "amazon.com", "amazon"),
    ("Daily_Life_Digital_Presence/Shopping/Walmart", "walmart.com", "walmart"),
    ("Daily_Life_Digital_Presence/Shopping/Target", "target.com", "target"),
    ("Daily_Life_Digital_Presence/Shopping/BestBuy", "bestbuy.com", "bestbuy"),
    ("Daily_Life_Digital_Presence/Shopping/Costco", "costco.com", "costco"),
    ("Daily_Life_Digital_Presence/Entertainment/AMC", "amctheatres.com", "amctheatres"),
    ("Daily_Life_Digital_Presence/Entertainment/Netflix", "netflix.com", "netflix"),
    ("Daily_Life_Digital_Presence/Entertainment/Hulu", "hulu.com", "hulu"),
    ("Daily_Life_Digital_Presence/Entertainment/Crunchyroll", "crunchyroll.com", "crunchyroll"),
    ("Daily_Life_Digital_Presence/Entertainment/DisneyPlus", "disneyplus.com", "disneyplus"),
    ("Daily_Life_Digital_Presence/Entertainment/HBO_Max", "hbomax.com", "hbomax"),
]

OUT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def try_clearbit(domain):
    try:
        url = f"https://logo.clearbit.com/{domain}?size=256"
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image"):
            return r.content, "png"
    except Exception as e:
        pass
    return None, None

def try_simpleicons(slug):
    try:
        url = f"https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/{slug}.svg"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.content, "svg"
    except Exception as e:
        pass
    return None, None

def save_bytes(path, content):
    with open(path, "wb") as f:
        f.write(content)

def main():
    found = []
    not_found = []
    
    print("=" * 70)
    print("LOGO DOWNLOADER - Starting fetch...")
    print("=" * 70)
    
    for idx, (rel_path, domain, slug) in enumerate(COMPANIES, 1):
        full_dir = os.path.join(OUT_ROOT, rel_path)
        ensure_dir(full_dir)
        
        company_name = rel_path.split("/")[-1]
        print(f"\n[{idx}/{len(COMPANIES)}] {company_name}")
        
        # Try Clearbit first (PNG)
        data, ext = try_clearbit(domain)
        if data:
            out_file = os.path.join(full_dir, f"logo.png")
            save_bytes(out_file, data)
            print(f"     ✓ Downloaded from Clearbit (PNG)")
            found.append(rel_path)
            continue
        
        # Try Simple Icons (SVG)
        data, ext = try_simpleicons(slug)
        if data:
            out_file = os.path.join(full_dir, f"logo.svg")
            save_bytes(out_file, data)
            print(f"     ✓ Downloaded from Simple Icons (SVG)")
            found.append(rel_path)
            continue
        
        print(f"     ✗ NOT FOUND - Manual sourcing needed")
        not_found.append(rel_path)
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {len(found)} logos downloaded, {len(not_found)} need manual sourcing")
    print("=" * 70)
    
    if found:
        print(f"\n✓ Successfully downloaded ({len(found)}):")
        for item in found:
            print(f"   {item}")
    
    if not_found:
        print(f"\n✗ Manual sourcing needed ({len(not_found)}):")
        for item in not_found:
            print(f"   {item}")

if __name__ == "__main__":
    main()
