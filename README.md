# Spotify-Playlist-from-Youtube
Takes Youtube's liked music videos and makes a Spotify playlist from it.

Primiarily uses the Youtube Data v3 API and Spotify API
In order to use this script, you need to have a Spotify account and a Youtube account. 

Used https://github.com/TheComeUpCode/SpotifyGeneratePlaylist as a start.
Unlike the code given, this script does not use the Youtube dl API, and instead webscrapes Youtube's video page source for the information.
This script also gives a result.txt file that reports the total songs detected, total songs added to the Spotify playlist, and lists all the songs that were not transfered.

# Detected Bugs
Unable to identify every music video from Youtube due to different formatting from source page of each music video.
As of recent has a 70% transfer rate of the detected music.
The songs that are not transferred over to Spotify are listed in a results.txt outputted by the program.
