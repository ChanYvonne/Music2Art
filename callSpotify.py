import spotipy
import json
# To access authorised Spotify data
from spotipy.oauth2 import SpotifyClientCredentials
import time

client_id = 'f0338d1fd79f4310835cede197372d6'
client_secret = '1e395ecaf45f488fa539560d57963bf6'

client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth='BQCwGuzAVwXB7kfGQgsVueP70tLs0RYpA7pRUaB_C3x8rxgMDxsV_svdaIdi5EqlIJr12YlaOjOxXWFQK4LHA2NnhRbgNViO-ac7oQY2S_WQS7X_-Ta-pOtHKSIVgH4Ljj6RSAQfZG7udQ',
                     client_credentials_manager=client_credentials_manager)
arduino = None


def get_track_uri(track, artist):
    result = sp.search(track + " " + artist, limit=5, type='track,artist')
    # print(json.dumps(result, indent=4))
    # print(track_uri)

    track_info = {}
    track_info['uri'] = result['tracks']['items'][0]['uri']
    track_info['popularity'] = result['tracks']['items'][0]['popularity']
    track_info['length'] = result['tracks']['items'][0]['duration_ms']

    return track_info


def get_audio_features(track_uri):

    track_features = {}

    features = sp.audio_features(track_uri)
    # print(json.dumps(features, indent=4))

    track_features['acousticness'] = features[0]['acousticness']
    track_features['danceability'] = features[0]['danceability']
    track_features['energy'] = features[0]['energy']
    track_features['instrumentalness'] = features[0]['instrumentalness']
    track_features['liveness'] = features[0]['liveness']
    track_features['loudness'] = features[0]['loudness']
    track_features['speechiness'] = features[0]['speechiness']
    track_features['tempo'] = features[0]['tempo']
    track_features['valence'] = features[0]['valence']
    track_features['key'] = features[0]['key']

    return track_features


def get_audio_analysis(track_uri):

    track_analysis = {}
    analysis = sp.audio_analysis(track_uri)
    # print(json.dumps(analysis, indent=4))
    sections = analysis['sections']
    segments = analysis['segments']

    # print(json.dumps(sections, indent=4))
    # print(len(sections))
    # print(len(segments))

    track_analysis['loudness'] = []
    track_analysis['pitches'] = []
    track_analysis['timbre'] = []
    track_analysis['segment_end'] = []

    for i in segments:
        track_analysis['loudness'].append(i['loudness_max'])
        track_analysis['pitches'].append(sum(i['pitches'])/len(i['pitches']))
        track_analysis['timbre'].append(sum(i['timbre'])/len(i['timbre']))
        current_time = float(
            i['start']) + float(i['duration'])
        track_analysis['segment_end'].append(current_time)

    return track_analysis


def main():
    # Process is getting albums from artist, getting songs from album, then getting the song

    artist = "Olivia Rodrigo"  # chosen artist
    track = "Driver's License"
    # artist, track = record_and_recognize_song()
    #artist, track = "Queen" , "Another One Bites The Dust"
    track_uri = get_track_uri(track, artist)['uri']
    track_info = get_audio_features(str(track_uri))
    get_audio_analysis(track_uri)

    # send_strokes_to_arduino()


if __name__ == "__main__":
    main()
