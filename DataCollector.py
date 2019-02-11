import json
import urllib.request

api_key = '359aa051532190aecabb2e638f0313c6'
api_secret = 'a5ced820a7e12b07d37782b9fa2ff405'
# Registered to tarmander13


class DataCollector:

    parseable_data = 0

    def __init__(self):
        target = "tarmander13"  # input("\nEnter last.fm username: ")
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" + target + \
              "&api_key=" + api_key + "&format=json"
        url_data = urllib.request.urlopen(url)
        self.parseable_data = json.load(url_data)
        total_pages = int(self.parseable_data['recenttracks']['@attr']['totalPages'])
        print(total_pages)
        print(self.parseable_data['recenttracks']['track'][0])
        # Start at 2: We have to call recent tracks to determine how many pages to fetch first page is already loaded.
        # Note: API pages start at 1, not 0
        i = 2
        # Just fetch 5 pages for now. Proof of concept
        while i < 5:  # total_pages:
            url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="\
                  + target + "&page=" + str(i) + \
                  "&api_key=" + api_key + "&format=json"
            url_data = urllib.request.urlopen(url)
            temp_data = json.load(url_data)
            temp_index = 0
            for numbered_track in temp_data['recenttracks']['track']:
                self.parseable_data['recenttracks']['track'].append(temp_data['recenttracks']['track'][temp_index])
                temp_index += 1
            print(i)
            i += 1

    def main(self):
        count = 0
        for track in self.parseable_data['recenttracks']['track']:
            count += 1
            print("Track #" + str(count) + ": " + track['artist']['#text'] + ": " + track['name'])
        print("Tracks loaded: " + str(count))


dc = DataCollector()
dc.main()