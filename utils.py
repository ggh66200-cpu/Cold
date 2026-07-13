import json
import os
import time

DATA_FILE = 'data.json'

def get_data():
    if not os.path.exists(DATA_FILE):
        return {"total_count": 0, "subs": {}, "users": {}, "settings": {"buy_btn": True, "sell_btn": True, "settings_btn": True}}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def check_access(user_id):
    data = get_data()
    if data['total_count'] < 100: return True
    return data['subs'].get(str(user_id), 0) > time.time()

def register_user(user_id):
    data = get_data()
    uid = str(user_id)
    if uid not in data['users']:
        data['total_count'] += 1
        data['users'][uid] = {"usage": 0}
        save_data(data)
        return True
    return False

def add_subscription(user_id, days):
    data = get_data()
    data['subs'][str(user_id)] = time.time() + (int(days) * 86400)
    save_data(data)

def get_stats():
    data = get_data()
    return f"👥 عدد المستخدمين الكلي: {len(data['users'])}\n🛠 حالة الأزرار: {data['settings']}"

def toggle_button(btn_name, status):
    data = get_data()
    data['settings'][btn_name] = status
    save_data(data)
