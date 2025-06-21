import os
import requests
import subprocess
import base64
import time
import random

# === CONFIGURATION ===
GITHUB_TOKEN = os.getenv("MY_PAT")  # Use GitHub Actions secrets
CHANNEL_ID = "UCKL5hAuzgFQsyrsQKgU0Qng"
YOUTUBE_CHANNEL_URL = f"https://www.youtube.com/channel/{CHANNEL_ID}/live"
CHANNEL_NAME_IN_M3U = "GMA 7"
GITHUB_REPO = "Jpao008/ph.m3u"
PLAYLIST_PATH = "ph.m3u"

# === USER-AGENTS ROTATION ===
USER_AGENTS = [
    # Desktop Browsers
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",

    # Mobile Browsers
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.207 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",

    # Bots and Special Agents (some sites treat these as normal)
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",

    # Older Browsers (sometimes helps)
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.1",

    # Edge, Opera, Brave
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.2478.80",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/98.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/124.0.0.0 Safari/537.36",

    # Tablets
    "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 12; Tablet; SM-T865) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",

    # Generic
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "Mozilla/5.0 (Linux; U; Android 4.4.2; en-US; Lenovo A6000) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
]


def get_random_user_agent():
    return random.choice(USER_AGENTS)

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
            print("❌ No M3U8 found.")
            return None
        except subprocess.CalledProcessError:
            print("ℹ️ yt-dlp failed (possibly not live). Retrying...")
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout expired. Retrying...")
        time.sleep(random.randint(3, 8))
    return None

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
        print("✅ GitHub playlist updated.")
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
