import spotipy
import json
# To access authorised Spotify data
from spotipy.oauth2 import SpotifyClientCredentials
import sounddevice as sd
from scipy.io.wavfile import write
import wavio
from pydub import AudioSegment
import os
from ShazamAPI import Shazam
from serial import Serial
import time

client_id = 'f0338d1fd79f4310835cede197372d6'
client_secret = '1e395ecaf45f488fa539560d57963bf6'

client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret)
# spotify object to access APIBQDAPTRBDFmfEX0bq0z_uXuBatyQ6EDJvbg
sp = spotipy.Spotify(auth='BQCztlGTWtplwudW27Pccs2toRB-ZR6UWczAivtD0z4Du6tBhnsVtsmhMrJcvmBYWleKaa3G8lspQk9xZSI49OmFmWYcwltAf1GpY5HXTu8Q7CYPcgtFpTsluaTofscCzuLp7ujg0USbTwlWoU10185eIYxlfDHCUJUktqX35UeQx3p1m74',
                     client_credentials_manager=client_credentials_manager)

# arduino = Serial(port='/dev/cu.usbserial-021FEBDC', baudrate=115200, timeout=.1)


def get_track_uri(track, artist):
    result = sp.search(track + " " + artist, limit=5, type='track,artist')
    print(result)
    track_uri = result['tracks']['items'][0]['uri']
    # print(track_uri)
    # maybe helpful later
    popularity = result['tracks']['items'][0]['popularity']
    return track_uri
    # print(json.dumps(result, indent=4))


def get_audio_features(track_uri):

    track_info = {}

    features = sp.audio_features(track_uri)
    # print(json.dumps(features, indent=4))

    track_info['acousticness'] = features[0]['acousticness']
    track_info['danceability'] = features[0]['danceability']
    track_info['energy'] = features[0]['energy']
    track_info['instrumentalness'] = features[0]['instrumentalness']
    track_info['liveness'] = features[0]['liveness']
    track_info['loudness'] = features[0]['loudness']
    track_info['speechiness'] = features[0]['speechiness']
    track_info['tempo'] = features[0]['tempo']
    track_info['valence'] = features[0]['valence']

    return track_info


def get_audio_analysis(track_uri):
    analysis = sp.audio_analysis(track_uri)
    # print(json.dumps(analysis, indent=4))
    sections = analysis['sections']
    segments = analysis['segments']

    # print(json.dumps(sections, indent=4))
    # print(len(sections))
    # print(len(segments))


def record_and_recognize_song():
    print("Listening!")
    # arduino.write(bytes("Listening", 'utf-8'))
    fs = 44100  # Sample rate
    seconds = 5  # Duration of recording

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)

    sd.wait()  # Wait until recording is finished
    write('output1.wav', fs, myrecording)  # Save as WAV file
    wavio.write("myfile1.wav", myrecording, fs, sampwidth=2)
    sound = AudioSegment.from_wav('myfile1.wav')
    sound.export('myfile.mp3', format='mp3')
    mp3_file_content_to_recognize = open('myfile.mp3', 'rb').read()

    shazam = Shazam(mp3_file_content_to_recognize)
    recognize_generator = shazam.recognizeSong()
    song = None
    while song is None:
        song = next(recognize_generator)
    print(song)
    title = song[1]['track']['title']
    artist = song[1]['track']['subtitle']
    print(artist, title)
    os.remove("myfile.mp3")
    os.remove("myfile1.wav")
    os.remove("output1.wav")
    return artist, title


def send_strokes_to_arduino():
    print("Sending Strokes!")


def main():
    # Process is getting albums from artist, getting songs from album, then getting the song

    artist = "Olivia Rodrigo"  # chosen artist
    track = "Driver's License"
    artist, track = record_and_recognize_song()
    #artist, track = "Queen" , "Another One Bites The Dust"
    track_uri = get_track_uri(track, artist)
    track_info = get_audio_features(str(track_uri))
    get_audio_analysis(track_uri)

    # send_strokes_to_arduino()


if __name__ == "__main__":
    main()
