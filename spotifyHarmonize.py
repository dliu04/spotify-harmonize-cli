import os
import authorize
import threading
import webbrowser
import time
import sys
import spotipy
import json

def run_flask():
    authorize.app.run(port=5000)

def clear_screen():
    # Clear the console screen
    os.system('cls' if os.name == 'nt' else 'clear')

def is_authorized():
    if not os.path.exists('token_info.json'):
        return False

    with open('token_info.json', 'r') as f:
        token_info = json.load(f)

    if 'access_token' not in token_info:
        return False

    return True

def playlist_input():
    while True:
        # Clear the screen
        clear_screen()

        # Get the playlist URL from the user
        print("Please paste your playlist URL.")
        print("Ensure that your account has access to this playlist, as the program will attempt to access songs from it.")
        print("You may also enter 'q' to quit.\n")
        playlist_url = input("Enter the playlist URL: ")
        
        if playlist_url.lower() == 'q':
            return 'quit'
        
        # Extract the playlist ID from the URL
        if 'playlist' in playlist_url:
            playlist_id = playlist_url.split('playlist/')[1].split('?')[0]
            return playlist_id
        else:
            print("Invalid playlist URL. Please try again.")

def new_or_recommend(playlist_id):    
    while True:
        # Clear the screen
        clear_screen()

        # Get the token info from the file
        with open('token_info.json', 'r') as f:
            token_info = json.load(f)

        # Create a Spotipy instance with the access token
        sp = spotipy.Spotify(auth=token_info['access_token'])

        # Fetch the playlist details
        playlist_details = sp.playlist(playlist_id)

        # Extract the playlist name
        playlist_name = playlist_details['name']

        # Explanation
        print("You can choose to select a different playlist to recommend songs from,\nor recommend songs based on your currently selected playlist.\n")

        # Display the options
        print("The selected playlist is:", playlist_name)
        print("1. Select new playlist")
        print("2. Recommend Songs")
        print("3. Quit")

        choice = input("Enter your choice: ")

        if choice == '1':
            return None  # Indicate that we need to select a new playlist
        elif choice == '2':
            recommend_songs(playlist_id)
        elif choice == '3':
            return 'quit'
        else:
            print("Invalid input. Please try again.")

def recommend_songs(playlist_id):
    # Clear the console screen
    clear_screen()

    # Get the token info from the file
    with open('token_info.json', 'r') as f:
        token_info = json.load(f)

    # Create a Spotipy instance with the access token
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Get the playlist tracks
    playlist_tracks = sp.playlist_tracks(playlist_id)['items']

    # Extract the track IDs
    track_ids = [track['track']['id'] for track in playlist_tracks if track['track'] is not None]

    # Ensure we have at most 5 seed tracks (Spotify API limit)
    seed_tracks = track_ids[:5]

    # Get the audio features for the tracks
    audio_features = sp.audio_features(seed_tracks)

    # Extract the audio features
    features = [track for track in audio_features if track is not None]

    # Calculate the average audio features
    avg_features = {}
    for feature in features:
        for key, value in feature.items():
            if isinstance(value, (int, float)):  # Ensure the value is numeric
                if key in avg_features:
                    avg_features[key] += value
                else:
                    avg_features[key] = value

    for key in avg_features:
        avg_features[key] /= len(features)

    # Get the recommended tracks based on the average audio features
    recommendations = sp.recommendations(
        seed_tracks=seed_tracks, 
        limit=10, 
        target_acousticness=avg_features.get('acousticness', 0),
        target_danceability=avg_features.get('danceability', 0),
        target_energy=avg_features.get('energy', 0),
        target_instrumentalness=avg_features.get('instrumentalness', 0),
        target_liveness=avg_features.get('liveness', 0),
        target_valence=avg_features.get('valence', 0)
    )

    # Display the recommended tracks
    print("Recommended Songs:")
    for idx, track in enumerate(recommendations['tracks']):
        print(f"{idx + 1}. {track['name']} by {track['artists'][0]['name']}")

    # Continue?
    input("\nPress Enter to continue...")

def main():
    # Clear the console screen
    clear_screen()

    while True:
        print("Welcome to Spotify Harmonize!")
        print("This software will generate a recommended playlist inspired by a playlist of your choosing.")
        print("Please ensure the intended playlists are public before you begin.")
        print("\n")
        print("1. Login to Spotify")
        print("2. Quit")

        choice = input("Enter your choice: ")

        if choice == '1':
            # Start the Flask app in a new thread
            flask_thread = threading.Thread(target=run_flask)
            flask_thread.daemon = True
            flask_thread.start()

            # Wait a moment for the server to start
            time.sleep(1)

            # Open the Spotify login page
            webbrowser.open("http://127.0.0.1:5000")

            # Wait until the user is authorized
            while not is_authorized():
                time.sleep(0.1)

            time.sleep(1)
            clear_screen()

            # Start the meat of the program
            while True:
                playlist_id = playlist_input()
                if playlist_id == 'quit':
                    break
                if playlist_id:
                    result = new_or_recommend(playlist_id)
                    if result == 'quit':
                        break 
            break

        elif choice == '2':
            break
        else:
            print("Invalid input. Please try again.")
    
    if os.path.exists('token_info.json'):
            os.remove('token_info.json')

    print("Harmonize next time!")
    

if __name__ == "__main__":
    main()
