from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import MDNavigationLayout
from kivymd.uix.navigationrail import MDNavigationRailItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import FadeTransition
from kivymd.uix.navigationdrawer import MDNavigationLayout

from widgets.navigation import Rail
from .plugin import Plugin, PluginData

from importlib import import_module
import yaml

class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.plugins = self.load_plugins()
        
        # nav layout
        self.nav_layout = MDNavigationLayout()
        
        #screen manager
        self.scr_mngr = MDScreenManager(transition=FadeTransition(duration=.2, clearcolor=[1, 1, 1, 1]))
        
        # scr 1
        self.scr1 = MDScreen()
        
        self.boxlayout1 = MDBoxLayout(orientation="vertical")
        self.boxlayout2 = MDBoxLayout(adaptive_height=True, md_bg_color="#fffcf4", padding="12dp")
        self.boxlayout2.add_widget(MDLabel(text="Flutter 3la zobry", adaptive_height=True, pos_hint={"center_y": 0.5}))
        
        self.boxlayout3 = MDBoxLayout()
        self.rail = Rail()
        self.load_nav_list()
        
        self.screen_manager_content = MDScreenManager(transition=FadeTransition(duration=.2, clearcolor=[1, 1, 1, 1]), id="screen_manager_content")
        self.load_screens()
        
        self.boxlayout3.add_widget(self.rail)
        self.boxlayout3.add_widget(self.screen_manager_content)
        
        self.boxlayout1.add_widget(self.boxlayout2)
        self.boxlayout1.add_widget(self.boxlayout3)
        
        self.scr1.add_widget(self.boxlayout1)
        
        self.scr_mngr.add_widget(self.scr1)
        
        self.nav_layout.add_widget(self.scr_mngr)
        
        self.add_widget(self.nav_layout)
        
    def load_plugins(self) -> dict: # load plugins from plugins.yaml
        
        with open('screens.yaml') as f:
            plugins_config = yaml.safe_load(f)
    
        plugins = []
        
        for plugin in plugins_config:
            module = import_module(f"screens.{plugin['plugin']}")
            
            all_attrs = module.__dir__() # get all the attributes of the module
            
            plugin_class = getattr(module, all_attrs[-1]) # get the screen class from module
            
            if issubclass(plugin_class, Plugin):
                plugins.append(PluginData(plugin_class.name, plugin_class.icon, plugin_class))
                
            
        return plugins # {'name': screen_class}

    def load_nav_list(self): # populate the nav list with the plugin names
        
        for plugin in self.plugins:
            item = MDNavigationRailItem(icon=plugin.icon)
            
            # load the screen when the nav list item is pressed
            item.bind(on_release=lambda x, plugin_name=plugin.name: self.display_screen(plugin_name))
            
            self.rail.add_widget(item)
            
    def display_screen(self, plugin_name): # make a screen the current screen
        # delete screen named "game_screen" if it exists
        
        if self.screen_manager_content.has_screen("game_screen"):
            self.screen_manager_content.remove_widget(self.screen_manager_content.get_screen("game_screen"))
            
        
        self.screen_manager_content.current = plugin_name

    def load_screens(self): # load all the screens and add them to the screen manager
        for plugin in self.plugins:
            screen_class = plugin.class_
            screen = screen_class(name=plugin.name) # create instance of a screen class
            self.screen_manager_content.add_widget(screen) # add the screen to the screen manager