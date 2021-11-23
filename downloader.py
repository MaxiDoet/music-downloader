import colorama
from ffmpeg.nodes import output_operator
from pytube import YouTube, Playlist
import ffmpeg
import sys, os, pathlib, re

def download_mp3(video : YouTube, index=1, playlist_length=1):
    stream = video.streams.get_audio_only()
    output_file = stream.download()

    print("[%sdownload%s] %d/%d %s%s%s" % (colorama.Fore.BLUE, colorama.Fore.RESET, index, playlist_length, colorama.Fore.GREEN, video.title, colorama.Fore.RESET))

    #os.rename(output_file, re.sub(r'[\\/*?:"<>|]',"", video.title + ".mp3"))
    new_filename = re.sub(r'[\\/*?:"<>|]',"", video.title + ".mp3")
    converted_stream = ffmpeg.input(output_file).output(new_filename).run()
    os.remove(output_file)

def download_playlist(playlist_url):
    playlist = Playlist(playlist_url)

    print("[%splaylist%s] Title: %s%s%s" % (colorama.Fore.BLUE, colorama.Fore.RESET, colorama.Fore.GREEN, playlist.title, colorama.Fore.RESET))
    print("[%splaylist%s] Length: %s%d%s" % (colorama.Fore.BLUE, colorama.Fore.RESET, colorama.Fore.GREEN, len(playlist), colorama.Fore.RESET))

    index = 1
    for video in playlist.videos:
        download_mp3(video, index, playlist.length)
        index+=1

    print("[%splaylist%s] %sDone%s" % (colorama.Fore.BLUE, colorama.Fore.RESET, colorama.Fore.GREEN, colorama.Fore.RESET))

# Init color console
colorama.init()
try:
    input_url = sys.argv[1]
except:
    print("%sNo url provided!%s" % (colorama.Fore.RED, colorama.Fore.RESET))
    exit(-1)

if input_url.find("playlist?list="):
    download_playlist(input_url)
else:
    print(input_url.find("playlist"))
    download_mp3(YouTube(input_url))