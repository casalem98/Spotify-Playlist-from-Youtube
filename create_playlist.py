'''
Steps:
1. Log into youtube
2. Get liked videos
3. Create new spotify playlist
4. Search for songs in spotify
5. Add song to spotify playlist
'''

import json 
import os
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import re

from secrets import spotify_user_id, spotify_token

class CreatePlaylist:

    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    #1. Log into youtube
    def get_youtube_client(self):
        #From the Youtube API document
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        print('Going to read client_secret file')
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)

        credentials = flow.run_console()


        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube

    #2. Get liked videos from youtube data api
    def get_liked_videos(self):
        # goes through the liked videos
        request = self.youtube_client.videos().list(
            part="snippet,contentDetails,statistics",
            maxResults=1500,
            myRating="like"
        )

        has_next_key = True
        songs_detected = 0
        songs_added = 0
        out_file = open("results.txt", "w+")

        while has_next_key:
            # colloect each video and get important information
            response = request.execute()

            for item in response["items"]:
                video_title = item["snippet"]["title"]
                category = item["snippet"]["categoryId"]
                #print(category)
                youtube_url = "http://www.youtube.com/watch?v={}".format(item["id"])

                #video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
                if category != '10':
                    continue

                artist, song_name = self.get_song_info(youtube_url, video_title)

                if artist is None or song_name is None:
                    continue
                print(item["id"])
                songs_detected += 1
                # song_name = song_name.group(1)
                # artist = artist.group(1)
                #print('Song name: ' + song_name + ' Artist :' + artist)

                # looks for the song in spotify, if not found does not add to playlist
                uri = self.get_spotify_uri(song_name, artist)
                if uri is None:
                    out_file.write('Song name: ' + song_name + ' Artist : ' + artist + ' Not found')
                    out_file.write('\n')
                    continue

                songs_added += 1
                self.all_song_info[video_title] = {
                        "youtube_url":youtube_url,
                        "song_name":song_name,
                        "artist":artist,
                        "spotify_uri":uri
                    }

            # continues in the next json page of api call
            if "nextPageToken" in response:
                next_key = response["nextPageToken"]
                request = self.youtube_client.videos().list(
                    part="snippet,contentDetails,statistics",
                    maxResults=2000,
                    myRating="like",
                    pageToken=next_key
                )
            else:
                has_next_key = False

        out_file.write('Total songs detected :' + str(songs_detected) + ' songs \n')
        out_file.write('Total songs added to playlist: ' + str(songs_added) + ' songs')
        out_file.close()

        print('Done getting the liked videos')

    # Gets the song name and artist from either the youtube music information or the title
    def get_song_info(self, youtube_url, video_title):
        if ' - ' in video_title:
            # print(video_title)
            artist = video_title.split(" - ")[0]
            song_name = video_title.split(" - ")[1]
            if '(' in str(song_name) and '(Ac' not in str(song_name):
                song_name = song_name.split(" (")[0]
            elif '[' in str(song_name):
                song_name = song_name.split(" [")[0]
            elif '|' in str(song_name):
                song_name = song_name.split(" |")[0]
            if 'ft.' in str(song_name):
                song_name = song_name.split("ft.")[0]
            if 'ft.' in str(artist):
                artist = artist.split("ft.")[0]
        else:
            res = requests.get(youtube_url)
            #print(video_title)
            song_name = re.search(r'"Song"\},"contents":\[\{"simpleText":"(.*?)"\}\],',res.text)
            artist = re.search(r'"Artist"\},"contents":\[\{"runs":\[\{"text":"(.*?)",',res.text)
        
            if artist is None:
                artist = re.search(r'"Artist"\},"contents":\[\{"simpleText":"(.*?)"\}\],',res.text)
                if artist is not None:
                    artist = artist.group(1)
            else:
                artist = artist.group(1)

            if song_name is None:
                song_name = re.search(r'"Song"\},"contents":\[\{"runs":\[\{"text":"(.*?)",',res.text)
                if song_name is not None:
                    song_name = song_name.group(1)
            else:
                song_name = song_name.group(1)

        # Song not found using any method above
        if song_name is None or artist is None:
            return artist, song_name

        return artist, song_name

    #3. Create new spotify playlist using the spotify api
    def create_playlist(self):
        request_body = json.dumps({
                    "name": "Youtube liked Videos",
                    "description": "All Liked Youtube Videos",
                    "public": True })
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        response_json = response.json()

        #playlist it
        return response_json["id"]


    #4. Search for songs in spotify 
    def get_spotify_uri(self, song_name, artist):
        query = "https://api.spotify.com/v1/search?q=track%3A{}%20artist%3A{}&type=track&offset=0&limit=20".format(song_name,artist)
        response = requests.get(
            query, 
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            })
        response_json = response.json()
        songs = response_json["tracks"]["items"]

        try:
            uri = songs[0]["uri"]
        except IndexError:
            #print('Different song name ')
            return None

        return uri

    #5. Add song to spotify playlist
    def add_song_to_spotify_playlist(self):
        #populate song dictionary
        self.get_liked_videos()
        #collect all of uri
        uri = []
        for song,info in self.all_song_info.items():
            uri.append(info["spotify_uri"])

        #create new playlist
        playlist_id = self.create_playlist()

        #add songs to playlist
        request_data = json.dumps(uri)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)

        response = requests.post(
            query,
            data=request_data, 
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )

        response_json = response.json()
        return response_json

if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.add_song_to_spotify_playlist()