import yaml

def get_settings():
    with open("settings.yaml") as f:
        return yaml.safe_load(f)