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
import time


from scipy.interpolate import interp1d

arduino = Serial(port='/dev/cu.usbserial-021FEBDC',
                 baudrate=115200, timeout=.1)
fps = 60
time_delta = 1./fps


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

    length = 2000
    width = 1500

    loud_scale = interp1d([min_loud, max_loud], [0, width]
                          )  # [min, max] of x-axis
    pitch_scale = interp1d([min_pitch, max_pitch], [
                           0, length])  # [min, max] of y-axis
    timbre_scale_x = interp1d([min_timbre, max_timbre], [
        0, length])  # another x- axis option

    timbre_scale_y = interp1d([min_timbre, max_timbre], [
        0, width])  # another y- axis option

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

    x_pitch_f = []
    x_timbre_f = []
    y_timbre_f = []
    y_loud_f = []

    visited = []

    # print(len(x_pitch))
    # print(len(x_timbre))

    # filter so it's not as many points -- assumes all lists are the same length
    # print(x_pitch)
    for i in range(math.floor(len(x_pitch)/100)):
        index = random.randrange(0, len(x_pitch))
        while(index in visited):
            index = random.randrange(0, len(x_pitch))
        visited.append(index)
        x_pitch_f.append(x_pitch[index])
        y_timbre_f.append(y_timbre[index])

    visited = []
    for i in range(math.floor(len(x_timbre)/100)):
        index = random.randrange(0, len(x_pitch))
        while(index in visited):
            index = random.randrange(0, len(x_pitch))
        visited.append(index)
        x_timbre_f.append(x_timbre[index])
        y_loud_f.append(y_loud[index])

    points = len(x_pitch_f) + len(x_timbre_f) + len(y_loud_f) + len(y_timbre_f)
    print("Total points extracted: " + str(points))

    loud_v_pitch = select_strokes(x_pitch_f, y_loud_f)
    loud_v_timbre = select_strokes(x_timbre_f, y_loud_f)
    timbre_v_pitch = select_strokes(x_pitch_f, y_timbre_f)

    # print(loud_v_pitch)

    # stimulate what it looks like
    plt.plot(loud_v_pitch[0], loud_v_pitch[1], c='red')
    plt.plot(loud_v_timbre[0], loud_v_timbre[1], c='green')
    plt.plot(timbre_v_pitch[0], timbre_v_pitch[1], c='blue')
    plt.show()

    loud_pitch = move_command(
        loud_v_pitch[0], loud_v_pitch[1])  # in y vs. x format

    loud_timbre = move_command(loud_v_timbre[0], loud_v_timbre[1])

    timbre_pitch = move_command(timbre_v_pitch[0], timbre_v_pitch[1])

    return [loud_pitch, loud_timbre, timbre_pitch]

# correlate specific brushstroke to segment features!


def select_strokes(x_cor, y_cor):
    new_x_coor = []
    new_y_coor = []
    # different brushstrokes -- either zigzag, box, or line
    for i in range(len(x_cor)-1):
        stroke = random.randrange(1, 6)
        # coor = manual_box(x_cor[i], y_cor[i])
        if (stroke == 1):
            if (i < 10):
                coor = triangle(x_cor[i], y_cor[i], y_cor[i:i+10])
            else:
                coor = triangle(x_cor[i], y_cor[i], y_cor[i-5:i+5])
        elif (stroke == 2):
            if (i < 10):
                coor = zigzag(x_cor[i], y_cor[i], x_cor[i+1],
                              y_cor[i+1], y_cor[i:i+10])
            else:
                coor = zigzag(x_cor[i], y_cor[i], x_cor[i+1],
                              y_cor[i+1], y_cor[i-5:i+5])
        elif (stroke == 3 or stroke == 4):
            if (i < 10):
                coor = manual_box(x_cor[i], y_cor[i], x_cor[i:i+10])
            else:
                coor = manual_box(x_cor[i], y_cor[i], x_cor[i-5:i+5])
        else:
            coor = [[x_cor[i]], [y_cor[i]]]
        new_x_coor.extend(coor[0])
        new_y_coor.extend(coor[1])

    return [new_x_coor, new_y_coor]


# def box_pattern(x1, y1, x2, y2):
#     num_squares = int((x2 - x1) / 2)
#     x_cor = [x1]
#     y_cor = [y1]
#     for i in range(1, num_squares+1):
#         x_cor.extend([x1 + 4*(i-1), x1 + 4*(i) + 8,
#                      x1 + 4*(i) + 8, x1 + 4*(i)])
#         y_cor.extend([y1 - 12*(i) + 8*(i-1), y1 - 12*(i) + 8*(i-1),
#                      y1 - 12*(i) + 8*(i), y1 - 12*(i) + 8*(i)])

#     x_cor.append(x2)
#     y_cor.append(y2)

#     return [x_cor, y_cor]


def zigzag(x1, y1, x2, y2, scale):
    normal = interp1d([min(scale), max(scale)], [.3, 1.5])
    y_range = x2 - x1
    domain = y2 - y1
    x_step = domain / 4
    y_step = y_range / 4
    x_cor = [x1]
    y_cor = [y1]
    for i in range(1, 5):
        x_cor.append(x1 + x_step*i)
        if (i % 2 == 0):
            y_cor.append(y1 + normal(scale[math.floor(len(scale)/2)])*y_step*i)
        else:
            y_cor.append(y1 - normal(scale[math.floor(len(scale)/2)])*y_step*i)

    x_cor.append(x2)
    y_cor.append(y2)

    return [x_cor, y_cor]


def triangle(x1, y1, scale):
    normal = interp1d([min(scale), max(scale)], [.3, 1.5])
    width = normal(scale[math.floor(len(scale)/2)]) * 100
    height = normal(scale[math.floor(len(scale)/2)]) * 100
    # print(width)
    # print(height)
    x_cor = [x1, x1 + width, x1 + .5*width, x1]
    y_cor = [y1, y1, y1 + height, y1]
    return [x_cor, y_cor]


def manual_box(x1, y1, scale):
    normal = interp1d([min(scale), max(scale)], [.3, 1.5])
    width = 300
    length = 500
    x_cor = [x1, x1 + width, x1 + width, x1, x1]
    y_cor = [y1, y1, y1 - length, y1 - length, y1]
    return [x_cor, y_cor]


def move_command(x_cor, y_cor):
    coordinates = []
    for y in y_cor:
        for x in x_cor:
            coordinates.append(
                "M," + str(x) + "," + str(y) + ".")
    return coordinates


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


def compile_coordinates(brushes, coordinates, colors):
    section = len(coordinates) / 5
    # print(section)

    all_commands = []

    # switch to using a brush: S,4.
    # divides the coordinates into 6 sections and switches brush 5 times
    coor_count = 0
    brush_count = 0
    for i in range(len(coordinates) + len(brushes)):
        if i % section == 0:
            # print(i/section)
            if (brush_count < 5):
                brush_count += 1
            all_commands.append("C," + str(brush_count) +
                                "," + str(brush_count-1) + ".")
            all_commands.append(
                "S," + str(brushes[math.floor(i / section)][0]) + ".")
            # first one is the paintbrush nummber and second is the paint hole numberr

        else:
            # print("count: " + str(coor_count))
            # print("len-coor: " + str(len(coordinates)))
            all_commands.append(coordinates[coor_count])
            if (coor_count < len(coordinates)-1):
                coor_count += 1

    # to stop all painting
    all_commands.append("X.")

    # print(all_commands)
    return all_commands


def send_commands(cmds):
    print("send")
    for cmd in cmds:
        print("CMD", cmd)
        notDone = True
        arduino.write(bytes(cmd, 'utf-8'))
        time.sleep(time_delta)
        while(notDone):
            data = arduino.readline().decode('utf-8')
            print(data)
            if("COMPLETED" in data):
                notDone = False
                time.sleep(time_delta)

    return data


def main():
    # Process is getting albums from artist, getting songs from album, then getting the song

    # artist, track = record_and_recognize_song()
    # artist, track = "Queen" , "Another One Bites The Dust"
    artist = "Hundred Waters"  # chosen artist
    track = "Show Me Love"
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
    all_coordinates.extend(loud_vs_pitch)
    all_coordinates.extend(loud_vs_timbre)
    all_coordinates.extend(timbre_vs_pitch)

    palette = select_color_palettes(features)
    all_commands = compile_coordinates(brushes, all_coordinates, palette)
    print(all_commands)
    print("total coors: " + str(len(all_coordinates)))

    # Test 1 - ~12000 read commands from testCommand.txt
    # text_file = open("testCommand.txt", "r")
    # commands = text_file.read().split('\', \'')
    # commands[len(commands)-1] = 'X.'
    # commands[0] = 'S,1.'

    # Test 2 - least commands
    # text_file = open("testCommand2.txt", "r")
    # commands = text_file.read().split('\', \'')

    # Test 3
    text_file = open("testCommand3.txt", "r")
    commands = text_file.read().split('\', \'')

    print("sending")
    while True:
        value = send_commands(commands)
        print(value)

    # print(len(coordinates))
    # print(coordinates[:100])


if __name__ == "__main__":
    main()
