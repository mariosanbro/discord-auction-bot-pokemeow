import json

def load_config() -> dict:
    with open('./configuration/configuration.json', 'r') as config_file:
        return json.load(config_file)
    
def save_config(config_dict: dict) -> None:
    with open('./configuration/configuration.json', 'w') as config_file:
        json.dump(config_dict, config_file, indent=4)
