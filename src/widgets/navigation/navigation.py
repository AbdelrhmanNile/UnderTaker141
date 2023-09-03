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
