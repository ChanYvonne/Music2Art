import spotipy
import json
# To access authorised Spotify data
from spotipy.oauth2 import SpotifyClientCredentials

client_id = 'f0338d1fd79f4310835cede197372d6'
client_secret = '1e395ecaf45f488fa539560d57963bf6'

client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret)
# spotify object to access APIBQDAPTRBDFmfEX0bq0z_uXuBatyQ6EDJvbg
sp = spotipy.Spotify(auth='BQA57OGFOkOYt3cEPNuYuF84DUloZ1t0cRVqK8xCapN-3oS7wCdGfGTqVQOMFPZrKm0Rpwn1bDTG7SLEzj6yZEk_KMsvJijYo0YLezXcs69xuQLSC_gwpbxfHbugfW3wh1n1ed0SHzCg-g',
                     client_credentials_manager=client_credentials_manager)


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


def main():
    # Process is getting albums from artist, getting songs from album, then getting the song

    artist = "Olivia Rodrigo"  # chosen artist
    track = "Driver's License"
    track_uri = get_track_uri(track, artist)
    track_info = get_audio_features(str(track_uri))
    get_audio_analysis(track_uri)


if __name__ == "__main__":
    main()
