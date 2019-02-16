import sys
import os
import spotipy
import spotipy.util as util

scope = 'user-library-read playlist-read-private playlist-read-collaborative user-modify-playback-state user-read-cur' \
        'rently-playing user-read-playback-state user-top-read user-read-recently-played app-remote-control streaming' \
        ' user-read-private user-library-read user-library-modify'

os.environ["SPOTIPY_CLIENT_ID"] = 'e4fecf947d534799b152a18023bae635'
os.environ["SPOTIPY_CLIENT_SECRET"] = '85c54c906e6b4695858061f2291f9838'
os.environ["SPOTIPY_REDIRECT_URI"] = 'https://httpbin.org/get'

token = util.prompt_for_user_token("user", scope)

if token:
        sp = spotipy.Spotify(auth=token)
        print(sp.current_user())
