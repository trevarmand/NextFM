import json
import urllib.request

api_key = '359aa051532190aecabb2e638f0313c6'
api_secret = 'a5ced820a7e12b07d37782b9fa2ff405'
# Registered to tarmander13

class DataCollector:

    parseable_data = 0

    def __init__(self):
        target = "tarmander13"  # input("\nEnter last.fm username: ")
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" + target + "&api_key=" + api_key + "&format=json"
        url_data = urllib.request.urlopen(url)
        self.parseable_data = json.load(url_data)

    def main(self):
        count = 0
        print(self.parseable_data)
        for track in self.parseable_data['recenttracks']["track"]:
            count += 1
            print(track["artist"]["#text"] + ": " + track["name"])
        print("Tracks per page: " + str(count))

dc = DataCollector()
dc.main()