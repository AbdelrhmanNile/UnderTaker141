from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.image import AsyncImage
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout

from kivymd.uix.list import MDList, ImageLeftWidgetWithoutTouch, IconRightWidget, OneLineAvatarIconListItem

from kivy.clock import Clock
from utils import JCQbt, get_settings
from database import Database
import os


db = Database("games.db")

settings = get_settings()
qbt = JCQbt(host=settings["qbittorrent_api"]["host"], 
            port=settings["qbittorrent_api"]["port"], 
            username=settings["qbittorrent_api"]["username"], 
            password=settings["qbittorrent_api"]["password"],
            save_path=settings["general"]["save_path"])

class GameCard(MDCard):
    def __init__(self, game_obj, **kwargs):
        super().__init__(**kwargs)
        
        self.game_obj = game_obj
        
        #self.scr_mngr = scr_mngr
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (170, 270)
        
        self.md_bg_color = "#00000000"
        
        self.name = MDLabel(text=game_obj.name if len(game_obj.name) < 13 else game_obj.name[:11] + "..", halign="left", size_hint=(0.6, 0.1))
        self.cover = AsyncImage(source=game_obj.cover)
        self.magnet = game_obj.magnet 
        
        self.add_widget(self.cover)
        self.add_widget(self.name)
                
    def on_press(self):
        
        text = f"Description: \n{self.game_obj.description}\n\n" \
                f"Size: {self.game_obj.size}\n\n" \
                f"Platform: {self.game_obj.platform}\n\n"
        
        dia = MDDialog(title=self.game_obj.name, 
                       text=text,
                       buttons=[
                           MDRectangleFlatButton(text="Download", on_press=self.download)
                        ],
                       )
        
        dia.open()
        
        
    def download(self, instance: MDRectangleFlatButton):
        qbt.download(self.magnet)
        instance.text = "Downloading..."
        instance.disabled = True
        
        library = self.parent.parent.parent.parent.parent.get_screen("Library")
        library.layout.add_widget(GameLibraryItem(game_torrent=qbt.get_torrent(self.magnet)))
        




class GameLibraryItem(OneLineAvatarIconListItem):
    def __init__(self, game_torrent,  **kwargs):
        super().__init__(**kwargs)
        
        self.text = str(game_torrent.name).split("-")[0]
        #self.magnet = game_torrent.magnet_uri
        
        self.game_obj = db.get_game(self.text)[0]
        self.torr = None
        self.magnet = self.game_obj.magnet
        #self.text = game_obj.name
        self.cover_link = self.game_obj.cover
        self.save_path = game_torrent.content_path
        self.status = game_torrent.state
        
        
        self._txt_bot_pad = "240dp"
        self.font_style = "H5"
        self.ids._lbl_primary.pos_hint = {"x": 0.3}
        self.ids._right_container.width = self.width
        self.size_hint = (None, None)
        self.size = (550, 300)
       
        self.pos_hint = {"center_x": 0.5, "center_y":0.5}
        
        self.manage_dialog = MDDialog(title=self.game_obj.name,
                          text=" ",
                          buttons=[
                              MDRectangleFlatButton(text="Open Location", on_press=self.open_location),
                              MDRectangleFlatButton(text="Pause", on_press=lambda x: qbt.pause(self.magnet)),
                                MDRectangleFlatButton(text="Resume", on_press=lambda x: qbt.resume(self.magnet)),
                              MDRectangleFlatButton(text="Close", on_press=lambda x: self.dismiss_dialog())
                              ])
         
        
        self.cover_img = ImageLeftWidgetWithoutTouch(source=self.cover_link, size_hint=(None, None), size=(170,270), pos_hint={"center_x":0.5, "center_y":0.5})
        self.add_widget(self.cover_img)
        
        self.manage_icon = IconRightWidget(icon="file-cog", on_press=lambda x: self.manage_dialog.open())
        self.add_widget(self.manage_icon)
        
        self.run_icon = IconRightWidget(icon="play", disabled=True)
        self.run_icon.bind(on_press=self.launch_game)
        self.add_widget(self.run_icon)

        
        self.disabled_states = ["metaDL", "pausedDL", "queuedDL", "stalledDL", "checkingDL", "forcedDL", "downloading"]
        

        self.clock = Clock.schedule_interval(self.update_status, 5)
        
    def on_icon_press(self, instance):
        print("pressed")
        
    def update_status(self, dt=None):
        
        self.torr = qbt.get_torrent(self.magnet)
        
        text = f"State: {self.torr.state}\n" \
                f"Download Progress: {self.torr.progress*100:.2f}%\n" \
                 f"Download Speed: {int(int(self.torr.dlspeed)/1000)} kB/s\n" \
                  f"ETA: {int(int(self.torr.eta)/60)} min\n"
                  
        self.manage_dialog.text = text 
        
        if self.torr.state in self.disabled_states:
            self.run_icon.disabled = True
            
            if self.torr.state == "downloading":
                self.text = f"{self.game_obj.name} - {self.torr.progress*100:.2f}%"
                self.save_path = self.torr.content_path        
        else:
            self.text = self.game_obj.name
            self.run_icon.disabled = False
            
    def open_location(self, instance):
        os.system(f"xdg-open {self.save_path} &")
    
    def launch_game(self, instance):
        os.system(f"cd {self.save_path} && chmod +x start* && ./start* &")
        
    def dismiss_dialog(self):
        self.manage_dialog.dismiss()
        