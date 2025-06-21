import os
import requests
import subprocess
import base64
import time
import random

# === CONFIGURATION ===
GITHUB_TOKEN = os.getenv("MY_PAT")
CHANNEL_ID = "UCKL5hAuzgFQsyrsQKgU0Qng"
YOUTUBE_CHANNEL_URL = f"https://www.youtube.com/channel/{CHANNEL_ID}/live"
CHANNEL_NAME_IN_M3U = "GMA 7"
GITHUB_REPO = "Jpao008/ph.m3u"
PLAYLIST_PATH = "ph.m3u"

# === USER-AGENTS ROTATION ===
USER_AGENTS = [
    # ✅ Desktop Browsers
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",

    # ✅ Mobile Browsers
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.207 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Infinix X6826) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; TECNO CH6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; vivo 1906) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",  # Samsung S24 Ultra
    "Mozilla/5.0 (Linux; Android 13; CPH2457) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.76 Mobile Safari/537.36",  # OPPO A78
    "Mozilla/5.0 (Linux; Android 14; RMX3771) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",  # realme 11 Pro+
    "Mozilla/5.0 (Linux; Android 13; SM-M536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",  # Samsung Galaxy M53 5G
    "Mozilla/5.0 (Linux; Android 12; itel S23) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.105 Mobile Safari/537.36",  # itel S23
    "Mozilla/5.0 (Linux; Android 13; Xiaomi 13T Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Infinix Zero 30 5G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",  # iPhone 15
    "Mozilla/5.0 (Linux; Android 14; ASUS_AI2205_D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",  # ROG Phone 7
    "Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; HUAWEI nova 11i) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Nokia C21 Plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.107 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; HONOR X9b) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; realme C55) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.76 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; TECNO Spark 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.78 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; WIKO T10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.185 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Samsung Galaxy A04e) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Xiaomi Redmi Note 13 5G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Infinix Smart 8 HD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; POCO M5s) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; OPPO Reno8 T 5G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1",  # iPhone SE 2022
    "Mozilla/5.0 (Linux; Android 13; Lava Blaze 5G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",

    # ✅ Bots and Special Agents
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",

    # ✅ Older Browsers
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.1",

    # ✅ Edge, Opera, Brave
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.2478.80",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/98.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.2592.61",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Safari/537.36 Edg/125.0.2535.67",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.2592.55",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.2592.80",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/102.0.4880.40",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Safari/537.36 OPR/101.0.4843.58",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/101.0.4843.33",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; ARM Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/125.0.0.0 Safari/537.36",

    # ✅ Tablets
    "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 12; Tablet; SM-T865) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",  # iPadOS 17
    "Mozilla/5.0 (iPad; CPU OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.7 Mobile/15E148 Safari/604.1",  # Older iPad
    "Mozilla/5.0 (iPad; CPU OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 13; Tablet; Lenovo TB-X606F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Lenovo Tab M10
    "Mozilla/5.0 (Android 14; Tablet; SM-X700) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Samsung Galaxy Tab S8
    "Mozilla/5.0 (Android 13; Tablet; Huawei MatePad 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Android 12; Tablet; Nokia T20) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.112 Safari/537.36",
    "Mozilla/5.0 (Android 13; Tablet; Xiaomi Pad 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; KFTRWI) AppleWebKit/537.36 (KHTML, like Gecko) Silk/102.3.1 like Chrome/102.0.5005.125 Safari/537.36",  # Fire HD 10
    "Mozilla/5.0 (Windows NT 10.0; Win64; ARM; Touch) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edge/125.0.2535.67",  # Windows Surface

    # ✅ Generic / CLI / App-based Clients
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "Mozilla/5.0 (Linux; U; Android 4.4.2; en-US; Lenovo A6000) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    "curl/8.1.2",
    "Wget/1.21.3 (linux-gnu)",
    "okhttp/4.12.0",
    "python-requests/2.31.0",
    "Go-http-client/2.0",

    # ✅ Real App Agents
    "com.ss.android.ugc.trill/321 (Linux; U; Android 13; PH; Redmi Note 11; Build/TKQ1.220829.002)",
    "Mozilla/5.0 (Linux; Android 12; PH; YouTube/18.20.36) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36",
    "FBAN/Orca-Android; FBAV/434.0.0.29.106; FBBV/400806621; FBDM/{density=3.0,width=1080,height=2340};",
    "FBAN/FBIOS;FBAV/465.0.0.37.120;FBBV/522334551;FBDV=iPhone14,2;FBMD=iPhone;FBSN=iOS;FBSV=17.4.1;FBSS=3;FBCR=Globe;FBID=phone;FBLC=en_US;",
    "Instagram 287.0.0.0.77 Android (30/11; 420dpi; 1080x2400; Xiaomi; Redmi Note 10 Pro; sweet; qcom; en_US)",
    "com.zhiliaoapp.musically/340 (Linux; U; Android 14; PH; Infinix X6826; Build/TP1A.220905.001)",
    "com.facebook.lite/400.0.0.7.104 (Android 11; Mobile; PH; 480x960; HUAWEI Y6s)",
    "YouTubeMusic/6.23.54 (Linux; U; Android 13; Xiaomi 2201116SG Build/TKQ1.221114.001)",
    "TwitterAndroid/10.20.0-release.01 (Xiaomi; Redmi Note 12; Android 13)",
    "Mozilla/5.0 (Linux; Android 12; PH; Lazada/7.30.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.98 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; PH; Shopee/3.15.2) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.61 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; PH; com.google.android.apps.youtube.music) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36",
    "okhttp/4.10.0 Shopee App/Android/13 Redmi Note 11/MIUI-14",
    "GCashAndroid/5.68.0 (Android 13; Xiaomi Redmi Note 12; Build/TKQ1.221114.001)",
    "com.netflix.mediaclient/10.2.1 build 29140 (Android 13; Xiaomi 2201116SG; PH; en-US)",
    "Spotify/8.9.30 Android/33 (Xiaomi Redmi Note 12 4G)",
    "Mozilla/5.0 (Linux; Android 13; PH; com.google.android.apps.photos) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
    "WhatsApp/2.24.12.76 Android/14 Device/SM-A546E",

    # ✅ Smart TVs / Consoles
    "Mozilla/5.0 (SMART-TV; Linux; Tizen 6.5) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0 TV Safari/537.36",
    "Mozilla/5.0 (PlayStation 5 3.00) AppleWebKit/605.1.15 (KHTML, like Gecko)",
    "Mozilla/5.0 (Xbox; Xbox One; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (SMART-TV; Tizen 7.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/5.0 TV Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SHIELD Android TV Build/RQ3A.210905.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; MiTV-MOOQ1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.125 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; BRAVIA 4K GB ATV3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Web0S; SmartTV; Linux/SmartTV) AppleWebKit/537.41 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.41 WebAppManager",
    "Mozilla/5.0 (CrKey armv7l 1.56.500000) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Chromecast
    "Mozilla/5.0 (Roku/DVP-13.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",  # Roku TV
    "AppleTV11,1/11.1 tvOS/17.5.1 model/AppleTV6,2 hw/AppleTV6,2",
    "Mozilla/5.0 (Nintendo Switch; WifiWebAuthApplet) AppleWebKit/601.6 (KHTML, like Gecko) NF/4.0.0.10.25 NintendoBrowser/5.1.0.13343",
    "Mozilla/5.0 (Linux; Android 9; Amazon AFTMM) AppleWebKit/537.36 (KHTML, like Gecko) Silk/103.2.1 like Chrome/103.0.5060.70 Safari/537.36",  # Fire TV Stick 4K
    "Mozilla/5.0 (Linux; Android 10; JVC SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Skyworth TV AOSP) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; TCL Android TV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Realme Smart TV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; Haier LE55U6900HQGA) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.65 Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def fallback_scrape_m3u8(channel_url, user_agent=None):
    headers = {
        "User-Agent": user_agent or "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1"
    }
    try:
        response = requests.get(channel_url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text

        match = re.search(r'"hlsManifestUrl":"(https:[^"]+\.m3u8[^"]*)"', html)
        if match:
            m3u8_url = match.group(1).replace("\\u0026", "&").replace("\\", "")
            print(f"✅ Fallback found M3U8: {m3u8_url}")
            return m3u8_url
        else:
            print("❌ Fallback failed: No hlsManifestUrl found.")
            return None
    except Exception as e:
        print(f"⚠️ Fallback error: {e}")
        return None

def get_youtube_live_m3u8(channel_url, retries=3):
    print(f"Checking for live stream at: {channel_url}")
    for attempt in range(retries):
        user_agent = get_random_user_agent()
        print(f"Attempt {attempt+1} using User-Agent: {user_agent}")
        try:
            result = subprocess.run(
                ['yt-dlp', '--get-url', '--user-agent', user_agent, channel_url],
                capture_output=True,
                text=True,
                timeout=20,
                check=True
            )
            for url in result.stdout.strip().split('\n'):
                if '.m3u8' in url:
                    print(f"✅ Found M3U8: {url}")
                    return url
            print("❌ No M3U8 found in yt-dlp result.")
        except subprocess.CalledProcessError:
            print("ℹ️ yt-dlp failed (possibly not live). Retrying...")
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout expired. Retrying...")
        time.sleep(random.randint(3, 8))

    print("❌ yt-dlp exhausted. Trying fallback scrape...")
    fallback_url = fallback_scrape_m3u8(channel_url, user_agent)
    return fallback_url

def update_github_file(new_m3u8_url):
    if not GITHUB_TOKEN:
        print("⚠️ GitHub token not set. Skipping update.")
        return

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PLAYLIST_PATH}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        file_data = response.json()

        current_content = base64.b64decode(file_data['content']).decode('utf-8')
        lines = current_content.splitlines()

        updated_lines = []
        found = False
        changed = False
        i = 0

        while i < len(lines):
            if lines[i].startswith("#EXTINF") and CHANNEL_NAME_IN_M3U in lines[i]:
                found = True
                updated_lines.append(lines[i])
                if i + 1 < len(lines) and lines[i + 1] != new_m3u8_url:
                    updated_lines.append(new_m3u8_url)
                    changed = True
                else:
                    updated_lines.append(lines[i + 1])
                i += 2
            else:
                updated_lines.append(lines[i])
                i += 1

        if not found:
            print(f"❌ Channel '{CHANNEL_NAME_IN_M3U}' not found.")
            return

        if not changed:
            print("ℹ️ Already up-to-date.")
            return

        new_content = "\n".join(updated_lines)
        payload = {
            "message": f"Auto-update: {CHANNEL_NAME_IN_M3U} stream refreshed",
            "content": base64.b64encode(new_content.encode()).decode(),
            "sha": file_data['sha']
        }

        put_response = requests.put(api_url, headers=headers, json=payload)
        put_response.raise_for_status()
        print("✅ GMA 7 GitHub playlist updated.")
    except requests.exceptions.RequestException as e:
        print(f"❌ GitHub update error: {e}")

# === MAIN ===
if __name__ == "__main__":
    print("--- Starting Stealth M3U8 Monitor ---")
    new_url = get_youtube_live_m3u8(YOUTUBE_CHANNEL_URL)
    if new_url:
        update_github_file(new_url)
    else:
        print("⚠️ No live stream. Nothing to update.")
    print("--- Done ---")
