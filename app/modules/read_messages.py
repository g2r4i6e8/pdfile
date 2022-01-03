# load txt dicts
import json
import os

with open(os.path.join('resources', 'txt_dict.json'), 'r', encoding="utf8") as file:
    txt_dict = json.load(file)

with open(os.path.join('resources', 'errors_dict.json'), 'r', encoding="utf8") as file:
    errors_dict = json.load(file)
