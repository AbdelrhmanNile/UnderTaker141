from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from widgets.core import Plugin
from widgets.game import GameCard
from widgets.searchbar import SearchBar
from kivy.uix.image import AsyncImage
from database import Database

# database
db = Database("games.db")


class Main(Plugin):
    name = "Main"
    icon = "controller"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = "main"
        
        #self.scr_mngr = scr_mngr
        
        # main layout
        self.layout = MDBoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        
        # Spacer
        self.layout.add_widget(MDBoxLayout(size_hint=(1, 0.05)))
        
        # searchbar
        self.searchbar = SearchBar()
        self.searchbar.bind(on_text_validate=self.update_grid_on_search)
        self.layout.add_widget(self.searchbar)
        
        # BoxLayout as separator
        #self.layout.add_widget(MDBoxLayout(size_hint=(1, 0.3)))
        
        # games grid
        self.scrollview = ScrollView()
        self.grid = MDGridLayout(cols=10, padding="12dp", spacing="12dp", adaptive_height=True, adaptive_width=True)
        self.scrollview.add_widget(self.grid)
        self.layout.add_widget(self.scrollview) 
        
        # fill grid with 50 random games
        self.randomize()
    
    # randomize grid
    def randomize(self):
        self.grid.clear_widgets()
        for i in db.get_randn_games(50):
            self.grid.add_widget(GameCard(i))
     
    # callback for searchbar   
    def update_grid_on_search(self, instance):
        text = instance.text
        instance.text = ""
        
        if text == "": # if entred text is empty, randomize grid
            self.randomize()
            return
        
        # clear grid
        self.grid.clear_widgets()
        
        # fill grid with search results
        for i in db.get_game(text):
            self.grid.add_widget(GameCard(i))

        