import json, os
from telebot import types

DATA_FILE = 'data.json'

# القاموس الخاص باللغات
LANGS = {
    "ar": {"main": "الرئيسية", "sell": "بيع للزبون", "buy": "شراء من زبون", "settings": "⚙️ إعدادات الصباح"},
    "ku": {"main": "سەرەکی", "sell": "فرۆشتن بە کڕیار", "buy": "کڕین لە کڕیار", "settings": "⚙️ ڕێکخستنەکانی بەیانی"},
    "en": {"main": "Main", "sell": "Sell to Customer", "buy": "Buy from Customer", "settings": "⚙️ Morning Settings"}
}

def get_data():
    default_settings = {"mithqal_21": 450000, "mithqal_18": 380000, "labor_21": 10000, "labor_18": 10000, "usd_100": 150000}
    if not os.path.exists(DATA_FILE):
        default_data = {"total_count": 166, "users": {}, "settings": default_settings}
        save_data(default_data)
        return default_data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {"total_count": 166, "users": {}, "settings": default_settings}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def update_all_settings(vals):
    data = get_data()
    keys = ["mithqal_21", "mithqal_18", "labor_21", "labor_18", "usd_100"]
    for i, k in enumerate(keys):
        data['settings'][k] = int(vals[i])
    save_data(data)

def calculate_paper_and_dinar(total_iqd, usd_100_rate):
    papers = int(total_iqd // usd_100_rate)
    rem = int(total_iqd % usd_100_rate)
    res = []
    if papers > 0: res.append(f"{papers} ورقة")
    if rem > 0: res.append(f"{rem:,} دينار")
    return " و ".join(res) if res else "0 دينار"

def get_keyboard(lang="ar"):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(LANGS[lang]["sell"], LANGS[lang]["buy"])
    m.add(LANGS[lang]["settings"])
    return m
