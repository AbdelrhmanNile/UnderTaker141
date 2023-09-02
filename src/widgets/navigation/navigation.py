from kivymd.uix.navigationrail import MDNavigationRail, MDNavigationRailMenuButton

class Rail(MDNavigationRail):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.anchor = "center"
        
        menu_button = MDNavigationRailMenuButton(
            icon="menu",
        )
        #self.add_widget(menu_button)
        
        self.id = "navigation_rail"
        self.md_bg_color = "#fffcf4"
        self.selected_color_background = "#e7e4c0"
        self.ripple_color_item = "#e7e4c0"
