import os
import sys
import spotipy
import spotipy.util as util


os.environ["SPOTIPY_CLIENT_ID"] = 'e4fecf947d534799b152a18023bae635'
os.environ["SPOTIPY_CLIENT_SECRET"] = '85c54c906e6b4695858061f2291f9838'
os.environ["SPOTIPY_REDIRECT_URI"] = 'https://spotify-finetune.herokuapp.com'


class Track:
    danceability = 0
    energy = 0
    acousticness = 0
    valence = 0
    score = 0
    def __init__(self, id, name):
        self.id = id
        self.name = name


def get_playlists(sp):
       playlists_objects = sp.current_user_playlists()["items"]
       playlists = {}
       for playlist in playlists_objects:
           playlists[playlist["id"]] = {
               "uri": playlist["uri"],
               "name": playlist["name"],
               "tracks": playlist["tracks"]["total"],
               "owner": playlist["owner"]["display_name"]
           }
       return playlists


def get_playlist_tracks(sp, playlist_id, username):
    tracks = {}
    track_objects = sp.user_playlist_tracks(username, playlist_id, "items(track(id,name))")["items"]
    for track in track_objects:
        tracks[track["track"]["id"]] = Track(track["track"]["id"], track["track"]["name"])
    return tracks


def get_all_saved_tracks(sp):
    tracks = {}
    results = sp.current_user_saved_tracks(50)
    track_objects = results["items"]
    while results['next']:
        results = sp.next(results)
        track_objects.extend(results["items"])
    for track in track_objects:
        tracks[track["track"]["id"]] = Track(track["track"]["id"], track["track"]["name"])
    return tracks


def query_track_metrics(sp, track_ids):
    ids = list(track_ids.keys())
    metrics = []
    chunks = [ids[i * 100:(i + 1) * 100] for i in range((len(ids) + 100 - 1) // 100)]
    for chunk in chunks:
        metrics.extend(sp.audio_features(chunk[:100]))
    return metrics


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


def get_most_related(sp, num_wanted, targets, username, playlist_id):
    if playlist_id is '':
        tracks = get_all_saved_tracks(sp)
    else:
        tracks = get_playlist_tracks(sp, playlist_id, username)
    metrics = query_track_metrics(sp, *[tracks])
    set_track_metrics(tracks, metrics)
    set_metric_scores(tracks.items(), targets)
    tracks = [track[1] for track in list(tracks.items())]
    tracks.sort(key=lambda x: x.score)
    return tracks[:num_wanted]


def create_playlist(sp, data):
    targets = {
        "danceability": (float(data["target[danceability]"]) / 100),
        "energy": (float(data["target[energy]"]) / 100),
        "acousticness": (float(data["target[acousticness]"]) / 100),
        "valence": (float(data["target[valence]"]) / 100)
    }
    response = sp.user_playlist_create(data["username"], data["name"])
    playlist_url = response['external_urls']['spotify']
    playlist_id = response["id"]
    related_tracks = get_most_related(sp, int(data["numSongs"]), targets, data["username"], data["playlist"])
    sp.user_playlist_add_tracks(data["username"], playlist_id, [track.id for track in related_tracks])
    return playlist_url
