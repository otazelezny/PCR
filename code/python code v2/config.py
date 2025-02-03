# code/config.py
import ujson as json  # Use ujson for MicroPython compatibility

def load_config(config_path="/config/config.json"):
    """
    Loads the configuration from a JSON file.
    """
    with open(config_path, "r") as f:
        config = json.load(f)
    return config