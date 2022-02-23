import argparse
from turtle import color
import colorama
from ffmpeg.nodes import output_operator
from pytube import YouTube, Playlist, Search
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import ffmpeg
import sys, os, pathlib, re
from halo import Halo
import json

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

# Parse arguments
parser = argparse.ArgumentParser(description='Youtube/Spotify downloader.')
parser.add_argument("--skip", help="Skip download if file exists", action=argparse.BooleanOptionalAction)
parser.add_argument("url", help="URL to download")
args = parser.parse_args()

def download_mp3(video : YouTube, folder, index=1, playlist_length=1):
    filename = re.sub(r'[\\/*?:"<>|]',"", video.title + ".mp3")
    filepath = "files/" + folder + "/" + filename

    spinner = Halo(text='%d/%d Fetching' % (index, playlist_length), spinner='dots')

    if not os.path.exists("files/" + folder):
        os.mkdir("files/" + folder)

    if os.path.exists(filepath):
        if args.skip:
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

def download_playlist(playlist_url):
    spinner = Halo(text='Fetching', spinner='dots')

    spinner.start()
    playlist = Playlist(playlist_url)
    spinner.stop()
    spinner.succeed("%s" % (playlist.title))

    index = 1
    for video in playlist.videos:
        download_mp3(video, playlist.title, index, playlist.length)
        index+=1

def find_youtube_by_title(title):
    results = Search(title).results
    return results[0]
    
def download_spotify_playlist(url):
    playlist = sp.playlist(str(url))
    playlist_name = playlist["name"]    

    tracks = playlist["tracks"]["items"]

    for i in range(len(tracks)):
        track_id = tracks[i]["track"]["id"]
        track = sp.track(track_id)
        query = track["name"] + " " + track["artists"][0]["name"]

        vid = find_youtube_by_title(query)
        download_mp3(vid, playlist_name, i+1, len(tracks))

# Init color console
colorama.init()

input_url = args.url

spinner = Halo(text='Please wait', spinner='dots')
spinner.start()

if "youtube.com" in input_url:
    if "youtube.com/playlist?list" in input_url:
        spinner.succeed("Youtube Playlist")
        download_playlist(input_url)
    else:
        spinner.succeed("Youtube Track")
        download_mp3(YouTube(input_url), "")  
elif "spotify.com" in input_url:
    spinner.succeed("Spotify Playlist")
    download_spotify_playlist(input_url)