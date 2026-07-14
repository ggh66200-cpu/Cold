import json, os, time

DATA_FILE = 'data.json'

def get_data():
    if not os.path.exists(DATA_FILE):
        # إنشاء ملف افتراضي إذا لم يكن موجوداً
        default_data = {
            "total_count": 166,
            "users": {},
            "settings": {
                "mithqal_21": 450000,
                "mithqal_18": 380000,
                "labor_21": 10000,
                "labor_18": 10000,
                "usd_100": 150000
            }
        }
        save_data(default_data)
        return default_data
    with open(DATA_FILE, 'r', encoding='utf-8') as f: 
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)

def check_user(user_id):
    data = get_data()
    uid = str(user_id)
    
    # إذا كان مستخدم جديد تماماً
    if uid not in data['users']:
        data['total_count'] += 1
        data['users'][uid] = {"join_date": time.time()}
        save_data(data)
        return True, data['total_count']
    
    # فحص الاشتراك التجريبي (7 أيام = 604800 ثانية)
    join_date = data['users'][uid]['join_date']
    if time.time() - join_date > 604800:
        return False, data['total_count'] # انتهى الاشتراك
    
    return True, data['total_count']

def update_setting(key, value):
    data = get_data()
    data['settings'][key] = int(value)
    save_data(data)
