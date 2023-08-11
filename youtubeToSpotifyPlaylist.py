import os
import re
import google_auth_oauthlib.flow
import googleapiclient.discovery
import spotipy
import spotipy.util as util
from dotenv import load_dotenv

load_dotenv()

# Import API keys from env file
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID") # user id
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET") # access token
spotify_redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

#test
# print("secrets:")
# print("youtube_api_key: " + youtube_api_key)
# print("spotify_client_id: " + spotify_client_id)
# print("spotify_client_secret: "+ spotify_client_secret)
# print("spotify_redirect_uri: " + spotify_redirect_uri)

# YouTube playlist ID, extract it from the playlist URL
youtube_playlist_id = os.getenv("YOUTUBE_PLAYLIST_ID")

# Function to authenticate with YouTube Data API
def youtube_authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secret_204729676666_k2c2b39cbui38s3uj1snrif19cci17c3_apps.json", scopes
    )
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    return youtube

# Function to fetch YouTube playlist items
def get_youtube_playlist_items(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=1000
    )
    response = request.execute()
    return response["items"]

# Function to extract video IDs from YouTube playlist items
def get_video_ids(youtube_items):
    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in youtube_items]
    return video_ids

# Function to authenticate with Spotify API
def spotify_authenticate():
    token = util.prompt_for_user_token(
        username="iouvzoi4qjplgohvy5dhkjb8y", # username
        scope="playlist-modify-public", #permissions
        client_id=spotify_client_id,
        client_secret=spotify_client_secret,
        redirect_uri=spotify_redirect_uri,
    )
    sp = spotipy.Spotify(auth=token)
    return sp

# Function to search for a track on Spotify and return its ID
def get_spotify_track_id(sp, track_name):
    results = sp.search(q=track_name, type="track", limit=1)
    if results["tracks"]["items"]:
        return results["tracks"]["items"][0]["id"]
    return None

# Function to create a new Spotify playlist
def create_spotify_playlist(sp, playlist_name):
    user_id = sp.me()["id"]
    playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
    return playlist["id"]

# Function to add tracks to a Spotify playlist
def add_tracks_to_spotify_playlist(sp, playlist_id, track_ids):
    sp.user_playlist_add_tracks(
        sp.me()["id"], playlist_id=playlist_id, tracks=track_ids
    )


#---------------testing---------------#
    
def manage_results_file(filename, video_ids):

    # Create results file
    with open(filename, "w+") as f:
        for video in video_ids:
            f.write(video + "\n")

    # Checking repeated elements in results file
        seen = set()
        repeated_videos = []

        with open('results.txt') as f:
            for line in f:
                line_check = line.strip().lower()
                if line_check in seen:
                    repeated_videos.append(line.strip())
                else:
                    seen.add(line_check)

        # Print repeated videos
        if repeated_videos:
            print("Repeated videos:")
            for video in repeated_videos:
                print(video)
        else:
            print("No repeated videos found.")

    #---------------testing---------------#


def main():
    filename_results = "results.txt"
    # YouTube authentication
    youtube = youtube_authenticate()
    youtube_playlist_items = get_youtube_playlist_items(youtube, youtube_playlist_id)
    # print(youtube_playlist_items)
    video_ids = get_video_ids(youtube_playlist_items)
    manage_results_file(filename_results,video_ids)
    print(video_ids)

    # Spotify authentication
    sp = spotify_authenticate()

    # Create a new Spotify playlist with the same name as the YouTube playlist
    youtube_playlist_name = youtube_playlist_items[0]["snippet"]["title"]
    spotify_playlist_id = create_spotify_playlist(sp, youtube_playlist_name)

    #tracks not found
    filename_errors = "errors.txt"

    # Convert YouTube video IDs to Spotify track IDs and add them to the playlist
    playlist_items = youtube.playlistItems().list(part="snippet", playlistId=youtube_playlist_id).execute()
    for item in playlist_items["items"]:
        track_name = item["snippet"]["title"]
        track_name = re.sub(r"\([^)]*\)", "", track_name).strip()
        print(track_name + " succesfully added")
        track_id = get_spotify_track_id(sp, track_name)
        if track_id:
            add_tracks_to_spotify_playlist(sp, spotify_playlist_id, [track_id])
        else:
            print(f"Could not find {track_name} on Spotify.")

    print("Playlist successfully created on Spotify.")

if __name__ == "__main__":
    main()