import yaml
import os

def get_settings():
    
    abs_path = os.path.dirname(__file__)
    abs_path = abs_path.split("/utils")[0]
    settings_path = os.path.join(abs_path, "settings.yaml")
    
    with open(settings_path) as f:
        return yaml.safe_load(f)
    
def write_settings(settings):
    
    abs_path = os.path.dirname(__file__)
    abs_path = abs_path.split("/utils")[0]
    settings_path = os.path.join(abs_path, "settings.yaml")
    
    with open(settings_path, "w") as f:
        yaml.dump(settings, f)