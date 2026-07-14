import json, os, time

DATA_FILE = 'data.json'

def get_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f: 
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)

def check_user(user_id):
    data = get_data()
    uid = str(user_id)
    if uid not in data['users']:
        data['total_count'] += 1
        # تسجيل وقت الدخول لبدء الـ 7 أيام (مخزنة بالثواني)
        data['users'][uid] = {"join_date": time.time()}
        save_data(data)
        return True, data['total_count']
    
    # فحص الاشتراك (7 أيام = 604800 ثانية)
    join_date = data['users'][uid]['join_date']
    if time.time() - join_date > 604800:
        return False, data['total_count'] # انتهى الاشتراك
    
    return True, data['total_count']

def update_setting(key, value):
    data = get_data()
    data['settings'][key] = int(value)
    save_data(data)
