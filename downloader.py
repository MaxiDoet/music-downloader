import argparse
from turtle import color
import colorama
from ffmpeg.nodes import output_operator
from numpy import source
from pip import List
from pytube import YouTube, Playlist, Search
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import ffmpeg
import sys, os, pathlib, re
from halo import Halo
import json
from ytmusicapi import YTMusic

# Try to load config
config = {}
try:
    config_fp = open("config.json", "r")
    config = json.load(config_fp)
except:
    # Create new config
    client_id_input = input("Spotify Client ID: ")
    client_secret_input = input("Spotify Client Secret: ")
    config = {
        "client_id": client_id_input,
        "client_secret": client_secret_input
    }
    config_fp = open("config.json", "w+")
    config_fp.write(json.dumps(config))

# Spotify credentials
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=config["client_id"], client_secret=config["client_secret"]))

ytmusic = YTMusic()

# Parse arguments
parser = argparse.ArgumentParser(description='Youtube/Spotify downloader.')
parser.add_argument("-r", help="Replace files if they already exist", action=argparse.BooleanOptionalAction)
parser.add_argument("url", help="URL to download")
args = parser.parse_args()

SOURCE_TYPES = ["YouTube", "Spotify"]

def download_youtube_video(video : YouTube, folder, index=1, playlist_length=1):
    filename = re.sub(r'[\\/*?:"<>|]',"", video.title + ".mp3")
    filepath = "files/" + folder + "/" + filename

    spinner = Halo(text='%d/%d Fetching' % (index, playlist_length), spinner='dots')

    if not os.path.exists("files/" + folder):
        os.mkdir("files/" + folder)

    if os.path.exists(filepath):
        if not args.r:
            spinner.warn("%d/%d %s" % (index, playlist_length, video.title))
            return
        else:
            os.remove(filepath)

    spinner.start()
    stream = video.streams.get_audio_only()
    spinner.stop()

    spinner.text = "%d/%d Downloading" % (index, playlist_length)
    spinner.start()
    output_file = stream.download()
    spinner.stop()

    spinner.text = "%d/%d Converting" % (index, playlist_length)
    spinner.start()
    try:
        converted_stream = ffmpeg.input(output_file).output(filepath).run(quiet=True)
    except ffmpeg._run.Error:
        spinner.fail("%d/%d FFmpeg error" % (index, playlist_length))
        return

    os.remove(output_file)

    spinner.stop()
    spinner.succeed("%d/%d %s" % (index, playlist_length, video.title))

class SourceInfo:
    def __init__(self, single, type, title, owner, trackCount, tracks):
        self.single = single
        self.type = type
        self.title = title
        self.owner = owner
        self.trackCount = trackCount
        self.tracks = tracks

    def __str__(self) -> str:
        return ("Source: %s\nTitle: %s\nOwner: %s\nTracks: %d\n" % (SOURCE_TYPES[self.type], self.title, self.owner, self.trackCount))

    def download(self):
        if self.type == 0:
            if (self.single):
                download_youtube_video(self.tracks[0], "", 1, 1)
            else:
                for i in range(len(self.tracks)):
                    download_youtube_video(self.tracks[i], self.title, i+1, self.trackCount)

        elif self.type == 1:
            for i in range(len(self.tracks)):
                download_youtube_video(self.tracks[i], self.title, i+1, self.trackCount)

def fetch_youtube_video(url) -> SourceInfo:
    video = YouTube(url)
    return SourceInfo(True, 0, video.title, video.author, 1, [YouTube(url)])

def fetch_youtube_playlist(url) -> SourceInfo:
    playlist = Playlist(url)
    return SourceInfo(False, 0, playlist.title, "Unknown", len(playlist.videos), playlist.videos)

def find_youtube_video(query):
    """
    results = Search(title).results
    return results[0]
    """

    results = ytmusic.search(query, filter="songs")
    result_id = ""

    for i in range(len(results)):
        category = results[i]["category"]
        result_type = results[i]["resultType"]

        if category == "Songs" and result_type == "song":
            result_id = results[i]["videoId"]
            return YouTube("https://youtube.com/watch?v=%s" % (result_id))
        else:
            pass

    return YouTube("https://youtube.com/watch?v=%s" % (result_id))

def fetch_spotify_playlist(url) -> SourceInfo:
    playlist = sp.playlist(str(url))
    tracks = playlist["tracks"]["items"]

    # Find youtube videos
    videos = []

    spinner = Halo(text='Fetching Tracks', spinner='dots')
    spinner.start()

    for i in range(len(tracks)):
        track_id = tracks[i]["track"]["id"]
        track = sp.track(track_id)
        videos.append(find_youtube_video(track["name"] + " " + track["artists"][0]["name"]))

    spinner.stop()

    return SourceInfo(False, 1, playlist["name"], playlist["owner"]["display_name"], len(videos), videos)

# Init color console
colorama.init()

input_url = args.url

spinner = Halo(text='Please wait', spinner='dots')
spinner.start()

# Fetch playlist
if "youtube.com" in input_url:
    spinner.stop()

    if "youtube.com/playlist?list" in input_url:
        source_info = fetch_youtube_playlist(input_url)
    else:
        source_info = fetch_youtube_video(input_url)
        
elif "spotify.com" in input_url:
    spinner.stop()
    source_info = fetch_spotify_playlist(input_url)
else:
    print("Unknown source type!")

print(source_info)

source_info.download()