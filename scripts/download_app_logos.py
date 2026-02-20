import os
import requests
from pathlib import Path
import time
import re

# List of apps and their domains/search terms
APPS = [
    # Social & Community - Direct Messaging
    ("Social_Community/Direct_Messaging/iMessage", "apple.com", "apple"),
    ("Social_Community/Direct_Messaging/FaceTime", "apple.com", "facetime"),
    ("Social_Community/Direct_Messaging/TextMe", "go-text.me", "textme"),
    ("Social_Community/Direct_Messaging/TextFree", "textfree.us", "textfree"),
    ("Social_Community/Direct_Messaging/WhatsApp", "whatsapp.com", "whatsapp"),
    ("Social_Community/Direct_Messaging/Facebook_Messenger", "messenger.com", "messenger"),
    ("Social_Community/Direct_Messaging/Discord", "discord.com", "discord"),
    ("Social_Community/Direct_Messaging/Slack", "slack.com", "slack"),
    
    # Social & Community - Communities & Groups
    ("Social_Community/Communities_Groups/Skool", "skool.com", "skool"),
    ("Social_Community/Communities_Groups/Mighty", "mightynetworks.com", "mighty"),
    ("Social_Community/Communities_Groups/Reddit", "reddit.com", "reddit"),
    ("Social_Community/Communities_Groups/Meetup", "meetup.com", "meetup"),
    ("Social_Community/Communities_Groups/Eventbrite", "eventbrite.com", "eventbrite"),
    ("Social_Community/Communities_Groups/LinkedIn_Events", "linkedin.com", "linkedin"),
    ("Social_Community/Communities_Groups/Meta_Events", "meta.com", "meta"),
    ("Social_Community/Communities_Groups/Faves", "faves.com", "faves"),
    
    # Social & Community - Social Media
    ("Social_Community/Social_Media/Instagram", "instagram.com", "instagram"),
    ("Social_Community/Social_Media/TikTok", "tiktok.com", "tiktok"),
    ("Social_Community/Social_Media/Snapchat", "snapchat.com", "snapchat"),
    ("Social_Community/Social_Media/Facebook", "facebook.com", "facebook"),
    ("Social_Community/Social_Media/YouTube", "youtube.com", "youtube"),
    ("Social_Community/Social_Media/Threads", "threads.net", "threads"),
    
    # Productivity & Organization - Planning & Notes
    ("Productivity_Organization/Planning_Notes/Notion", "notion.so", "notion"),
    ("Productivity_Organization/Planning_Notes/Obsidian", "obsidian.md", "obsidian"),
    ("Productivity_Organization/Planning_Notes/Apple_Notes", "apple.com", "applenotes"),
    ("Productivity_Organization/Planning_Notes/Google_Tasks", "google.com", "googletasks"),
    ("Productivity_Organization/Planning_Notes/Reminders", "apple.com", "applereminders"),
    ("Productivity_Organization/Planning_Notes/Calendar", "apple.com", "applecalendar"),
    
    # Productivity & Organization - Project Management
    ("Productivity_Organization/Project_Management/Asana", "asana.com", "asana"),
    ("Productivity_Organization/Project_Management/Miro", "miro.com", "miro"),
    ("Productivity_Organization/Project_Management/GitHub", "github.com", "github"),
    ("Productivity_Organization/Project_Management/Google_Cloud", "cloud.google.com", "googlecloud"),
    
    # Productivity & Organization - Automation & Tools
    ("Productivity_Organization/Automation_Tools/IFTTT", "ifttt.com", "ifttt"),
    ("Productivity_Organization/Automation_Tools/Shortcuts", "apple.com", "shortcuts"),
    ("Productivity_Organization/Automation_Tools/Scriptable", "scriptable.app", "scriptable"),
    ("Productivity_Organization/Automation_Tools/Pythonista", "omz-software.com", "pythonista"),
    ("Productivity_Organization/Automation_Tools/Fireflies", "fireflies.ai", "fireflies"),
    
    # Finance & Payments
    ("Finance_Payments/Cash_App", "cash.app", "cashapp"),
    ("Finance_Payments/Venmo", "venmo.com", "venmo"),
    ("Finance_Payments/PayPal", "paypal.com", "paypal"),
    ("Finance_Payments/Rocket_Money", "rocketmoney.com", "rocketmoney"),
    ("Finance_Payments/Acorns", "acorns.com", "acorns"),
    ("Finance_Payments/Wells_Fargo", "wellsfargo.com", "wellsfargo"),
    ("Finance_Payments/Bank_of_America", "bankofamerica.com", "bankofamerica"),
    ("Finance_Payments/Western_Union", "westernunion.com", "westernunion"),
    ("Finance_Payments/Zelle", "zellepay.com", "zelle"),
    ("Finance_Payments/Plaid", "plaid.com", "plaid"),
    ("Finance_Payments/SquareUp", "squareup.com", "square"),
    
    # Shopping & Rewards - Retail
    ("Shopping_Rewards/Retail/Amazon", "amazon.com", "amazon"),
    ("Shopping_Rewards/Retail/Walmart", "walmart.com", "walmart"),
    ("Shopping_Rewards/Retail/Target", "target.com", "target"),
    ("Shopping_Rewards/Retail/Lowes", "lowes.com", "lowes"),
    ("Shopping_Rewards/Retail/Home_Depot", "homedepot.com", "homedepot"),
    ("Shopping_Rewards/Retail/Office_Depot", "officedepot.com", "officedepot"),
    ("Shopping_Rewards/Retail/eBay", "ebay.com", "ebay"),
    ("Shopping_Rewards/Retail/Temu", "temu.com", "temu"),
    ("Shopping_Rewards/Retail/Etsy", "etsy.com", "etsy"),
    
    # Shopping & Rewards - Food & Coffee
    ("Shopping_Rewards/Food_Coffee/Chick-fil-A", "chick-fil-a.com", "chickfila"),
    ("Shopping_Rewards/Food_Coffee/Dutch_Bros", "dutchbros.com", "dutchbros"),
    ("Shopping_Rewards/Food_Coffee/Starbucks", "starbucks.com", "starbucks"),
    ("Shopping_Rewards/Food_Coffee/DoorDash", "doordash.com", "doordash"),
    ("Shopping_Rewards/Food_Coffee/Uber_Eats", "ubereats.com", "ubereats"),
    
    # Shopping & Rewards - Shipping & Tracking
    ("Shopping_Rewards/Shipping_Tracking/UPS", "ups.com", "ups"),
    ("Shopping_Rewards/Shipping_Tracking/FedEx", "fedex.com", "fedex"),
    ("Shopping_Rewards/Shipping_Tracking/USPS_Mobile", "usps.com", "usps"),
    
    # Navigation & Travel - Maps & Transport
    ("Navigation_Travel/Maps_Transport/Google_Maps", "maps.google.com", "googlemaps"),
    ("Navigation_Travel/Maps_Transport/Apple_Maps", "apple.com", "applemaps"),
    ("Navigation_Travel/Maps_Transport/Yandex_Maps", "yandex.com", "yandexmaps"),
    ("Navigation_Travel/Maps_Transport/ParkMobile", "parkmobile.io", "parkmobile"),
    ("Navigation_Travel/Maps_Transport/Uber", "uber.com", "uber"),
    ("Navigation_Travel/Maps_Transport/Lyft", "lyft.com", "lyft"),
    
    # Navigation & Travel - Housing & Weather
    ("Navigation_Travel/Housing_Weather/Apartments_App", "apartments.com", "apartments"),
    ("Navigation_Travel/Housing_Weather/Weather", "weather.gov", "weather"),
    
    # Health & Fitness
    ("Health_Fitness/MyChart", "mychart.com", "mychart"),
    ("Health_Fitness/BetterSleep", "bettersleep.com", "bettersleep"),
    ("Health_Fitness/PT_Solutions", "ptsolutions.com", "ptsolutions"),
    ("Health_Fitness/Noji", "noji.com", "noji"),
    ("Health_Fitness/Healow", "healow.com", "healow"),
    ("Health_Fitness/Life_Time", "lifetime.life", "lifetime"),
    ("Health_Fitness/Weight_Gurus", "weightgurus.com", "weightgurus"),
    ("Health_Fitness/Go_Kinetic", "gokinetic.com", "gokinetic"),
    ("Health_Fitness/Elevate", "elevateapp.com", "elevate"),
    ("Health_Fitness/Think_Dirty", "thinkdirtyapp.com", "thinkdirty"),
    
    # Learning & Self-Improvement
    ("Learning_Self-Improvement/Duolingo", "duolingo.com", "duolingo"),
    ("Learning_Self-Improvement/Mimo", "getmimo.com", "mimo"),
    ("Learning_Self-Improvement/Brilliant", "brilliant.org", "brilliant"),
    ("Learning_Self-Improvement/Quizgecko", "quizgecko.com", "quizgecko"),
    ("Learning_Self-Improvement/Information_Reading", "pocket.com", "pocket"),
    
    # Entertainment & Media - Streaming
    ("Entertainment_Media/Streaming/Netflix", "netflix.com", "netflix"),
    ("Entertainment_Media/Streaming/Hulu", "hulu.com", "hulu"),
    ("Entertainment_Media/Streaming/Max", "max.com", "hbomax"),
    ("Entertainment_Media/Streaming/Prime_Video", "primevideo.com", "amazonprimevideo"),
    ("Entertainment_Media/Streaming/Disney_Plus", "disneyplus.com", "disneyplus"),
    ("Entertainment_Media/Streaming/Crunchyroll", "crunchyroll.com", "crunchyroll"),
    ("Entertainment_Media/Streaming/YouTube", "youtube.com", "youtube"),
    
    # Entertainment & Media - Devices & Control
    ("Entertainment_Media/Devices_Control/VIZIO", "vizio.com", "vizio"),
    ("Entertainment_Media/Devices_Control/Apple_TV_Remote", "apple.com", "appletvremote"),
    
    # AI & Knowledge Tools
    ("AI_Knowledge_Tools/ChatGPT", "openai.com", "openai"),
    ("AI_Knowledge_Tools/Claude", "anthropic.com", "claude"),
    ("AI_Knowledge_Tools/Perplexity", "perplexity.ai", "perplexity"),
    ("AI_Knowledge_Tools/Rewind", "rewind.ai", "rewind"),
]

OUT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__))))
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def save_bytes(path, content):
    with open(path, "wb") as f:
        f.write(content)

def sanitize_path(path):
    # Replace characters that might cause issues in folder names
    path = path.replace("&", "and")
    return path

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

def main():
    print("=" * 70)
    print("APP LOGO DOWNLOADER - Starting fetch...")
    print("=" * 70)
    
    found = []
    not_found = []
    
    for idx, (rel_path, domain, slug) in enumerate(APPS, 1):
        # Sanitize path to avoid issues with special characters
        safe_path = sanitize_path(rel_path)
        full_dir = os.path.join(OUT_ROOT, safe_path)
        ensure_dir(full_dir)
        
        app_name = rel_path.split("/")[-1]
        print(f"\n[{idx}/{len(APPS)}] {app_name}")
        
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
            
        # If we got here, both attempts failed
        print(f"     ✗ NOT FOUND - {domain}")
        not_found.append(rel_path)
        
        # Add a small delay to avoid hitting rate limits
        time.sleep(0.5)
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {len(found)} app logos downloaded, {len(not_found)} not found")
    print("=" * 70)
    
    if found:
        print(f"\n✓ Successfully downloaded ({len(found)}):")
        for item in sorted(found):
            print(f"   {item}")
    
    if not_found:
        print(f"\n✗ Not found ({len(not_found)}):")
        for item in sorted(not_found):
            print(f"   {item}")

if __name__ == "__main__":
    main()
