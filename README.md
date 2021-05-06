# Music2Art
We are creating a robot that will analyze a song and leverage key features such as tempo and energy to paint a visual representation on a canvas.

## Using the Spotify API

Currently, we search an artist and obtain the analysis of all the songs inn their first 2 albums.

Look at our [main google doc](https://docs.google.com/document/d/1xPSgBzcAEPLYSjhON0_wrUdEWrFwvOdIUPejxYnWpKk/edit) to see what the Spotify API client and oauth credentials. If the OAuth token is expired, retrieve a new OAuth Token [here](https://developer.spotify.com/console/get-audio-analysis-track/?id=06AKEBrKUckW0KREUWRnvT).

Also, we're using the Spotipy library so to install:
```pip install spotipy```