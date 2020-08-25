# Spotify-Playlist-from-Youtube
Takes Youtube's liked music videos and makes a Spotify playlist from it.

Primiarily uses the Youtube Data v3 API and Spotify API
In order to use this script, you need to have a Spotify account and a Youtube account. 

Used https://github.com/TheComeUpCode/SpotifyGeneratePlaylist as a start.

Code differences:
1. This script does not use the Youtube dl API, and instead webscrapes Youtube's video page source for the information.
2. This script also gives a result.txt file that reports the total songs detected, total songs added to the Spotify playlist, and lists all the songs that were not transfered.
3. This script iterates over all json files given from Youtube API, allowing it to go through all Youtube liked videos instead of only one page of the json files.

# Files
To run this program, you must download all the imports used for python. You must also have the client keys and id's to use the api's in order to connect with your accounts.

create_playlist.py - main code source

client_secret.json - used for the Youtube Data v3 API, contains the api key, client id, etc.

secrets.py - contains api key and sportify user used for the Spotify API

results.txt - example results that outputs from program

# Detected Bugs
Unable to identify every music video from Youtube due to different formatting from source page of each music video.
As of recent has a 70% transfer rate of the detected music.
The songs that are not transferred over to Spotify are listed in a results.txt outputted by the program.

There is a way of getting a high percent transfer value by about 10% but it makes the program take longer to process through all the videos, as one of the methods in getting the songs used is looking at the webpage source. Doing this for every song takes too long. 
