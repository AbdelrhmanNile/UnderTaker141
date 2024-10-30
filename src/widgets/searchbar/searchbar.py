from kivymd.uix.textfield import MDTextField


class SearchBar(MDTextField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hint_text = "Search a game"
        self.multiline = False
        
        # center the textfield, pad from left and right
        self.size_hint = (0.5, None)
        self.height = "25dp"
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        
