import telebot
from telebot import types
import json
import os
import math
import time
from datetime import datetime, timedelta

TOKEN = '8656689517:AAEjDWKpXpKGa_OXaxBz45QLMNp3ps2JUBs'
bot = telebot.TeleBot(TOKEN)
DATA_FILE = "gold_data.json"
ADMIN_CHAT_ID = "7305704935"

user_data = {}

def load_from_telegram_cloud():
    global user_data
    try:
        updates = bot.get_updates(limit=100, allowed_updates=["message"])
        file_id = None
        for update in reversed(updates):
            if update.message and update.message.document and update.message.document.file_name == DATA_FILE:
                file_id = update.message.document.file_id
                break
        if file_id:
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            user_data = json.loads(downloaded_file.decode('utf-8'))
            with open(DATA_FILE, "w") as f:
                json.dump(user_data, f)
            return
    except: pass
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            user_data = json.load(f)

def save_and_backup():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f)
    try:
        with open(DATA_FILE, "rb") as f:
            bot.send_document(ADMIN_CHAT_ID, f, caption=f"👑 نسخة احتياطية (بوت الذهب) - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    except: pass

load_from_telegram_cloud()

def check_subscription(chat_id):
    cid = str(chat_id)
    if cid not in user_data:
        expire_date = datetime.now() + timedelta(days=3)
        user_data[cid] = {'usd_rate': 0, 'gold_21': 0, 'gold_18': 0, 'expire_at': expire_date.strftime("%Y-%m-%d %H:%M:%S")}
        save_and_backup()
        return True, user_data[cid]['expire_at']
    expire_time = datetime.strptime(user_data[cid]['expire_at'], "%Y-%m-%d %H:%M:%S")
    return datetime.now() < expire_time, user_data[cid]['expire_at']

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("☀️ الإعدادات الصباحية", "💰 بيع ذهب للزبون", "⚖️ شراء ذهب من زبون")
    return markup

@bot.message_handler(commands=['start'])
def start_msg(message):
    is_active, expire_date = check_subscription(message.chat.id)
    fake_users = 342 + len(user_data)
    text = f"👑 أهلاً بك في بوت الذهب العراقي\n👥 {fake_users} صائغ يعتمدون علينا.\n⏱️ اشتراكك لغاية: {expire_date.split()[0]}"
    bot.reply_to(message, text, reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def router(message):
    is_active, expire_date = check_subscription(message.chat.id)
    if not is_active:
        bot.reply_to(message, f"🔒 انتهى اشتراكك! حول 7,500 د.ع لزين كاش: 07XXXXXXXX وأرسل الوصل.")
        return
    if message.text == "☀️ الإعدادات الصباحية":
        msg = bot.reply_to(message, "💵 أرسل سعر 100$ (مثال: 153000):")
        bot.register_next_step_handler(msg, lambda m: bot.reply_to(m, "🟡 أرسل سعر غرام 21:").register_next_step_handler(m, lambda m2: bot.reply_to(m2, "⚪ أرسل سعر غرام 18:").register_next_step_handler(m2, save_all, m.text)))
    elif "بيع" in message.text or "شراء" in message.text:
        action = "sell" if "بيع" in message.text else "buy"
        msg = bot.reply_to(message, "أرسل الوزن بالغم:")
        bot.register_next_step_handler(msg, calc_final, action)

def save_all(message, usd):
    cid = str(message.chat.id)
    user_data[cid].update({'usd_rate': float(usd), 'gold_21': float(message.text), 'gold_18': 0}) # تبسيط
    save_and_backup()
    bot.reply_to(message, "✅ تم الحفظ.")

def calc_final(message, action):
    cid = str(message.chat.id)
    weight = float(message.text)
    load = bot.reply_to(message, "⏳ جاري الحساب...")
    time.sleep(2)
    bot.edit_message_text("📊 النتيجة: ...", chat_id=cid, message_id=load.message_id)
    # هنا تكمل منطق الحساب
bot.polling()
