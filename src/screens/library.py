from widgets.core import Plugin
from widgets.game import GameLibraryCard
from widgets.gamelist import Gamelist
from kivymd.uix.button import MDRectangleFlatButton
from kivy.clock import Clock

from database import Database

db = Database("games.db")


class Library(Plugin):
    name = "Library"
    icon = "bookshelf"
    def __init__(self, qbt_client, **kwargs):
        super().__init__(**kwargs)
        self.id = "library"
        
        self.qbt_client = qbt_client
        self.qbt_client.check_connection()
        
        self.gamelist = Gamelist()
        self.gamelist.search_bind(self.update_library)
        self.add_widget(self.gamelist)
        
        self.load_library()
        
        self.count_check = Clock.schedule_interval(self.check_counts, 5)
            
            
    def load_library(self, instance=None):
        if not self.qbt_client.is_connected():
            self.gamelist.add_widget(MDRectangleFlatButton(text="Please connect to Qbittorrent to view your library", on_press=self.update_library, size_hint=(None, None), size=(500, 100), pos_hint={"center_x": 0.5, "center_y": 0.5}))
            return
        torrs = self.qbt_client.get_torrents()
        for game in torrs:
            gameCard = GameLibraryCard(game_torrent=game, qbt_client=self.qbt_client)
            if getattr(instance, "text", "").lower() in gameCard.game_name.lower():
                self.gamelist.add_game(gameCard)
            else:
                gameCard = None
        if instance :
            instance.text = ""        
            
    def update_library(self, instance=None):
        if not self.qbt_client.is_connected():
            return
        self.gamelist.clear_list()
        self.load_library(instance)
  
    def check_counts(self, dt=None):
        try:
            torrents_count = self.qbt_client.count()
        except Exception as e:
            return
        if self.gamelist.game_count() > torrents_count:
            self.update_library()