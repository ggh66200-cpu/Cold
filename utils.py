import json, os, time
DATA_FILE = 'data.json'

def get_data():
    if not os.path.exists(DATA_FILE): return {"total_count": 80, "users": {}, "settings": {"buy_btn": True, "sell_btn": True, "sub_btn": False}, "buy_21": 85000, "sell_21": 87000, "usd_100": 150000}
    with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def check_access(user_id):
    data = get_data()
    uid = str(user_id)
    # الأدمن دائماً مسموح له
    if uid == "YOUR_ADMIN_ID": return True
    # نظام الـ 7 أيام
    reg_time = data['users'].get(uid, {}).get('reg_date', time.time())
    if time.time() - reg_time < (7 * 86400): return True
    # نظام الاشتراكات المدفوعة
    return data['users'].get(uid, {}).get('is_sub', False)

def register_user(user_id):
    data = get_data()
    uid = str(user_id)
    if uid not in data['users']:
        data['total_count'] += 1
        data['users'][uid] = {"reg_date": time.time(), "is_sub": False}
        save_data(data)
