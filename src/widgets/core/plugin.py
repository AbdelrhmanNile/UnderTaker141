from kivymd.uix.screen import MDScreen
from kivymd.uix.responsivelayout import MDResponsiveLayout
from kivymd.uix.widget import Widget
from dataclasses import dataclass

# Base class for screens
class Plugin(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color="#90a4ae"
        self.radius = [18, 0, 0, 0]
        self.layout = None
        
    def push_widget(self, widget: Widget):
        try:
            self.layout.add_widget(widget)
        except Exception as e:
            print(e)
            exit()
            

# plugin dataclass
@dataclass
class PluginData:
    name: str
    icon: str
    class_: type