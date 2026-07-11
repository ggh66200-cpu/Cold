import telebot
from telebot import types
import json, os, time
from datetime import datetime, timedelta

TOKEN = '8656689517:AAEjDWKpXpKGa_OXaxBz45QLMNp3ps2JUBs'
bot = telebot.TeleBot(TOKEN)
DATA_FILE = "gold_data.json"
ADMIN_CHAT_ID = "7305704935" # ضع الآيدي الخاص بك هنا

user_data = {}

def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: user_data = json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f: json.dump(user_data, f)

load_data()

@bot.message_handler(commands=['start'])
def start(message):
    cid = str(message.chat.id)
    if cid not in user_data:
        user_data[cid] = {'status': 'trial', 'expire': (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")}
        save_data()
    
    # خدعة المشتركين الوهميين
    fake_count = 450 + len(user_data)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 حساب ذهب", "📅 تفعيل اشتراك")
    bot.reply_to(message, f"👑 أهلاً بك في حاسبة الذهب الذكية.\n👥 انضم إلينا أكثر من {fake_count} صائغ.\n\nاختر العملية:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📅 تفعيل اشتراك")
def sub_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("أسبوعي (7,500 د.ع)", callback_data="sub_7"))
    markup.add(types.InlineKeyboardButton("شهري (25,000 د.ع)", callback_data="sub_30"))
    bot.reply_to(message, "اختر باقة الاشتراك وأرسل صورة الوصل:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data.startswith("sub_"):
        bot.send_message(call.message.chat.id, "تم اختيار الباقة. الآن أرسل صورة وصل التحويل للإدارة.")
    elif call.data.startswith("approve_"):
        cid = call.data.split("_")[1]
        user_data[cid]['status'] = 'active'
        user_data[cid]['expire'] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        save_data()
        bot.send_message(cid, "✅ تم تفعيل اشتراكك بنجاح!")
        bot.edit_message_text("تم تفعيل العميل.", call.message.chat.id, call.message.message_id)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ نعم (تفعيل)", callback_data=f"approve_{message.chat.id}"))
        bot.send_photo(ADMIN_CHAT_ID, message.photo[-1].file_id, caption=f"طلب تفعيل من العميل: {message.chat.id}", reply_markup=markup)
        bot.reply_to(message, "تم إرسال الوصل للإدارة، سيتم التفعيل قريباً.")

@bot.message_handler(func=lambda m: m.text == "💰 حساب ذهب")
def calc(message):
    # خدعة التحميل البصري
    msg = bot.reply_to(message, "⏳ جاري الاتصال بالبورصة...")
    time.sleep(1)
    bot.edit_message_text("🧮 تحليل السعر...", message.chat.id, msg.message_id)
    time.sleep(1)
    bot.edit_message_text("✅ تم إنجاز الحسبة بدقة.", message.chat.id, msg.message_id)

bot.polling()
