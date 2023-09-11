import os
os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivymd.app import MDApp
from widgets.core import MainScreen
from utils import check_config, check_database
from __version__ import __version__

class UnderTaker141(MDApp):
    def build(self):
        
        check_config()
        check_database()
        
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"

        return MainScreen(__version__)


UnderTaker141().run()