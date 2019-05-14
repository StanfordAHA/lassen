import json
import os

with open(f"{os.path.dirname(os.path.abspath(__file__))}/../rules/all.json",'r') as jfile:
    rules = json.load(jfile)
