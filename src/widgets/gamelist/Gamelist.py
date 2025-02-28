from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.boxlayout import MDBoxLayout
from widgets.searchbar import SearchBar

class CenteredStackLayout(MDStackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_height = True
    
    def on_size(self, instance, value):
        width, height = self.size
        card_width = getattr(next(iter(self.children), None), "width", None)
        if not card_width:
            return
        number_of_cards = width//card_width
        padding = (width - (card_width * number_of_cards)) / (number_of_cards + 1) 
        self.padding = padding
        self.spacing = padding

class Gamelist(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # main layout
        self.orientation="vertical"

        # searchbar
        self.searchbar = SearchBar()
        self.searchbar.bind(on_text_validate=self.update_list_on_search)
        self.add_widget(self.searchbar)

        # games grid
        self.scrollview = MDRecycleView()
        self.stack = CenteredStackLayout()
        self.scrollview.add_widget(self.stack)
        self.add_widget(self.scrollview) 

    def clear_list(self):
        self.stack.clear_widgets()
        
    def add_game(self, game):
        self.stack.add_widget(game)

    def search_bind(self, call_on_text_change):
        self.call_on_text_change = call_on_text_change
    
    def update_list_on_search(self, instance):
        self.call_on_text_change(instance)
    
    def game_count(self):
        return len(self.stack.children)

