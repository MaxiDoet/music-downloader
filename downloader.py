import colorama
from ffmpeg.nodes import output_operator
from pytube import YouTube, Playlist
import ffmpeg
import sys, os, pathlib, re
from halo import Halo

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

# Init color console
colorama.init()
try:
    input_url = sys.argv[1]
except:
    print("%sNo url provided!%s" % (colorama.Fore.RED, colorama.Fore.RESET))
    exit(-1)

if "youtube.com/playlist?list" in input_url:
    download_playlist(input_url)
else:
    download_mp3(YouTube(input_url))