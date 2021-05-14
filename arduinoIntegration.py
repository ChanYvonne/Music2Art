import callSpotify
import sounddevice as sd
from scipy.io.wavfile import write
import wavio
from pydub import AudioSegment
import os
# from ShazamAPI import Shazam
from serial import Serial
import math
import numpy as np
import matplotlib.pyplot as plt
import random

from scipy.interpolate import interp1d

# arduino = Serial(port='/dev/cu.usbserial-021FEBDC',
#                  baudrate=115200, timeout=.1)


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


def get_spotify_info(artist, track):
    track_info = callSpotify.get_track_uri(track, artist)
    uri = track_info['uri']
    length = float(track_info['length'])
    track_features = callSpotify.get_audio_features(str(uri))
    track_analysis = callSpotify.get_audio_analysis(uri)

    return [track_features, track_analysis, length]


def truncate(number, digits):
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


def generate_coordinates(loudness, pitches, timbre):
    max_loud = max(loudness)
    min_loud = min(loudness)
    max_pitch = max(pitches)
    min_pitch = min(pitches)
    max_timbre = max(timbre)
    min_timbre = min(timbre)

    loud_scale = interp1d([min_loud, max_loud], [0, 3162]
                          )  # [min, max] of x-axis
    pitch_scale = interp1d([min_pitch, max_pitch], [
                           0, 4540])  # [min, max] of y-axis
    timbre_scale_x = interp1d([min_timbre, max_timbre], [
        0, 4540])  # another x- axis option

    timbre_scale_y = interp1d([min_timbre, max_timbre], [
        0, 3162])  # another y- axis option

    x_pitch = []
    x_timbre = []
    y_timbre = []
    y_loud = []

    for y in loud_scale(loudness):
        y_loud.append(truncate(y, 3))
    for x in pitch_scale(pitches):
        x_pitch.append(truncate(x, 3))
    for x in timbre_scale_x(timbre):
        x_timbre.append(truncate(x, 3))
    for y in timbre_scale_y(timbre):
        y_timbre.append(truncate(y, 3))

    # stimulate what it looks like
    # plt.scatter(x_pitch, y_loud, c='red')
    # plt.scatter(x_pitch, y_timbre, c='green')
    # plt.scatter(x_timbre, y_loud, c='blue')
    # plt.show()

    loud_pitch = []  # in y vs. x format
    for y in y_loud:
        for x in x_pitch:
            loud_pitch.append(
                "M," + str(x) + "," + str(y) + ".")

    loud_timbre = []
    for y in y_loud:
        for x in x_timbre:
            loud_timbre.append(
                "M," + str(x) + "," + str(y) + ".")

    timbre_pitch = []
    for y in y_timbre:
        for x in x_pitch:
            timbre_pitch.append(
                "M," + str(x) + "," + str(y) + ".")

    return [loud_pitch, loud_timbre, timbre_pitch]


def select_brushes(duration):
    time_sect = duration / 6.0
    first_brush = [random.randrange(1, 3), 0.0]
    second_brush = [random.randrange(4, 6), time_sect]
    third_brush = [random.randrange(1, 4), time_sect * 2]
    fourth_brush = [random.randrange(3, 6), time_sect * 3]
    fifth_brush = [random.randrange(4, 6), time_sect * 4]
    sixth_brush = [random.randrange(2, 5), time_sect * 5]

    return [first_brush, second_brush, third_brush, fourth_brush, fifth_brush, sixth_brush]


def select_color_palettes(features):
    valence = features['valence']
    energy = features['energy']
    colors = ""
    if valence >= .5 and energy >= .5:
        colors = ["pink", "blue", "yellow", "red", "green"]
    elif valence >= .5 and energy < .5:
        colors = ["orange", "pink", "yellow", "white", "green"]
    elif valence < .5 and energy >= .5:
        colors = ["blue", "white", "red orange", "blue", "green"]
    else:
        colors = ["blue", "purple", "dark red", "black", "indigo"]
    return colors


def compile_coordiinates(brushes, coordinates, colors):
    section = len(coordinates) / 6

    all_commands = []

    # get color command -- ex: C,1,red.
    for i in range(1, len(brushes)+1):
        all_commands.append("C," + str(i) + "," + colors[i-1] + ".")

    # switch to using a brush: S,4.
    # divides the coordinates into 6 sections and switches brush 5 times
    coor_count = 0
    for i in range(len(coordinates) + len(brushes)):
        if i % section == 0:
            all_commands.append("S," + brushes[i] + ".")
        else:
            all_commands.append(coordinates[coor_count])
            coor_count += 1

    return all_commands


def send_commands(cmds):
    arduino.write(bytes("M,100,200.", 'utf-8'))


def main():
    # Process is getting albums from artist, getting songs from album, then getting the song

    # artist, track = record_and_recognize_song()
    #artist, track = "Queen" , "Another One Bites The Dust"
    artist = "Borns"  # chosen artist
    track = "Electric Love"
    spotify_info = get_spotify_info(artist, track)
    features = spotify_info[0]
    analysis = spotify_info[1]
    duration = spotify_info[2] / 1000
    brushes = select_brushes(duration)
    coordinates = generate_coordinates(
        analysis['loudness'], analysis['pitches'], analysis['timbre'])
    loud_vs_pitch = coordinates[0]
    loud_vs_timbre = coordinates[1]
    timbre_vs_pitch = coordinates[2]
    all_coordinates = []
    all_coordinates.append(loud_vs_pitch).append(
        loud_vs_timbre).append(timbre_vs_pitch)
    palette = select_color_palettes(features)
    all_commands = compile_coordiinates(brushes, all_coordinates, palette)
    send_commands(all_commands)

    # print(len(coordinates))
    # print(coordinates[:100])
if __name__ == "__main__":
    main()
