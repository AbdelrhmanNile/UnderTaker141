from widgets.core import Plugin
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from widgets.game import GameLibraryCard
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.list import MDList
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from utils import JCQbt
from utils import get_settings

from database import Database

db = Database("games.db")

settings = get_settings()
qbt = JCQbt(host=settings["qbittorrent_api"]["host"],
            port=settings["qbittorrent_api"]["port"],
            username=settings["qbittorrent_api"]["username"],
            password=settings["qbittorrent_api"]["password"],
            save_path=settings["general"]["save_path"])

class Library(Plugin):
    name = "Library"
    icon = "bookshelf"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = "library"
        
        self.layout = MDGridLayout(cols=8, padding="12dp", spacing="30dp", adaptive_height=True, adaptive_width=True)
        
        self.scroll = MDRecycleView()
                
        self.scroll.add_widget(self.layout)
        
        self.add_widget(self.scroll)
        
        
        self.load_library()
                
            
            
    def load_library(self):
        torrs = qbt.get_torrents()
        for game in torrs:
            self.layout.add_widget(GameLibraryCard(game_torrent=game))            
            
    def update_library(self):
        self.list.clear_widgets()
        self.load_library()