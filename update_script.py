import os
import requests
import subprocess
import base64

# ==============================================================================
# --- START HERE: CONFIGURATION - I-SET UP ANG MGA SUMUSUNOD ---
# ==============================================================================

# 1. GITHUB_TOKEN: Siguraduhing mayroon ka nito sa iyong GitHub Secrets.
#    Ang pangalan ng secret ay dapat "GITHUB_TOKEN".
#    Ito ang iyong GitHub Personal Access Token na may 'repo' scope.
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 2. CHANNEL_ID: Palitan ito ng ID ng YouTube channel na gusto mong subaybayan.
#    Maaari kang maghanap online ng "how to find youtube channel id" para makuha ito.
#    Halimbawa: "UCBi2mrWuNuyYy4gbM6fU18Q" (Raffy Tulfo in Action)
CHANNEL_ID = "UCBi2mrWuNuyYy4gbM6fU18Q" 
YOUTUBE_CHANNEL_URL = f"https://www.youtube.com/channel/{CHANNEL_ID}/live"

# 3. CHANNEL_NAME_IN_M3U: Palitan ito ng eksaktong pangalan ng channel
#    na nakasulat sa iyong .m3u file. (Case-sensitive ito).
CHANNEL_NAME_IN_M3U = "GMA 7" # Palitan mo ito kung kinakailangan

# --- Mga values na awtomatikong kinukuha mula sa GitHub Actions ---
# Hindi mo na kailangang baguhin ang mga ito kung tama ang iyong workflow file.
GITHUB_REPO = os.getenv("GITHUB_REPO")
PLAYLIST_PATH = os.getenv("PLAYLIST_PATH", "ph.m3u")

# ==============================================================================
# --- END OF CONFIGURATION - HUWAG NANG BAGUHIN ANG CODE SA IBABA NITO ---
# ==============================================================================


def get_youtube_live_m3u8(channel_url):
    """
    Ito ang AUTOMATIC CHECK.
    Direktang kinukuha ang live M3U8 URL. Kung hindi live ang channel,
    magkakaroon ito ng error, at hihinto ang script para sa run na ito.
    """
    print(f"Automatically checking for live stream at: {channel_url}")
    
    # User-Agent para magpanggap na isang totoong browser.
    # Ito ay para subukang iwasan ang "confirm you're not a bot" error.
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    
    try:
        # Idinagdag ang --user-agent sa command.
        result = subprocess.run(
            ['yt-dlp', '--get-url', '--user-agent', user_agent, channel_url],
            capture_output=True,
            text=True,
            check=True
        )
        # Kung may nakuha, ibig sabihin ay LIVE.
        for url in result.stdout.strip().split('\n'):
            if '.m3u8' in url:
                print(f"✅ Live stream found! URL: {url}")
                return url
        print("❌ Live stream link (M3U8) not found in the output.")
        return None
    except subprocess.CalledProcessError as e:
        # Kung pumasok dito, ibig sabihin HINDI LIVE o may ibang error.
        print(f"ℹ️  Channel is likely not live or is blocked. Details: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("CRITICAL ERROR: yt-dlp is not installed in the environment.")
        return None


def update_github_file(new_m3u8_url):
    """
    Ia-update ang playlist file sa GitHub kung may nahanap na bagong URL.
    """
    if not GITHUB_TOKEN:
        print("Error: GitHub token is not set. Cannot update file.")
        return

    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PLAYLIST_PATH}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Ititigil kung may error tulad ng 404
        file_data = response.json()

        current_content = base64.b64decode(file_data['content']).decode('utf-8')
        lines = current_content.splitlines()
        
        updated_lines = []
        found_channel = False
        content_changed = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.strip().startswith("#EXTINF") and CHANNEL_NAME_IN_M3U in line:
                found_channel = True
                if i + 1 < len(lines):
                    old_url = lines[i+1]
                    updated_lines.append(line)
                    if old_url != new_m3u8_url:
                        print(f"URL is different. Updating URL for '{CHANNEL_NAME_IN_M3U}'.")
                        updated_lines.append(new_m3u8_url)
                        content_changed = True
                    else:
                        updated_lines.append(old_url)
                    i += 2
                else:
                    updated_lines.append(line)
                    i += 1
            else:
                updated_lines.append(line)
                i += 1

        if not found_channel:
            print(f"Error: Channel '{CHANNEL_NAME_IN_M3U}' not found in the M3U8 file.")
            return

        if not content_changed:
            print("URL is already up-to-date. No update needed.")
            return

        new_content = "\n".join(updated_lines)
        payload = {
            "message": f"Auto-update: Refresh {CHANNEL_NAME_IN_M3U} stream link",
            "content": base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
            "sha": file_data['sha']
        }
        
        update_response = requests.put(api_url, headers=headers, json=payload)
        update_response.raise_for_status()
        print("✅ Successfully updated the playlist on GitHub.")

    except requests.exceptions.HTTPError as e:
        print(f"An error occurred with GitHub API request: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    print("--- Starting M3U8 Update Script (Direct Method with User-Agent) ---")
    new_url = get_youtube_live_m3u8(YOUTUBE_CHANNEL_URL)
    if new_url:
        update_github_file(new_url)
    else:
        print("No new link found. Update process finished for this run.")
    print("--- Script finished ---")
