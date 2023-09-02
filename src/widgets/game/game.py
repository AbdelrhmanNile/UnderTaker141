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
        library.list.add_widget(GameLibraryItem(game_torrent=qbt.get_torrent(self.magnet)))
        




class GameLibraryItem(OneLineAvatarIconListItem):
    def __init__(self, game_torrent,  **kwargs):
        super().__init__(**kwargs)
        
        self.disabled = True
        
        self.text = str(game_torrent.name).split("-")[0]
        #self.magnet = game_torrent.magnet_uri
        
        self.game_obj = db.get_game(self.text)[0]
        self.magnet = self.game_obj.magnet
        #self.text = game_obj.name
        self.cover_link = self.game_obj.cover
        self.save_path = game_torrent.content_path
        self.status = game_torrent.state
        
        
        self._txt_bot_pad = "240dp"
        self.font_style = "H4"
        self.ids._lbl_primary.pos_hint = {"x": 0.3}
        self.ids._right_container.width = self.width
        self.size_hint = (1, None)
        self.size = (1, 300)
        
        
        self.cover_img = ImageLeftWidgetWithoutTouch(source=self.cover_link, size_hint=(None, None), size=(170,270), pos_hint={"center_x":0.5, "center_y":0.5})
        self.add_widget(self.cover_img)
        
        #self.delete_icon = IconRightWidget(icon="delete")
        #self.add_widget(self.delete_icon)
                
        self.open_location_icon = IconRightWidget(icon="folder-open")
        self.open_location_icon.bind(on_press=self.open_location)
        self.add_widget(self.open_location_icon)
        
        self.run_icon = IconRightWidget(icon="play")
        self.run_icon.bind(on_press=self.launch_game)
        self.add_widget(self.run_icon)
        
        self.info_label = MDLabel(text=f"\n{self.status}", size_hint=(1, 0.1), pos_hint={"x":0.3})

        self.ids._text_container.add_widget(self.info_label)
        

        Clock.schedule_interval(lambda dt: self.update_status(), 5)
        
    def on_icon_press(self, instance):
        print("pressed")
        
    def update_status(self):
        torr = qbt.get_torrent(self.magnet)
        print(torr.name)
        if torr.state == "downloading":
            self.disabled = True
            self.text = f"{self.game_obj.name} - {torr.progress*100:.2f}%"
            self.info_label.text = f"{float(torr.progress)*100}%\n{int(torr.dlspeed)/1000} kB/s\n{int(torr.eta)/60} min"
            self.save_path = torr.content_path
            
        else:
            self.text = self.game_obj.name
            self.disabled = False
            self.info_label.text = " "
            
    def open_location(self, instance):
        os.system(f"xdg-open {self.save_path} &")
    
    def launch_game(self, instance):
        os.system(f"cd {self.save_path} && chmod +x start* && ./start* &")
        

        