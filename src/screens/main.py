from widgets.core import Plugin
from widgets.game import GameCard
from widgets.gamelist import Gamelist
from database import Database

# database
db = Database("games.db")

class Main(Plugin):
    name = "Main"
    icon = "controller"
    def __init__(self, qbt_client, **kwargs):
        super().__init__(**kwargs)
        self.id = "main"
        
        self.qbt_client = qbt_client
        
        self.gamelist = Gamelist()
        self.gamelist.search_bind(self.update_grid_on_search)
        self.add_widget(self.gamelist)
        
        # fill grid with 50 random games
        self.randomize()
    
    # randomize grid
    def randomize(self):
        self.gamelist.clear_list()
        for i in db.get_randn_games(50):
            self.gamelist.add_game(GameCard(i, self.qbt_client))

    # callback for searchbar   
    def update_grid_on_search(self, instance):
        text = instance.text
        instance.text = ""
        
        if text == "": # if entred text is empty, randomize grid
            self.randomize()
            return
        
        # clear grid
        self.gamelist.clear_list()
        
        # fill grid with search results
        for i in db.get_game(text):
            self.gamelist.add_game(GameCard(i, self.qbt_client))

        