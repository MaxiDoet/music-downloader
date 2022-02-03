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

# Spotify credentials
client_id = "70cc9baf7e154688a8d6ed961471e595"
client_secret = "1c8dd29b8b3d4ed19f781b0bd639773b"

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def download_mp3(video : YouTube, index=1, playlist_length=1):
    spinner = Halo(text='%d/%d Fetching' % (index, playlist_length), spinner='dots')

    spinner.start()
    stream = video.streams.get_audio_only()
    spinner.stop()

    spinner.text = "%d/%d Downloading" % (index, playlist_length)
    spinner.start()
    output_file = stream.download()
    spinner.stop()

    spinner.text = "%d/%d Converting" % (index, playlist_length)
    spinner.start()
    new_filename = re.sub(r'[\\/*?:"<>|]',"", video.title + ".mp3")
    converted_stream = ffmpeg.input(output_file).output("files/" + new_filename).run(quiet=True)
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
        download_mp3(video, index, playlist.length)
        index+=1

def find_youtube_by_title(title):
    results = Search(title).results
    return results[0]
    
def download_spotify_playlist(url):
    playlist = sp.playlist(url)
    tracks = playlist["tracks"]["items"]

    for i in range(len(tracks)):
        track_id = tracks[i]["track"]["id"]
        track = sp.track(track_id)
        query = track["name"] + " " + track["artists"][0]["name"]

        vid = find_youtube_by_title(query)
        download_mp3(vid, i+1, len(tracks))

# Init color console
colorama.init()
try:
    input_url = sys.argv[1]
except:
    print("%sNo url provided!%s" % (colorama.Fore.RED, colorama.Fore.RESET))
    exit(-1)

spinner = Halo(text='Detecting link type', spinner='dots')
spinner.start()

if "youtube.com" in input_url:
    if "youtube.com/playlist?list" in input_url:
        spinner.succeed("Youtube Playlist")
        download_playlist(input_url)
    else:
        spinner.succeed("Youtube Audio")
        download_mp3(YouTube(input_url))  
elif "spotify.com" in input_url:
    spinner.succeed("Spotify Playlist")
    download_spotify_playlist(input_url)