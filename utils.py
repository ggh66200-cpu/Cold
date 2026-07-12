import time
import json
import os

DATA_FILE = 'data.json'

def get_data():
    if not os.path.exists(DATA_FILE):
        return {"subs": {}, "users": {}, "total_count": 0, "usd_100": 150000}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تسجيل دخول مستخدم جديد وتفعيل الفترة المجانية
def register_user(user_id):
    data = get_data()
    if str(user_id) not in data['users']:
        data['users'][str(user_id)] = {"usage": 0, "trial_end": time.time() + (3 * 86400)}
        data['total_count'] += 1
        save_data(data)
    return data['users'][str(user_id)]

# فحص الوصول (100 مستخدم مجاني -> 3 أيام تجربة -> اشتراك)
def check_access(user_id):
    data = get_data()
    # إذا عدد المستخدمين أقل من 100، الكل مجاني
    if data['total_count'] <= 100: return True
    
    # فحص الاشتراك المدفوع
    if time.time() < data['subs'].get(str(user_id), 0): return True
    
    # فحص الفترة التجريبية (3 أيام)
    user = data['users'].get(str(user_id))
    if user and time.time() < user['trial_end']: return True
    
    return False

def add_subscription(user_id, days):
    data = get_data()
    data['subs'][str(user_id)] = time.time() + (int(days) * 86400)
    save_data(data)

def get_stats():
    data = get_data()
    return f"عدد المستخدمين الكلي: {data['total_count']}\nالمشتركين الفعليين: {len(data['subs'])}"
