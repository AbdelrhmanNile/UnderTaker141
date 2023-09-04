from kivymd.app import MDApp
from widgets.core import MainScreen
from utils import check_config, check_database


class UnderTaker141(MDApp):
    def build(self):
        
        check_config()
        check_database()
        
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"

        return MainScreen()


UnderTaker141().run()