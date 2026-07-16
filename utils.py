import json, os, time
from telebot import types

DATA_FILE = 'data.json'

def get_data():
    default_settings = {
        "mithqal_21": 450000,
        "mithqal_18": 380000,
        "labor_21": 10000,
        "labor_18": 10000,
        "usd_100": 150000
    }
    
    if not os.path.exists(DATA_FILE):
        default_data = {
            "total_count": 166,
            "users": {},
            "settings": default_settings
        }
        save_data(default_data)
        return default_data
        
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: 
            data = json.load(f)
    except:
        data = {
            "total_count": 166,
            "users": {},
            "settings": default_settings
        }

    if 'settings' not in data:
        data['settings'] = default_settings
    else:
        for k, v in default_settings.items():
            if k not in data['settings']:
                data['settings'][k] = v
                
    if 'total_count' not in data:
        data['total_count'] = 166
    if 'users' not in data:
        data['users'] = {}
        
    save_data(data)
    return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)

def check_user(user_id):
    data = get_data()
    uid = str(user_id)
    
    if uid not in data['users'] or not isinstance(data['users'][uid], dict):
        if uid not in data['users']:
            data['total_count'] += 1
        data['users'][uid] = {"join_date": time.time()}
        save_data(data)
        return True, data['total_count']
    
    user_record = data['users'][uid]
    if 'join_date' not in user_record:
        user_record['join_date'] = time.time()
        save_data(data)
    
    # 💡 تم تفعيل السماح الدائم للمطور والعملاء حالياً لتفادي قفل الـ start أثناء الفحص
    # يمكنك إرجاع فحص الـ 7 أيام لاحقاً عند الإطلاق الفعلي
    return True, data['total_count']

def update_setting(key, value):
    data = get_data()
    data['settings'][key] = int(value)
    save_data(data)

# دالة حساب الورق والدينار العراقي الذكية (بدون استخدام كلمة دنانير نهائياً)
def calculate_paper_and_dinar(total_iqd, usd_100_rate):
    if usd_100_rate <= 0:
        return f"{total_iqd:,.0f} دينار"
    
    papers = int(total_iqd // usd_100_rate)
    remaining_iqd = int(total_iqd % usd_100_rate)
    
    result = []
    if papers > 0:
        if papers == 1:
            result.append("1 ورقة")
        elif papers == 2:
            result.append("2 ورقة")
        else:
            result.append(f"{papers} ورقة")
            
    if remaining_iqd > 0:
        result.append(f"{remaining_iqd:,.0f} دينار")
        
    if not result:
        return "0 دينار"
        
    return " و ".join(result)

def get_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 بيع للزبون", "⚖️ شراء من زبون")
    markup.add("⚙️ إعدادات الصباح")
    return markup

def get_karat_unit_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("غرام عيار 21", "غرام عيار 18")
    markup.add("مثقال عيار 21", "مثقال عيار 18")
    markup.add("⬅️ الرجوع للرئيسية")
    return markup

def send_main_menu(bot, chat_id, text_to_send):
    bot.send_message(chat_id, text_to_send, parse_mode="Markdown", reply_markup=get_keyboard())
