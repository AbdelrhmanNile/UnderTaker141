from widgets.core import Plugin
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from utils import get_settings, write_settings
import yaml
from database import Database
from threading import Thread
db = Database("games.db")

class Settings(Plugin):
    name = "Settings"
    icon = "cog"
    
    def __init__(self, qbt_client=None,**kwargs):
        super().__init__(**kwargs)
        self.settings_yaml = get_settings()
        
        self.layout = MDBoxLayout(orientation="vertical", padding="12dp", pos_hint={"y": 0.05}, spacing="12dp")
        self.add_widget(self.layout)
        
        
        # settings label
        self.settings_label = MDLabel(text="Settings", halign="left", font_style="H4", size_hint=(1, 0.1))
        self.layout.add_widget(self.settings_label)
        
        # general settings
        self.save_path = MDTextField(text=self.settings_yaml["general"]["save_path"], hint_text="Save path", pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=(0.8, 0.1))
        self.layout.add_widget(self.save_path)
        
        # qBittorrent settings
        self.qbt_host = MDTextField(text=self.settings_yaml["qbittorrent_api"]["host"], hint_text="qBittorrent host", pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=(0.8, 0.1))
        self.layout.add_widget(self.qbt_host)
        self.qbt_port = MDTextField(text=str(self.settings_yaml["qbittorrent_api"]["port"]), hint_text="qBittorrent port", pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=(0.8, 0.1))
        self.layout.add_widget(self.qbt_port)
        self.qbt_username = MDTextField(text=self.settings_yaml["qbittorrent_api"]["username"], hint_text="qBittorrent username", pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=(0.8, 0.1))
        self.layout.add_widget(self.qbt_username)
        self.qbt_password = MDTextField(text=self.settings_yaml["qbittorrent_api"]["password"], hint_text="qBittorrent password", pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=(0.8, 0.1))
        self.layout.add_widget(self.qbt_password)
        
        # igdb settings
        self.twitch_client_id = MDTextField(text=self.settings_yaml["igdb"]["twitch_client_id"], hint_text="Twitch client id", pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=(0.8, 0.1))
        self.layout.add_widget(self.twitch_client_id)
        self.twitch_client_secret = MDTextField(text=self.settings_yaml["igdb"]["twitch_client_secret"], hint_text="Twitch client secret", pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=(0.8, 0.1))
        self.layout.add_widget(self.twitch_client_secret)
        
        # buttons
        self.save_btn = MDRectangleFlatButton(text="Save",on_press=self.save_settings, pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=(0.8, 0.00001))
        self.layout.add_widget(self.save_btn)
        
        # update database button, color red, text color black
        self.update_db_btn = MDRectangleFlatButton(text="Update database",pos_hint={"center_x": 0.5, "center_y": 0.5}, md_bg_color="#ff0000", size_hint=(0.8, 0.00001), text_color=(0, 0, 0, 1))
        self.update_db_btn.bind(on_press=self.update_db)
        self.layout.add_widget(self.update_db_btn)
        
        # boxlayout as spacer
        self.layout.add_widget(MDBoxLayout(size_hint=(None, None), size=(1, 150)))
        
        
        
    def save_settings(self, instance):
        self.settings_yaml["general"]["save_path"] = self.save_path.text
        self.settings_yaml["qbittorrent_api"]["host"] = self.qbt_host.text
        self.settings_yaml["qbittorrent_api"]["port"] = int(self.qbt_port.text)
        self.settings_yaml["qbittorrent_api"]["username"] = self.qbt_username.text
        self.settings_yaml["qbittorrent_api"]["password"] = self.qbt_password.text
        self.settings_yaml["igdb"]["twitch_client_id"] = self.twitch_client_id.text
        self.settings_yaml["igdb"]["twitch_client_secret"] = self.twitch_client_secret.text
        
        write_settings(self.settings_yaml)
            
        self.settings_yaml = get_settings()
        
        
    def update_db(self, instance):
        
        instance.text = "It will take a while, please wait..."
        instance.disabled = True
        
        
        
        #from utils import JohnCena141Scraper
        #scraper = JohnCena141Scraper("cc", self.settings_yaml["igdb"]["twitch_client_id"], self.settings_yaml["igdb"]["twitch_client_secret"], db)
        #scraper.run()
        from utils import ReleasesFeed
        updater = ReleasesFeed(twitch_client_id=self.settings_yaml["igdb"]["twitch_client_id"], twitch_client_secret=self.settings_yaml["igdb"]["twitch_client_secret"], db_object=db)
        t = Thread(target=updater.pipeline)
        t.start()
        instance.text = "Done! please restart the app"