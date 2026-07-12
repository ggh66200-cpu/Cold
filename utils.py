import time
import json
import os

DATA_FILE = 'data.json'

def get_data():
    if not os.path.exists(DATA_FILE):
        return {"subs": {}, "users": {}, "total_count": 0}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def check_access(user_id):
    data = get_data()
    uid = str(user_id)
    # إذا لم يصل العدد لـ 100، الكل مجاني
    if data['total_count'] < 100: return True
    # فحص الاشتراك
    if time.time() < data['subs'].get(uid, 0): return True
    # إذا انتهى الاشتراك أو الفترة التجريبية
    return False

def register_user(user_id):
    data = get_data()
    uid = str(user_id)
    if uid not in data['users']:
        data['total_count'] += 1
        data['users'][uid] = {"usage": 0}
        save_data(data)
        return True # مستخدم جديد
    return False
