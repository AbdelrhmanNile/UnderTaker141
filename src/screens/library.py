from widgets.core import Plugin
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from widgets.game import GameLibraryItem
from kivy.uix.scrollview import ScrollView
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
        # main layout
        self.layout = MDBoxLayout(orientation="vertical", padding="50dp", id="lib_layout")
        self.add_widget(self.layout)
        
        # Games list
        self.scroll = ScrollView()
        self.list = MDList(padding="12dp", spacing="12dp", id="lib_list")
                
        self.scroll.add_widget(self.list)
        self.layout.add_widget(self.scroll)
        
        
        self.load_library()
        
        #Clock.schedule_interval(lambda dt: self.update_library(), 1)
        
            
            
    def load_library(self):
        torrs = qbt.get_torrents()
        for game in torrs:
            self.list.add_widget(GameLibraryItem(game_torrent=game))
            
    def update_library(self):
        self.list.clear_widgets()
        self.load_library()