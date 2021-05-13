import callSpotify
import sounddevice as sd
from scipy.io.wavfile import write
import wavio
from pydub import AudioSegment
import os
# from ShazamAPI import Shazam
from serial import Serial
import math

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
    track_uri = callSpotify.get_track_uri(track, artist)['uri']
    track_info = callSpotify.get_audio_features(str(track_uri))
    track_analysis = callSpotify.get_audio_analysis(track_uri)

    return [track_info, track_analysis]


def truncate(number, digits):
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


def loudness_pitch_coordinates(loudness, pitches):
    max_loud = max(loudness)
    min_loud = min(loudness)
    max_pitch = max(pitches)
    min_pitch = min(pitches)

    loud_scale = interp1d([min_loud, max_loud], [0, 160]
                          )  # [min, max] of x-axis
    pitch_scale = interp1d([min_pitch, max_pitch], [
                           0, 110])  # [min, max] of y-axis

    command_strings = []

    for y in loud_scale(loudness):
        for x in pitch_scale(pitches):
            x_cor = truncate(x, 3)
            y_cor = truncate(y, 3)
            command_strings.append(
                "M," + str(x_cor) + "," + str(y_cor) + ".")

    return command_strings


def sendCommands():
    arduino.write(bytes("M,100,200.", 'utf-8'))


def main():
    # Process is getting albums from artist, getting songs from album, then getting the song

    # artist, track = record_and_recognize_song()
    #artist, track = "Queen" , "Another One Bites The Dust"
    artist = "Jon Bellion"  # chosen artist
    track = "Stupid Deep"
    spotify_info = get_spotify_info(artist, track)
    analysis = spotify_info[1]
    coordinates = loudness_pitch_coordinates(
        analysis['loudness'], analysis['pitches'])
    print(len(coordinates))
    print(coordinates[:100])


if __name__ == "__main__":
    main()
