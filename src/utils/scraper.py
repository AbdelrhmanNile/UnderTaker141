import threading
import csv
import json
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from igdb.wrapper import IGDBWrapper
from .thread_with_return import ThreadWithReturnValue
import time
import os
import re

DEBUGGING = False

class JohnCena141Scraper:
    def __init__(
        self,
        csv_name,
        twitch_client_id,
        twitch_client_secret,
        db_object,
        page_limit=None
    ):
        self.start_page_num = 1
        self.csv_name = csv_name
        
        if page_limit is None:
            self.page_limit = self.get_num_pages()
        else:
            self.page_limit = page_limit
        
        self.twitch_client_id = twitch_client_id
        self.twitch_client_secret = twitch_client_secret
        
        self.db = db_object
        self.reset_lists()


    def get_num_pages(self):
        link = "https://1337x.to/johncena141-torrents/1/"
        page = requests.get(link)
        soup = BeautifulSoup(page.content, "lxml")
        last_page_element = soup.find("li", class_="last")
        href = last_page_element.find("a")["href"]
        last_page_num = re.findall(r"/johncena141-torrents/([0-9]+)/", href)[0]
        return int(last_page_num)

    
    def reset_lists(self):
        self.urllist = []
        self.filenamelist = []
        self.seederlist = []
        self.leecherlist = []
        self.sizelist = []
        self.datelist = []
        self.splitarr = []
        self.magnetlinks = []

    def task1(self):
        for url1 in self.splitarr[0]:
            self.scrape_individual(url1)

    def task2(self):
        for url2 in self.splitarr[1]:
            self.scrape_individual(url2)

    def task3(self):
        for url3 in self.splitarr[2]:
            self.scrape_individual(url3)

    def scrape_individual(self, url):
        source = requests.get(url).text
        soup = BeautifulSoup(source, "lxml")

        leftside = []
        rightside = []

        for h1_tag in soup.find("h1"):
            self.filenamelist.append(h1_tag)

        for ul_tag in soup.find_all("ul", {"class": "list"}):
            for li_tag in ul_tag.find_all("li"):
                leftside.extend(
                    strong_tag.text for strong_tag in li_tag.find_all("strong")
                )
                rightside.extend(span_tag.text for span_tag in li_tag.find_all("span"))

        combined = np.column_stack([leftside, rightside])

        for each_detail in combined:
            if "Seeders" in each_detail[0]:
                self.seederlist.append(each_detail[1])
            if "Leechers" in each_detail[0]:
                self.leecherlist.append(each_detail[1])
            if "Total size" in each_detail[0]:
                self.sizelist.append(each_detail[1])
            if "Date uploaded" in each_detail[0]:
                self.datelist.append(each_detail[1])
        self.magnetlinks.append(
            soup.find(string="Magnet Download").find_parent("a").get("href")
        )

    def run(self):
        print("scrapping for games")

        while True:
            if self.start_page_num == self.page_limit:
                print("scrapping is done")
                self.clean()
                json_data = self.to_json()
                self.push_to_db(json_data)
                
                # delete csv
                os.remove(f"{self.csv_name}.csv")

                exit()
            else:
                source = requests.get(
                    f"https://1337x.to/johncena141-torrents/{self.start_page_num}/"
                ).content
                soup = BeautifulSoup(source, "lxml")

                tablebody = soup.find("tbody")
                # extract page links for every torrent and store it in an array
                for tag in tablebody.find_all("a"):
                    temp_url = tag.get("href").split("/")
                    if "torrent" in temp_url[1]:
                        self.urllist.append("https://1337x.to" + (tag.get("href")))

                # split array for parralel scraping
                self.splitarr = np.array_split(self.urllist, 3)

                t1 = threading.Thread(target=self.task1, name="t1")
                t2 = threading.Thread(target=self.task2, name="t2")
                t3 = threading.Thread(target=self.task3, name="t3")

                t1.start()
                t2.start()
                t3.start()

                t1.join()
                t2.join()
                t3.join()

                combined = np.column_stack(
                    [
                        self.filenamelist,
                        self.seederlist,
                        self.leecherlist,
                        self.sizelist,
                        self.datelist,
                        self.magnetlinks,
                    ]
                )
                df = pd.DataFrame(combined)

                df.to_csv(f"{self.csv_name}.csv", mode="a", index=False)
                self.start_page_num += 1
                self.reset_lists()

    def clean(self):
        print("cleaning dataset")
        df = pd.read_csv(f"{self.csv_name}.csv")
        df = df.loc[df["0"] != "0"]
        df = df.loc[df["3"] != "0"]
        df = df.loc[df["3"] != "1"]


        ### adding readable column names
        data = [
            {
                "no": "",
                "name": "",
                "seeders": "",
                "leechers": "",
                "size": "",
                "date": "",
                "magnet": "",
                "pltfrm": "",
                "cover": "",
                "summary": "",
            }
        ]
        df_data = pd.DataFrame(data)
        df_data.to_csv(f"{self.csv_name}.csv", mode="w", index=False)

        df.to_csv(f"{self.csv_name}.csv", mode="a", index=True)
        print("cleaning is done")

    def to_json(self):
        print("converting csv to json")
        data = []
        # Open a csv reader called DictReader
        with open(f"{self.csv_name}.csv", encoding="utf-8") as csvf:
            csvReader = csv.DictReader(csvf)
            for rows in csvReader:
                data.append(rows)

        # remove first 2 rows
        data = data[2:]
        
        #with open(f"{self.csv_name}.json", "w", encoding="utf-8") as jsonf:
        #    jsonf.write(json.dumps(data, indent=4))

        print("converting to json is done")

        ## update pltfrm and trim name and get cover art
        return self.parallelize_update_game_records(data)

    def get_cover_and_summary(self, game):
        
        
        game_info = self.db._get_game_info(game)
        
        if (game_info is not None):
            if game_info.cover is not None:
                return game_info.cover, game_info.description
        
        time.sleep(2)
        
        r = requests.post(
            f"https://id.twitch.tv/oauth2/token?client_id={self.twitch_client_id}&client_secret={self.twitch_client_secret}&grant_type=client_credentials"
        )

        access_token = json.loads(r._content)["access_token"]

        wrapper = IGDBWrapper(f"{self.twitch_client_id}", access_token)

        # JSON API request
        byte_array = wrapper.api_request(
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
        byte_array = wrapper.api_request(
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

        if DEBUGGING:
            # save json
            with open(f"{self.csv_name}.json", "w", encoding="utf-8") as jsonf:
                jsonf.write(json.dumps(json_array, indent=4))
        
        return json_array

    def push_to_db(self, json_array):
        
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
        print("pushing to db done")
        
        
    def parallelize_update_game_records(self, json_array):
        
        num = 20
        
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
            json_array.extend(results[i])
        
        return json_array
    