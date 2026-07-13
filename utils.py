import json, os
DATA_FILE = 'data.json'

def get_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def update_price(key, value):
    data = get_data()
    data[key] = int(value)
    save_data(data)
