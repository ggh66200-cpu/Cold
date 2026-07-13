import json, os, time
DATA_FILE = 'data.json'

def get_data():
    if not os.path.exists(DATA_FILE): return {"total_count": 80, "users": {}, "settings": {"buy_btn": True, "sell_btn": True, "sub_btn": False}, "buy_21": 85000, "sell_21": 87000, "buy_18": 75000, "sell_18": 77000, "usd_100": 150000}
    with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def register_user(user_id):
    data = get_data()
    uid = str(user_id)
    if uid not in data['users']:
        data['total_count'] += 1
        data['users'][uid] = {"reg_date": time.time()}
        save_data(data)

def update_price(key, value):
    data = get_data()
    data[key] = int(value)
    save_data(data)

def toggle_button(btn_name, status):
    data = get_data()
    data['settings'][btn_name] = status
    save_data(data)
