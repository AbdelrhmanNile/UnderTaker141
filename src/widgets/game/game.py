from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.image import AsyncImage
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, ImageLeftWidgetWithoutTouch, IconRightWidget, OneLineAvatarIconListItem
from kivymd.color_definitions import colors
from kivymd.toast.kivytoast.kivytoast import toast

from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from utils import JCQbt, get_settings
from database import Database
import os
import html

from widgets.border import BorderBehavior


db = Database("games.db")

settings = get_settings()


class GameCard(MDCard, BorderBehavior):
    def __init__(self, game_obj, qbt_client, **kwargs):
        super().__init__(**kwargs)
        
        self.borders = (1, 'solid', get_color_from_hex(colors["BlueGray"]["600"]))
        
        self.game_obj = game_obj
        
        self.qbt_client = qbt_client
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (200, 300)
        
        self.md_bg_color = "#00000000"
        
        self.name = MDLabel(text=game_obj.name if len(game_obj.name) < 13 else game_obj.name[:15] + "..", halign="left", size_hint=(1, 0.1), padding=(5, 0))
        self.cover = AsyncImage(source=game_obj.cover, size_hint=(0.9, 0.9), pos_hint={"center_x":0.5, "center_y":0.5})
        self.magnet = game_obj.magnet 
        
        self.add_widget(self.cover)
        self.add_widget(self.name)
                
    def on_press(self):
        
        text = f"Description: \n{self.game_obj.description}\n\n" \
                f"Size: {self.game_obj.size}\n\n" \
                f"Platform: {self.game_obj.platform.title()}\n\n"
        
        qbt_connected = self.qbt_client.is_connected()
        
        dia = MDDialog(title=self.game_obj.name, 
                       text=text,
                       buttons=[
                           MDRaisedButton(text="Download" if qbt_connected else "Please connect to Qbittorrent to download", on_press=self.download, disabled=not qbt_connected),
                        ],
                       )
        
        dia.open()
        
        
    def download(self, instance):
        self.qbt_client.download(self.magnet)
        instance.text = "Downloading..."
        toast(f"Downloading {self.game_obj.name} ...", duration=3.0)
        instance.disabled = True
        
        library = self.parent.parent.parent.parent.parent.get_screen("Library")
        library.layout.add_widget(GameLibraryCard(game_torrent=self.qbt_client.get_torrent(self.magnet), qbt_client=self.qbt_client))
        


class GameLibraryCard(MDCard, BorderBehavior):
    def __init__(self, game_torrent, qbt_client, **kwargs):
        super().__init__(**kwargs)
        
        self.borders = (1, 'solid', get_color_from_hex(colors["BlueGray"]["600"]))
        
        self.qbt_client = qbt_client
        
        self.game_name = str(game_torrent.name).split("-")[0]
        self.game_obj = self.query_game(self.game_name)
        
        self.torr = None
        self.magnet = game_torrent.magnet_uri
        self.cover_link = self.game_obj.cover
        self.save_path = game_torrent.content_path
        self.status = game_torrent.state
        
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (200, 300)
        
        self.md_bg_color = "#00000000"
        
        self.cover = AsyncImage(source=self.cover_link, size_hint=(0.9, 0.9), pos_hint={"center_x":0.5, "center_y":0.5})
        self.add_widget(self.cover)
        
        self.buttons = MDBoxLayout(orientation="horizontal", size_hint=(1, 0.1), pos_hint={"center_x":0.5, "center_y":0.5})
        
        self.run_btn = MDIconButton(icon="play", on_press=self.launch_game)
        self.buttons.add_widget(self.run_btn)
        
                
        
        self.manage_dialog = MDDialog(title=self.game_obj.name,
                            text=" ",
                            buttons=[
                                MDRaisedButton(text="Open Location", on_press=self.open_location),
                                MDRaisedButton(text="Pause", on_press=lambda x: self.qbt_client.pause(self.magnet)),
                                MDRaisedButton(text="Resume", on_press=lambda x: self.qbt_client.resume(self.magnet)),
                                MDRaisedButton(text="Delete", on_press=lambda x: self.delete(self.magnet), md_bg_color=colors["Red"]["500"]),
                                MDRaisedButton(text="Close", on_press=lambda x: self.dismiss_dialog())
                                ])
        
        self.manage_btn = MDIconButton(icon="file-cog", on_press=lambda x: self.manage_dialog.open())
        self.buttons.add_widget(self.manage_btn)
        
        self.add_widget(self.buttons)

        
        self.disabled_states = ["metaDL", "pausedDL", "queuedDL", "stalledDL", "checkingDL", "forcedDL", "downloading"]
        
        self.clock = Clock.schedule_interval(self.update_status, 5)
        
        
    def update_status(self, dt=None):
            
            connected = self.qbt_client.is_connected()
            
            for i in range(1, len(self.manage_dialog.buttons) - 1):
                self.manage_dialog.buttons[i].disabled = not connected
            
            if not connected:
                text = "qBittorrent not connected, please connect ..."
                self.manage_dialog.text = text
                return
            
            self.torr = self.qbt_client.get_torrent(self.magnet)
            
            progress = f"{self.torr.progress*100:.1f}%"
            speed = f"{self.torr.dlspeed//1000} KB/s"
            eta = self.torr.eta//60
            eta = f"{eta} min" if eta != 144000 else "∞"
            text = f"State: {self.torr.state}\n" \
                    f"Download Progress: {progress}\n" \
                    f"Download Speed: {speed}\n" \
                    f"ETA: {eta}\n"
                    
            self.manage_dialog.text = text 
            
            if self.torr.state in self.disabled_states:
                self.run_btn.disabled = True
                if self.torr.state == "downloading":
                    self.save_path = self.torr.content_path
            else:
                self.run_btn.disabled = False
    
    def launch_game(self, instance):
        os.system(f"cd {self.save_path} && chmod +x start* && ./start* &")
        
    def open_location(self, instance):
        os.system(f"xdg-open {self.save_path} &")
        
    def dismiss_dialog(self):
        self.manage_dialog.dismiss()
        
    def query_game(self, name):
        name = html.unescape(name)
        query_result = db.get_library_game(name)
        if len(query_result) == 1:
            return query_result[0]
        
        for q in query_result:
            if q.name.strip() == name.strip():
                return q
            
        partial_name = name.split(" ")
        partial_name = partial_name[:len(partial_name)//2]
        partial_name = " ".join(partial_name)
        return db.get_library_game(partial_name)[0]
    
    def delete(self, magnet):
        self.clock.cancel()
        self.qbt_client.delete(magnet, delete_files=True)
        self.manage_dialog.dismiss()
        self.parent.remove_widget(self)