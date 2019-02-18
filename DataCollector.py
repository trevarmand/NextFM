import json
import urllib.request

# Registered to tarmander13


class DataCollector:

    parseable_data = 0
    tracks_loaded = 0

    def __init__(self):
        import time
        from API_Credentials import api_key
        target = input("\nEnter last.fm username: ")
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" + target + \
              "&api_key=" + api_key + "&format=json&limit=200"
        url_data = urllib.request.urlopen(url)
        self.parseable_data = json.load(url_data)
        total_pages = int(self.parseable_data['recenttracks']['@attr']['totalPages'])
        print("Total Pages: " + str(total_pages))

        api_total_time = 0

        # Start at 2: We have to call recent tracks to determine how many pages to fetch first page is already loaded.
        # Note: API pages start at 1, not 0
        i = 2
        fail_attempts = 0
        while i <= total_pages:  # total_pages:
            start = time.time()
            url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="\
                  + target + "&page=" + str(i) + \
                  "&api_key=" + api_key + "&format=json&limit=200"
            try:
                url_data = urllib.request.urlopen(url)
            except urllib.error.HTTPError:
                if fail_attempts > 5:
                    print("Server Error, loading failed")
                    fail_attempts += 1
                else:
                    time.sleep(0.5)
                    print("Server issue fetching page, retrying: " + str(fail_attempts) + "/5")
                    continue  # Start the loop again, i doesn't increase so just retries the current page
            temp_data = json.load(url_data)
            api_total_time += time.time() - start
            temp_data['recenttracks']['track'].pop(0)  # Don't include current track in data
            self.parseable_data['recenttracks']['track'].extend(temp_data['recenttracks']['track'])
            print("Loaded page " + str(i))
            i += 1
        print("\nAverage api response time: " + str(round(api_total_time / (i - 1), 3)))

    def main(self):
        self.tracks_loaded = len(self.parseable_data['recenttracks']['track'])
        print("Tracks loaded: " + str(self.tracks_loaded) + "\n")
        self.take_input()

    # Prompt the user for input so they can gather insights on their listening
    def take_input(self):
        next_in = input("Enter command, or HELP for help: ")
        if next_in.lower() == 'help':
            print("\nCommands available:\ntop_track\ntop_artist\non_repeat"
                  "\nsong_play_count (song)\ntrack_by_artist (artist)\nalbum_by_artist (artist)\nsong_by_album (album)")
        elif next_in == 'top_track':
            self.most_played_song()
        elif next_in == 'top_artist':
            self.most_played_artist()
        elif next_in == 'on_repeat':
            self.played_on_repeat()
        elif next_in.__contains__('song_play_count'):
            self.song_play_count(next_in[16:])
        elif next_in.__contains__('track_by_artist'):
            self.top_track_by_artist(next_in[14:])
        elif next_in.__contains__('album_by_artist'):
            self.album_by_artist(next_in[16:])
        elif next_in.__contains__('song_by_album'):
            self.song_by_album(next_in[14:])
        self.take_input()

    # Prints the most played song by artist and number of times
    def most_played_song(self):
        track_counts = {}
        last_count = 0
        top_track = "jjju"
        top_artist = "jjju"
        for track in self.parseable_data['recenttracks']['track']:
            cur_track = track['name']
            track_counts[cur_track] = track_counts.get(cur_track, 0) + 1
            if track_counts.get(cur_track) > last_count:
                top_track = cur_track
                top_artist = track['artist']['#text']
                last_count = track_counts.get(cur_track)
        print("\nTop track: " + str(top_track) + " by " + top_artist)
        print("Number of plays: " + str(last_count) + "\n")

    # Prints the most played artist and number of plays, and the % of total plays they owned
    def most_played_artist(self):
        artist_counts = {}
        top_count = 0
        top_artist = "jjju"
        for track in self.parseable_data['recenttracks']['track']:
            artist_name = track['artist']['#text']
            artist_counts[artist_name] = artist_counts.get(artist_name, 0) + 1
            if artist_counts.get(artist_name) > top_count:
                top_artist = artist_name
                top_count = artist_counts.get(artist_name, 0)
        print("\nTop artist: " + top_artist)
        print("Number of plays: " + str(top_count))
        print(top_artist + " consumed " + str(round(top_count / self.tracks_loaded, 3) * 100) + "% of your listening\n")

    # Prints the most repeated song and the number of repeats
    def played_on_repeat(self):
        track_counts = {}
        cur_count = 0
        last_count = 0
        most_repreated = "jjju"
        prev_track = "jjju"
        top_artist = "jjju"
        for track in self.parseable_data['recenttracks']['track']:
            if track['name'] == prev_track:
                cur_count += 1
                track_counts[track['name']] = max(track_counts.get(track['name'], 0), cur_count)
                if cur_count > last_count:
                    most_repreated = track['name']
                    top_artist = track['artist']['#text']
                    last_count = track_counts.get(track['name'])
            else:
                cur_count = 0
            prev_track = track['name']
        print("\nMost Repeated: " + str(most_repreated) + " by " + top_artist)
        print("Number of plays: " + str(last_count) + "\n")

    # Prints your most played track for the specified artist
    def top_track_by_artist(self, artist):
        track_counts = {}
        last_count = 0
        top_track = "Null"
        for track in self.parseable_data['recenttracks']['track']:
            if track['artist']['#text'].lower() == artist.lower():
                cur_track = track['name']
                track_counts[cur_track] = track_counts.get(cur_track, 0) + 1
                if track_counts.get(cur_track) > last_count:
                    top_track = cur_track
                    last_count = track_counts.get(cur_track)
        if last_count == 0:
            print("No tracks found for " + artist)
        else:
            print("\nTop track for " + artist + ": " + str(top_track))
            print("Number of plays: " + str(last_count) + "\n")

    # Prints the number of times you played the specified song
    def song_play_count(self, song):
        count = 0
        for track in self.parseable_data['recenttracks']['track']:
            if track['name'].lower() == song.lower():
                count += 1
        print("You listened to " + song + " " + str(count) + " times\n")

    # Tells you your favorite album from the specified artist
    def album_by_artist(self, artist):
        album_counts = {}
        top_album = "null"
        cur_max = 0
        for track in self.parseable_data['recenttracks']['track']:
            if track['artist']['#text'].lower() == artist.lower():
                album_counts[track['album']['#text']] = album_counts.get(track['album']['#text'], 0) + 1
                if album_counts[track['album']['#text']] > cur_max:
                    top_album = track['album']['#text']
                    cur_max = album_counts[track['album']['#text']]
        if cur_max == 0:
            print("You haven't listened to this artist")
        else:
            print("Your top album from " + artist + " is " + top_album + ", with " + str(cur_max) + " listens\n")

    # Tells you your favorite song from a given album
    def song_by_album(self, album):
        song_counts = {}
        top_song = "null"
        cur_max = 0
        for track in self.parseable_data['recenttracks']['track']:
            if track['album']['#text'].lower() == album.lower():
                song_counts[track['name']] = song_counts.get(track['name'], 0) + 1
                if song_counts[track['name']] > cur_max:
                    top_song = track['name']
                    cur_max = song_counts[track['name']]
        if cur_max == 0:
            print("You haven't listened to this album")
        else:
            print("Your top track from " + album + " is " + top_song + " with " + str(cur_max) + " plays\n")


dc = DataCollector()
dc.main()