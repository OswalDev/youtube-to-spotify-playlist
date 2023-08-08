import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Replace these with your actual client ID and client secret
client_id = "2e21bc67c2d24c67ba71615295b77cdf"
client_secret = "93b778f4273343a2be42921f1565cdcd"

# Replace "YOUR_REDIRECT_URI" with the actual redirect URI you want to use
redirect_uri = "http://localhost:8080"

# Create the Spotipy object with authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))

# Use the 'sp' object to search for a track
track_name = "Believer"  # Replace with the name of the track you want to search for
results = sp.search(q=track_name, type="track")

# Extract information from the search results
if results["tracks"]["items"]:
    track_info = results["tracks"]["items"][0]
    print("Track Name:", track_info["name"])
    print("Artist:", track_info["artists"][0]["name"])
    print("Album:", track_info["album"]["name"])
    print("Preview URL:", track_info["preview_url"])
else:
    print("Track not found.")
