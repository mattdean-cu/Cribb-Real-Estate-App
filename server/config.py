"""
Legacy config file - replace with config package
This file can be removed once you update app.py to use the new config system
"""
from config import get_config

# Get the appropriate config
Config = get_config()