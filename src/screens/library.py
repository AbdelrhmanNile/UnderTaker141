from widgets.core import Plugin
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from widgets.game import GameLibraryCard
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.list import MDList
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRectangleFlatButton
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
    def __init__(self, qbt_client, **kwargs):
        super().__init__(**kwargs)
        self.id = "library"
        
        self.qbt_client = qbt_client
        
        self.layout = MDGridLayout(cols=8, padding="12dp", spacing="30dp", adaptive_height=True, adaptive_width=True)
        
        self.scroll = MDRecycleView()
                
        self.scroll.add_widget(self.layout)
        
        self.add_widget(self.scroll)
        
        if self.qbt_client.is_connected():
            self.load_library()
        else:
            self.layout.add_widget(MDRectangleFlatButton(text="Please connect to Qbittorrent to view your library", on_press=self.update_library, size_hint=(None, None), size=(500, 100), pos_hint={"center_x": 0.5, "center_y": 0.5}))
                
            
            
    def load_library(self):
        if not self.qbt_client.is_connected():
            return
        torrs = self.qbt_client.get_torrents()
        for game in torrs:
            self.layout.add_widget(GameLibraryCard(game_torrent=game, qbt_client=self.qbt_client))            
            
    def update_library(self, instance=None):
        if not self.qbt_client.is_connected():
            return
        self.layout.clear_widgets()
        self.load_library()