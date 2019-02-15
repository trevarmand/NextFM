import json
import urllib.request

api_key = '359aa051532190aecabb2e638f0313c6'
api_secret = 'a5ced820a7e12b07d37782b9fa2ff405'
# Registered to tarmander13


class DataCollector:

    parseable_data = 0
    tracks_loaded = 0

    def __init__(self):
        import time
        target = "tarmander13"  # input("\nEnter last.fm username: ")
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" + target + \
              "&api_key=" + api_key + "&format=json&limit=200"
        url_data = urllib.request.urlopen(url)
        self.parseable_data = json.load(url_data)
        total_pages = int(self.parseable_data['recenttracks']['@attr']['totalPages'])
        print("Total Pages: " + str(total_pages))

        api_totaltime = 0

        # Start at 2: We have to call recent tracks to determine how many pages to fetch first page is already loaded.
        # Note: API pages start at 1, not 0
        i = 2
        fail_attempts = 0
        # Just fetch 5 pages for now. Proof of concept
        while i < total_pages:  # total_pages:
            start = time.time()
            url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="\
                  + target + "&page=" + str(i) + \
                  "&api_key=" + api_key + "&format=json&limit=200"
            try:
                url_data = urllib.request.urlopen(url)
            except urllib.error.HTTPError:
                if fail_attempts > 5:
                    print("Server Error, loading failed")
                else:
                    time.sleep(0.5)
                    print("Server issue fetching page, retrying: " + str(fail_attempts) + "/5")
                    continue  # Start the loop again, i doesn't increase so just retries the current page
            temp_data = json.load(url_data)
            api_totaltime += time.time() - start
            temp_data['recenttracks']['track'].pop(0)  # Don't include current track in data
            self.parseable_data['recenttracks']['track'].extend(temp_data['recenttracks']['track'])
            print("Loaded page " + str(i))
            i += 1
        print("Average api response time: " + str(round(api_totaltime / (i - 1), 3)))

    def main(self):
        self.tracks_loaded = len(self.parseable_data['recenttracks']['track'])
        print("Tracks loaded: " + str(self.tracks_loaded))
        self.most_played_song()
        self.most_played_artist()
        self.played_on_repeat()

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
        print("Number of plays: " + str(last_count))

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
        print(top_artist + " consumed " + str(round(top_count / self.tracks_loaded, 3) * 100) + "% of your listening")

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
        print("Number of plays: " + str(last_count))


dc = DataCollector()
dc.main()