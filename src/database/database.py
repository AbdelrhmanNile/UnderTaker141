"""
ORM for the database
"""

from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    cover = Column(String)
    size = Column(String)
    magnet = Column(String)
    platform = Column(String)
    description = Column(String)
    
    def __init__(self, name, cover, size, magnet, platform, description):
        self.name = name
        self.cover = cover
        self.size = size
        self.magnet = magnet
        self.platform = platform
        self.description = description

    def __repr__(self):
        return f"<Game(name={self.name}, cover={self.cover}, size={self.size}, platform={self.platform})>"
    
class GamesInfo(Base):
    __tablename__ = 'games_info'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    cover = Column(String)
    description = Column(String)
    
    def __init__(self, name, cover, description):
        self.name = name
        self.cover = cover
        self.description = description
        

    def __repr__(self):
        return f"<CoversDB(name={self.name}, cover={self.cover}, description={self.description})>"
    

class Database:
    """
    Interface for the database
    """
    def __init__(self, db_file):
        self.db_file = db_file
        self.engine = create_engine(f'sqlite:///database/{db_file}', echo=False)
        self.session = sessionmaker(bind=self.engine)()
        Base.metadata.create_all(self.engine)
        
    def add_game(self, name, cover, size, magnet, platform, description):
        
        # check if game already exists in GamesInfo table
        if self._get_game_info(name) is None:
            self._add_game_info(name, cover, description)
        
        # if exists but cover is None, update cover and description
        elif self._get_game_info(name).cover is None:
            self._update_game_info(name, cover, description)
    
        self.session.add(Game(name, cover, size, magnet, platform, description))
        self.session.commit()
        
    def get_games(self):
        return self.session.query(Game).all()
    
    def get_game(self, name):
        # search by matching incomplete name
        return self.session.query(Game).filter(Game.name.ilike(f'%{name}%')).all()
    
    def get_game_by_magnet(self, magnet):
        return self.session.query(Game).filter(Game.magnet == magnet).first()
    
    def get_specific_game(self, name):
        return self.session.query(Game).filter(Game.name.ilike(f'%{name}%')).first()
    
    # get n random games from the database
    def get_randn_games(self, n):
        # if n is greater than the number of games in the database, return all games
        if n > self.count_games():
            return self.get_games()
        return self.session.query(Game).order_by(func.random()).limit(n).all()
    
    def delete_game(self, name):
        game = self.get_game(name)
        self.session.delete(game)
        self.session.commit()
        
    def update_game(self, name, cover, size, magnet, platform, description):
        game = self.get_game(name)
        game.cover = cover
        game.size = size
        game.magnet = magnet
        game.platform = platform
        game.description = description
        self.session.commit()
        
    def count_games(self):
        return self.session.query(Game).count()
    
    def _add_game_info(self, name, cover, description):
        cover = GamesInfo(name, cover, description)
        self.session.add(cover)
        self.session.commit()
        
    def _get_game_info(self, name):
        return self.session.query(GamesInfo).filter(GamesInfo.name.ilike(f'%{name}%')).first()
    
    def _update_game_info(self, name, cover, description):
        game_info = self._get_game_info(name)
        game_info.cover = cover
        game_info.description = description
        self.session.commit()
        
    def close(self):
        self.session.close()
        
    def delete_all(self):
        self.session.query(Game).delete()
        self.session.commit()
        
    #def _get_game_info_from_igdb(self, game_name):
        
        

        

if __name__ == '__main__':
    db = Database("games.db")
    
    g = db._get_game_info("baba")
    print(g.cover)