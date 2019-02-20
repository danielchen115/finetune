import os
import sys
import spotipy
import spotipy.util as util

scope = 'user-library-read playlist-read-private playlist-read-collaborative user-modify-playback-state user-read-cur' \
        'rently-playing user-read-playback-state user-top-read user-read-recently-played app-remote-control streaming' \
        ' user-read-private user-library-read user-library-modify'

os.environ["SPOTIPY_CLIENT_ID"] = 'e4fecf947d534799b152a18023bae635'
os.environ["SPOTIPY_CLIENT_SECRET"] = '85c54c906e6b4695858061f2291f9838'
os.environ["SPOTIPY_REDIRECT_URI"] = 'http://spotify-finetune.herokuapp.com'

# token = util.prompt_for_user_token("user", scope)
#
# username = "daniel.chen115"

class Track:
    danceability = 0
    energy = 0
    acousticness = 0
    valence = 0
    score = 0
    def __init__(self, id, name):
        self.id = id
        self.name = name

# if token:
#         sp = spotipy.Spotify(auth=token)


def get_playlists(sp):
       playlists_objects = sp.current_user_playlists()["items"]
       playlists = {}
       for playlist in playlists_objects:
           playlists[playlist["id"]] = {
               "name": playlist["name"],
               "tracks": playlist["tracks"]["total"],
               "owner": playlist["owner"]["display_name"]
           }
       return playlists


def get_playlist_tracks(playlist_id):
    tracks = {}
    track_objects = sp.user_playlist_tracks(username, playlist_id, "items(track(id,name))")["items"]
    for track in track_objects:
        tracks[track["track"]["id"]] = Track(track["track"]["id"], track["track"]["name"])
    return tracks


def get_all_saved_tracks():
    tracks = {}
    results = sp.current_user_saved_tracks(50)
    track_objects = results["items"]
    while results['next']:
        results = sp.next(results)
        track_objects.extend(results["items"])
    for track in track_objects:
        tracks[track["track"]["id"]] = Track(track["track"]["id"], track["track"]["name"])
    return tracks


def query_track_metrics(track_ids):
    #TODO This API call can only take 100 track ids at a time, loop through the track_ids 100 at a time and return results
    return sp.audio_features(list(track_ids.keys())[:100])


def set_track_metrics(tracks, metrics):
    for metric in metrics:
        track = tracks[metric["id"]]
        track.danceability = metric["danceability"]
        track.energy = metric["energy"]
        track.acousticness = metric["acousticness"]
        track.valence = metric["valence"]


def set_metric_scores(tracks, targets):
    for id, track in tracks:
        track.score = abs(track.danceability - targets["danceability"]) + \
            abs(track.energy - targets["energy"]) + \
            abs(track.acousticness - targets["acousticness"]) + \
            abs(track.valence - targets["valence"])


def get_most_related(num_wanted, playlist_id=None):
    if playlist_id is None:
        tracks = get_all_saved_tracks()
    else:
        tracks = get_playlist_tracks(playlist_id)

    metrics = query_track_metrics(*[tracks])
    set_track_metrics(tracks, metrics)
    set_metric_scores(tracks.items(), targets)
    tracks = [track[1] for track in list(tracks.items())]
    tracks.sort(key=lambda x: x.score)
    return tracks[:num_wanted]

# targets = {
#     "danceability": 1,
#     "energy": 1,
#     "acousticness": 0.5,
#     "valence": 1
# }
#
# test = get_most_related(2000)
# print(test)
# print([track.score for track in test])

#7qkm4SsiK3T1nfHomYKojy