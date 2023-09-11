import qbittorrentapi
import os
import re
import time
from kivy.clock import Clock

class JCQbt:
    """
    A class to interact with qBittorrent, specifically for JC141 related downloads.
    """
    def __init__(self, host, port, username, password, save_path):
        
        os.system("qbittorrent &")
        
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        self.connected = False
        
        self.qbt_client = None
          
        self.init_client()
        self.save_path = save_path
        
        self.connection_check = Clock.schedule_interval(self.check_connection, 10)
        
    
    def init_client(self):
        if self.qbt_client is not None:
            self.qbt_client.log_out()
            
        
        self.qbt_client = qbittorrentapi.Client(host=self.host, port=self.port, username=self.username, password=self.password)
        self.check_connection()
            
    
    def check_connection(self, dt=None):
        try:
            self.qbt_client.auth_log_in()
            self.connected = True
        except Exception as e:
            print("\n--# Please make sure qBittorrent is running and the settings are correct. #--\n")
            self.connected = False
            
    # get all torrents with the tag "jc141"
    def get_torrents(self):
        return self.qbt_client.torrents_info(tag="jc141")
    
    # pause torrent
    def pause(self, url):
        return self.qbt_client.torrents_pause(torrent_hashes=self.get_hash(url))
    
    # resume torrent
    def resume(self, url):
        return self.qbt_client.torrents_resume(torrent_hashes=self.get_hash(url))
    
    # delete torrent
    def delete(self, url, delete_files=False):
        return self.qbt_client.torrents_delete(torrent_hashes=self.get_hash(url), delete_files=delete_files)

    # download torrent, add tag "jc141" to easily identify
    def download(self, url):
        return self.qbt_client.torrents_add(urls=url, tags="jc141", save_path=self.save_path)
    
    # get torrent hash from magnet link
    def get_hash(self, url):
        return re.findall(r"magnet:\?xt=urn:btih:([a-zA-Z0-9]+)", url)[0]
    
    # get torrent with hash
    def get_torrent(self, url):
        return self.qbt_client.torrents_info(torrent_hashes=self.get_hash(url))[0]

    def is_connected(self):
        return self.connected
    
    def count(self):
        return len(self.get_torrents())