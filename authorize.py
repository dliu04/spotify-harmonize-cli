from flask import Flask, request, url_for, session, redirect
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from flask_session import Session
import json

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = 'iwantto###signasecret!'
Session(app)

TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    spotify_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = spotify_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info

    # Store token info in a file
    with open('token_info.json', 'w') as f:
        json.dump(token_info, f)

    return redirect(url_for('savePlaylist'))

@app.route('/savePlaylist')
def savePlaylist():
    token_info = get_token()
    if not token_info:
        return redirect(url_for('login'))
    return "OAUTH SUCCESSFUL! You can now generate playlists."

@app.route('/is_authorized')
def check_authorization():
    token_info = session.get(TOKEN_INFO, None)
    if token_info and token_info['expires_at'] > int(time.time()):
        return "true"
    return "false"

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    print("Session contents:", session)  # Debug output
    if not token_info:
        print("Token info not found in session.")
        return redirect(url_for('login', _external=False))
    
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        print("Token is expired, refreshing...")
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info  # Update session with the new token info

    print("Token info retrieved successfully.")
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id='e3ee009e9bc04a5dbb8f9a62a6d6f923',
        client_secret='7be4c70da1944a92818d3ef2291c9afc',
        redirect_uri=url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private'
    )

if __name__ == "__main__":
    app.run(port=5000, debug=False)
