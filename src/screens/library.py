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
import time

db = Database("games.db")


class Library(Plugin):
    name = "Library"
    icon = "bookshelf"
    def __init__(self, qbt_client, **kwargs):
        super().__init__(**kwargs)
        self.id = "library"
        
        self.qbt_client = qbt_client
        self.qbt_client.check_connection()
        
        self.layout = MDGridLayout(cols=8, padding="12dp", spacing="30dp", adaptive_height=True, adaptive_width=True)
        
        self.scroll = MDRecycleView()
                
        self.scroll.add_widget(self.layout)
        
        self.add_widget(self.scroll)
        
        self.load_library()
        
        self.count_check = Clock.schedule_interval(self.check_counts, 1)
            
            
    def load_library(self):
        if not self.qbt_client.is_connected():
            self.layout.add_widget(MDRectangleFlatButton(text="Please connect to Qbittorrent to view your library", on_press=self.update_library, size_hint=(None, None), size=(500, 100), pos_hint={"center_x": 0.5, "center_y": 0.5}))
            return
        torrs = self.qbt_client.get_torrents()
        for game in torrs:
            self.layout.add_widget(GameLibraryCard(game_torrent=game, qbt_client=self.qbt_client))            
            
    def update_library(self, instance=None):
        if not self.qbt_client.is_connected():
            return
        self.layout.clear_widgets()
        self.load_library()
        
    def library_count(self):
        return len(self.layout.children)
    
    def check_counts(self, dt=None):
        try:
            torrents_count = self.qbt_client.count()
        except Exception as e:
            return
        if self.library_count() > torrents_count:
            self.update_library()