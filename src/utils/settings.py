import getpass
import yaml
import os
from bs4 import BeautifulSoup
import requests

def get_settings_template():
    
    abs_path = os.path.dirname(__file__)
    abs_path = abs_path.split("/utils")[0]
    settings_path = os.path.join(abs_path, "settings.yaml")
    
    with open(settings_path) as f:
        settings = yaml.safe_load(f)
        settings["general"]["save_path"] = f"/home/{getpass.getuser()}/Downloads"
        return settings
    
def write_settings(settings):
    
    user_name = getpass.getuser()
    config_path = f"/home/{user_name}/.config/undertaker141"
    
    settings_path = os.path.join(config_path, "settings.yaml")
    
    with open(settings_path, "w") as f:
        yaml.dump(settings, f)
        
def check_config():
    user_name = getpass.getuser()
    config_path = f"/home/{user_name}/.config/undertaker141"
    
    # Check if config directory exists
    if not os.path.exists(config_path):
        os.makedirs(config_path)
        settings = get_settings_template()
        write_settings(settings)
    
    # Check if settings file exists
    settings_path = os.path.join(config_path, "settings.yaml")
    if not os.path.isfile(settings_path):
        settings = get_settings_template()
        write_settings(settings)
        
def get_settings():
    user_name = getpass.getuser()
    config_path = f"/home/{user_name}/.config/undertaker141"
    
    settings_path = os.path.join(config_path, "settings.yaml")
    
    with open(settings_path) as f:
        return yaml.safe_load(f)
    
def check_database():
    user_name = getpass.getuser()
    config_path = f"/home/{user_name}/.config/undertaker141"
    
    db_file_path = os.path.join(config_path, "games.db")
    
    # Check if database file exists
    if not os.path.isfile(db_file_path):
        abs_path = os.path.dirname(__file__)
        abs_path = abs_path.split("/utils")[0]
        db_template_path = os.path.join(abs_path, "database/games.db")
        
        # Copy template database file
        with open(db_template_path, "rb") as f:
            db_template = f.read()
            
        with open(db_file_path, "wb") as f:
            f.write(db_template)

def get_latest_release():
    link = "https://github.com/AbdelrhmanNile/UnderTaker141/releases/tag/latest"
    try:
        page = requests.get(link)
    except requests.exceptions.ConnectionError:
        return None, None
    soup = BeautifulSoup(page.content, "lxml")
    latest_release = soup.find("h1", class_="d-inline mr-3").text.split(":")[0]
    latest_release = latest_release.strip()
    return latest_release, link