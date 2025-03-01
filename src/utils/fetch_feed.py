import requests
import json
from .thread_with_return import ThreadWithReturnValue
from igdb.wrapper import IGDBWrapper
import os
import numpy as np
import time


class ReleasesFeed:
    def __init__(self,
                 twitch_client_id,
                 twitch_client_secret,
                 db_object):
        
        self.twitch_client_id = twitch_client_id
        self.twitch_client_secret = twitch_client_secret
        self.db = db_object
        
        self.feed_json_url = "https://github.com/jc141x/releases-feed/releases/latest/download/releases.json"
 
        r = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={self.twitch_client_id}&client_secret={self.twitch_client_secret}&grant_type=client_credentials")
        
        access_token = json.loads(r._content)["access_token"]

        self.igdb_wrapper = IGDBWrapper(f"{self.twitch_client_id}", access_token)
        
    
    def pipeline(self):
        
        feed = self.get_latest_feed()
        feed = self.format_feed(feed)
        
        feed = self.parallelize_update_game_records(feed)
        
        self.update_database(feed)
    
    
    def get_latest_feed(self):
        r = requests.get(self.feed_json_url)
        return r.json()
    
    def format_feed(self, feed):
        
        formated_feed = []
        
        schema = {
            "name": "",
            "size": "",
            "magnet": "",
            "pltfrm": "",
            "cover": "",
            "summary": "",
        }
        
        for record in feed:
            formated_feed.append(schema.copy())
            formated_feed[-1]["name"] = record["name"]
            formated_feed[-1]["size"] = record["total_size"]
            formated_feed[-1]["magnet"] = record["magnet_link"]    
            
        return formated_feed
    
    def get_cover_and_summary(self, game):
        
        game_info = self.db._get_game_info(game)
        
        if (game_info is not None):
            if game_info.cover is not None:
                return game_info.cover, game_info.description
        
        time.sleep(2)
        
        # JSON API request
        byte_array = self.igdb_wrapper.api_request(
            "games", f'search "{game}"; fields cover, summary; offset 0;'
        )
        # parse into JSON however you like...

        data = json.loads(byte_array)
        #print(data)

        if len(data) == 0:
            return "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/nocover.png", "No summary available"
        
        try:
            cover_id = int(data[0]["cover"])
            game_summary = data[0]["summary"]
        except KeyError:
            
            try:
                cover_id = int(data[1]["cover"])
                game_summary = data[1]["summary"]
            except Exception:
                return "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/nocover.png", "No summary available"        
        
        # cover url 
        byte_array = self.igdb_wrapper.api_request(
            "covers", f"fields url; where id = {cover_id};"
        )
        
        data = json.loads(byte_array)
        cover_url = "https:" + str(data[0]["url"]).replace("thumb", "1080p") 
        
        return cover_url, game_summary

    def update_game_records(self, json_array):
                
        num = len(json_array)
        
        # udate platform info
        for i in range(num):
            try:
                if "Wine" in json_array[i]["magnet"]:
                    json_array[i]["pltfrm"] = "wine"
                elif "Native" in json_array[i]["magnet"]:
                    json_array[i]["pltfrm"] = "native"
            except KeyError:
                continue

        # normalize game names and get cover art
        for i in range(num):
            try:
                if "-" in json_array[i]["name"]:
                    json_array[i]["name"] = json_array[i]["name"].split("-", 1)[0]
                else:
                    json_array[i]["name"] = json_array[i]["name"].split("[", 1)[0]

                
                if '\"' in json_array[i]["name"]:
                    continue
                
                #print(json_array[i]["no"])

                json_array[i]["cover"], json_array[i]["summary"] = self.get_cover_and_summary(
                    json_array[i]["name"].replace("–", "-").replace("’", "'")
                )
                time.sleep(1) 
            except KeyError:
                continue
        
        return json_array
    
    def parallelize_update_game_records(self, json_array):
        
        num = 10
        
        # split json array into 10 chunks
        chunks = np.array_split(json_array, num)
        
        # convert chunks to list
        chunks = [list(i) for i in chunks]
        
        results = [None] * num
        
        start = time.time()
        
        threads = []
        for i in range(num):
            threads.append(ThreadWithReturnValue(target=self.update_game_records, args=(chunks[i],)))
            threads[i].start()
            time.sleep(1)
            
        
        # join threads
        for i in range(num):
            results[i] = threads[i].join()
            
        end = time.time()
        print(f"parallelize_update_game_records took {end - start} seconds")
        # merge results
        json_array = []
        for i in range(num):
            if results[i] is not None:
                json_array.extend(results[i])
        
        return json_array

    def update_database(self, json_array):
        
        self.db.delete_all()
        
        num = len(json_array)
        
        for i in range(num):
            try:
                if json_array[i]["pltfrm"] == "wine" or json_array[i]["pltfrm"] == "native":
                    self.db.add_game(
                        json_array[i]["name"],
                        json_array[i]["cover"],
                        json_array[i]["size"],
                        json_array[i]["magnet"],
                        json_array[i]["pltfrm"],
                        json_array[i]["summary"],
                    )
            except KeyError:
                continue
        print("updating db done")


      