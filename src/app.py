from kivymd.app import MDApp
from widgets.core import MainScreen

gruv_box_colors = {
    
}


class UnderTaker141(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"

        return MainScreen()


UnderTaker141().run()