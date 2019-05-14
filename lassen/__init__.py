import json
import os

from .mapper.lassen import LassenMapper

with open(f"{os.path.dirname(os.path.abspath(__file__))}/../rules/all.json",'r') as jfile:
    rules = json.load(jfile)
