import json, os, time
from telebot import types

DATA_FILE = 'data.json'

# قاموس اللغات
LANG_DATA = {
    'ar': {
        'main_menu': "القائمة الرئيسية",
        'sell': "💰 بيع للزبون",
        'buy': "⚖️ شراء من زبون",
        'settings': "⚙️ إعدادات الصباح",
        'back': "⬅️ الرجوع للرئيسية"
    },
    'ku': {
        'main_menu': "لیستی سەرەکی",
        'sell': "💰 فرۆشتن بە کڕیار",
        'buy': "⚖️ کڕین لە کڕیار",
        'settings': "⚙️ رێکخستنەکانی بەیانی",
        'back': "⬅️ گەڕانەوە بۆ سەرەکی"
    },
    'en': {
        'main_menu': "Main Menu",
        'sell': "💰 Sell to Customer",
        'buy': "⚖️ Buy from Customer",
        'settings': "⚙️ Morning Settings",
        'back': "⬅️ Back to Main"
    }
}

def get_data():
    if not os.path.exists(DATA_FILE):
        data = {"total_count": 166, "users": {}, "settings": {"mithqal_21": 450000, "mithqal_18": 380000, "labor_21": 10000, "labor_18": 10000, "usd_100": 150000}}
        save_data(data)
        return data
    with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def check_user(user_id):
    # نظام الاشتراك معزول هنا
    data = get_data()
    uid = str(user_id)
    if uid not in data['users']:
        data['total_count'] += 1
        data['users'][uid] = {"join_date": time.time(), "lang": "ar"} # الافتراضي عربي
        save_data(data)
    return True, data['total_count'], data['users'][uid].get('lang', 'ar')

def set_lang(user_id, lang):
    data = get_data()
    data['users'][str(user_id)]['lang'] = lang
    save_data(data)

def get_text(lang, key):
    return LANG_DATA.get(lang, LANG_DATA['ar']).get(key, key)

def get_keyboard(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(get_text(lang, 'sell'), get_text(lang, 'buy'))
    markup.add(get_text(lang, 'settings'))
    return markup
