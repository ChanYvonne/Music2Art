import spotipy
# To access authorised Spotify data
from spotipy.oauth2 import SpotifyClientCredentials

client_id = '{client_id}'
client_secret = '{client_secret}'

client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret)
# spotify object to access API
sp = spotipy.Spotify(auth='{OAuth_Token}',
                     client_credentials_manager=client_credentials_manager)
name = "Taylor Swift"  # chosen artist
result = sp.search(name)  # search query
# print(result['tracks']['items'][0]['artists'])

# Extract Artist's uri
artist_uri = result['tracks']['items'][0]['artists'][0]['uri']

# Pull all of the artist's albums
sp_albums = sp.artist_albums(artist_uri, album_type='album')
# Store artist's albums' names' and uris in separate lists
album_names = []
album_uris = []
# for i in range(len(sp_albums['items'])):
for i in range(2):
    album_names.append(sp_albums['items'][i]['name'])
    album_uris.append(sp_albums['items'][i]['uri'])

print(album_names)
print(album_uris)
# Keep names and uris in same order to keep track of duplicate albums

spotify_albums = {}
album_count = 0


def album_songs(uri):
    album = uri  # assign album uri to a_name

    spotify_albums[album] = {}  # Creates dictionary for that specific album
    # Create keys-values of empty lists inside nested dictionary for album
    spotify_albums[album]['album'] = []  # create empty list
    spotify_albums[album]['track_number'] = []
    spotify_albums[album]['id'] = []
    spotify_albums[album]['name'] = []
    spotify_albums[album]['uri'] = []

    tracks = sp.album_tracks(album)  # pull data on album tracks
    # print(tracks)

    for n in range(len(tracks['items'])):  # for each song track
        # append album name tracked via album_count
        spotify_albums[album]['album'].append(album_names[album_count])
        spotify_albums[album]['track_number'].append(
            tracks['items'][n]['track_number'])
        spotify_albums[album]['id'].append(tracks['items'][n]['id'])
        spotify_albums[album]['name'].append(tracks['items'][n]['name'])
        spotify_albums[album]['uri'].append(tracks['items'][n]['uri'])


def audio_features(album):
    # Add new key-values to store audio features
    spotify_albums[album]['acousticness'] = []
    spotify_albums[album]['danceability'] = []
    spotify_albums[album]['energy'] = []
    spotify_albums[album]['instrumentalness'] = []
    spotify_albums[album]['liveness'] = []
    spotify_albums[album]['loudness'] = []
    spotify_albums[album]['speechiness'] = []
    spotify_albums[album]['tempo'] = []
    spotify_albums[album]['valence'] = []
    spotify_albums[album]['popularity'] = []

    trackIds = []
    for track in spotify_albums[album]['id']:
        trackIds.append(track)

    print(trackIds)
    # pull audio features per track
    features = sp.audio_features(trackIds)
    # print(features)

    # analysis = sp.audio_analysis(trackIds[0])
    # print(analysis)

    # Append to relevant key-value
    if not(all(x is None for x in features)):
        spotify_albums[album]['acousticness'].append(
            features[0]['acousticness'])
        spotify_albums[album]['danceability'].append(
            features[0]['danceability'])
        spotify_albums[album]['energy'].append(features[0]['energy'])
        spotify_albums[album]['instrumentalness'].append(
            features[0]['instrumentalness'])
        spotify_albums[album]['liveness'].append(features[0]['liveness'])
        spotify_albums[album]['loudness'].append(features[0]['loudness'])
        spotify_albums[album]['speechiness'].append(features[0]['speechiness'])
        spotify_albums[album]['tempo'].append(features[0]['tempo'])
        spotify_albums[album]['valence'].append(features[0]['valence'])

    # popularity is stored elsewhere
    pop = sp.track(track)
    spotify_albums[album]['popularity'].append(pop['popularity'])


for i in album_uris:  # each album
    album_songs(i)
    print("Album " + str(album_names[album_count]) +
          " songs has been added to spotify_albums dictionary")
    album_count += 1  # Updates album count once all tracks have been added

for i in spotify_albums:
    audio_features(i)


# print(spotify_albums)
