# app/user_config.py

import os
import json
import random


CONFIG_PATH = "user_config.json"

def generate_user_code():
    return f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"

def load_or_create_user_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    else:
        user_code = generate_user_code()
        config = {
            "user_code": user_code
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f)
        return config
