import os
import base64
import requests
import yt_dlp
from googleapiclient.discovery import build
from github import Github, GithubException

# ==============================================================================
# --- START HERE: CONFIGURATION - I-SET UP ANG MGA SUMUSUNOD ---
# ==============================================================================

# --- Mga Secrets na kailangang ilagay sa GitHub Repository Settings ---
# 1. YT_API_KEY: Ang iyong YouTube Data API v3 key mula sa Google Cloud Console.
#    Pumunta sa "Settings > Secrets and variables > Actions" at i-set ito.
YT_API_KEY = os.getenv("YT_API_KEY")

# 2. GITHUB_TOKEN: Ang iyong GitHub Personal Access Token na may 'repo' scope.
#    I-set din ito sa "Settings > Secrets and variables > Actions".
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# --- Mga values na maaaring palitan direkta dito kung gusto mo ---
# 3. CHANNEL_ID: Ito ang ID ng YouTube channel na susubaybayan.
#    (UCbLgT2NVE9xT-D_4-t-H25g ay para sa GMA Network)
#    Palitan mo ito kung ibang channel ang target mo.
CHANNEL_ID = "UCKL5hAuzgFQsyrsQKgU0Qng"

# 4. CHANNEL_NAME_IN_M3U: Ang eksaktong pangalan ng channel na nakasulat sa
#    iyong .m3u file. Ito ay case-sensitive.
CHANNEL_NAME_IN_M3U = "GMA 7"

# --- Mga values na awtomatikong kinukuha mula sa GitHub Actions (karaniwang hindi na kailangang baguhin) ---
# GITHUB_REPO: Pangalan ng iyong repository (e.g., "Jpao008/ph.m3u"). Awtomatikong mase-set ito ng workflow.
GITHUB_REPO = os.getenv("GITHUB_REPO")

# PLAYLIST_PATH: Path ng iyong file sa loob ng repository.
PLAYLIST_PATH = os.getenv("PLAYLIST_PATH", "ph.m3u")


# ==============================================================================
# --- END OF CONFIGURATION - HUWAG NANG BAGUHIN ANG CODE SA IBABA NITO ---
# ==============================================================================


def get_live_video_id():
    """Finds the video ID of the current live stream on the channel."""
    if not YT_API_KEY:
        print("Error: YouTube API Key (YT_API_KEY) is not set in GitHub Secrets.")
        return None
    try:
        print(f"Searching for live video on channel ID: {CHANNEL_ID}")
        youtube = build("youtube", "v3", developerKey=YT_API_KEY)
        request = youtube.search().list(
            part="id",
            channelId=CHANNEL_ID,
            eventType="live",
            type="video",
            maxResults=1
        )
        response = request.execute()
        items = response.get("items", [])
        if items:
            video_id = items[0]["id"]["videoId"]
            print(f"Found live video ID: {video_id}")
            return video_id
        else:
            print("Channel is not currently live.")
            return None
    except Exception as e:
        print(f"An error occurred while calling YouTube API: {e}")
        return None


def get_m3u8_url(video_id):
    """Extracts the .m3u8 manifest URL from a given video ID using yt-dlp."""
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Extracting M3U8 URL for video: {video_url}")
    ydl_opts = {
        'quiet': True,
        'forcejson': True,  # Don't download, just get info
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            for f in info.get('formats', []):
                # We look for the native HLS manifest
                if f.get('protocol') == 'm3u8_native':
                    print(f"Successfully found M3U8 URL: {f['url']}")
                    return f['url']
        print("Error: M3U8 manifest URL not found in video formats.")
        return None
    except Exception as e:
        print(f"An error occurred during yt-dlp extraction: {e}")
        return None


def update_github_playlist(new_url):
    """Updates the playlist file on GitHub if the URL has changed."""
    if not GITHUB_TOKEN:
        print("Error: GitHub Token is not set in GitHub Secrets.")
        return
    if not GITHUB_REPO:
        print("Error: GITHUB_REPO variable is not set.")
        return

    try:
        print(f"Connecting to GitHub repository: {GITHUB_REPO}")
        gh = Github(GITHUB_TOKEN)
        repo = gh.get_repo(GITHUB_REPO)

        print(f"Getting contents of file: {PLAYLIST_PATH}")
        file_contents = repo.get_contents(PLAYLIST_PATH)

        current_content = base64.b64decode(file_contents.content).decode('utf-8')
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
                    old_url = lines[i + 1]
                    updated_lines.append(line)
                    if old_url != new_url:
                        print(f"URL is different. Updating URL for {CHANNEL_NAME_IN_M3U}.")
                        updated_lines.append(new_url)
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
            print(f"Error: Channel '{CHANNEL_NAME_IN_M3U}' not found in the M3U8 file. No changes made.")
            return

        if not content_changed:
            print("URL is already up-to-date. No changes needed.")
            return

        new_content = "\n".join(updated_lines)
        commit_message = f"Auto-update: Refresh {CHANNEL_NAME_IN_M3U} stream link"

        print("Pushing updated file to GitHub...")
        repo.update_file(
            file_contents.path,
            commit_message,
            new_content,
            file_contents.sha
        )
        print("✅ Successfully updated the playlist on GitHub.")

    except GithubException as e:
        print(f"A GitHub error occurred: {e.status} {e.data}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    print("--- Starting M3U8 Update Script ---")
    live_video_id = get_live_video_id()
    if live_video_id:
        m3u8_link = get_m3u8_url(live_video_id)
        if m3u8_link:
            update_github_playlist(m3u8_link)
    else:
        print("Could not retrieve a new M3U8 link. Update process will not run.")
    print("--- Script finished ---")

