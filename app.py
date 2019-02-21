from flask import Flask, render_template, request, jsonify
from helper import *


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/playlists', methods=['GET', 'POST'])
def playlists():
    token = request.form['token']
    sp = spotipy.Spotify(auth=token)
    playlists = get_playlists(sp)
    data = {"playlists": playlists}
    return jsonify(data)


@app.route('/save', methods=['GET', 'POST'])
def save():
    token = request.form['token']
    sp = spotipy.Spotify(auth=token)
    url = create_playlist(sp, request.form)
    return jsonify(url)


if __name__ == "__main__":
    app.run(debug=True)
