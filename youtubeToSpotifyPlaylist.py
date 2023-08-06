import os 
import re 
import google_auth_oauthlib.flow 
import googleapiclient.discovery 
import spotipy 
import spotipy.util as util 
 
# Replace with your own API keys 
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY" 
SPOTIPY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID" 
SPOTIPY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET" 
SPOTIPY_REDIRECT_URI = "YOUR_SPOTIFY_REDIRECT_URI"  # For example, "http://localhost:8888/callback" 
 
# YouTube playlist ID, extract it from the playlist URL 
YOUTUBE_PLAYLIST_ID = "YOUR_YOUTUBE_PLAYLIST_ID" 
 
# Function to authenticate with YouTube Data API 
def youtube_authenticate(): 
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"] 
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file( 
        "client_secrets.json", scopes 
    ) 
    credentials = flow.run_console() 
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials) 
    return youtube 
 
# Function to fetch YouTube playlist items 
def get_youtube_playlist_items(youtube, playlist_id): 
    request = youtube.playlistItems().list( 
        part="snippet", 
        playlistId=playlist_id, 
        maxResults=50, 
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
        username="YOUR_SPOTIFY_USERNAME", 
        scope="playlist-modify-public", 
        client_id=SPOTIPY_CLIENT_ID, 
        client_secret=SPOTIPY_CLIENT_SECRET, 
        redirect_uri=SPOTIPY_REDIRECT_URI, 
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
 
def main(): 
    # YouTube authentication 
    youtube = youtube_authenticate() 
    youtube_playlist_items = get_youtube_playlist_items(youtube, YOUTUBE_PLAYLIST_ID) 
    video_ids = get_video_ids(youtube_playlist_items) 
 
    # Spotify authentication 
    sp = spotify_authenticate() 
 
    # Create a new Spotify playlist with the same name as the YouTube playlist 
    youtube_playlist_name = youtube_playlist_items[0]["snippet"]["playlistTitle"] 
    spotify_playlist_id = create_spotify_playlist(sp, youtube_playlist_name) 
 
    # Convert YouTube video IDs to Spotify track IDs and add them to the playlist 
    for video_id in video_ids: 
        youtube_url = f"https://www.youtube.com/watch?v={video_id}" 
        track_name = ( 
            youtube.playlistItems().list(part="snippet", id=video_id) 
            .execute()["items"][0]["snippet"]["title"] 
        ) 
        track_name = re.sub(r"\([^)]*\)", "", track_name).strip()  # Remove parenthesis and their contents 
        track_id = get_spotify_track_id(sp, track_name) 
        if track_id: 
            add_tracks_to_spotify_playlist(sp, spotify_playlist_id, [track_id]) 
        else: 
            print(f"Could not find {track_name} on Spotify.") 
 
    print("Playlist successfully created on Spotify.") 
 
if name == "__main__": 
    main()