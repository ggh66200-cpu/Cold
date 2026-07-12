import telebot, os, time, math
from flask import Flask
from threading import Thread
from langs import LANG
from sub import is_subscribed

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- إعداد السيرفر ---
app = Flask(__name__)
@app.route('/')
def home(): return "Dubai Master - System Online"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# --- القائمة الرئيسية (شاملة) ---
def get_main_markup(lang='ar'):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(LANG[lang]['buy'], LANG[lang]['sell'])
    markup.add(LANG[lang]['settings'])
    markup.add(LANG[lang]['lang'], LANG[lang]['sub'])
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    # البوت سيعرض القائمة بالعربية افتراضياً، وسيظهر كل شيء
    bot.send_message(cid, "💎 **Dubai Master System**\nمرحباً بك في النظام الرئيسي.", reply_markup=get_main_markup('ar'))

# --- معالجة الأزرار (شاملة لكل اللغات) ---
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    cid = message.chat.id
    text = message.text
    
    # تحديد اللغة بناءً على الزر المضغوط
    lang = 'ar'
    if text in [LANG['ku']['buy'], LANG['ku']['sell']]: lang = 'ku'
    elif text in [LANG['en']['buy'], LANG['en']['sell']]: lang = 'en'
    
    # 1. زر الإعدادات الصباحية
    if text in [LANG['ar']['settings'], LANG['ku']['settings'], LANG['en']['settings']]:
        bot.send_message(cid, "أرسل (سعر الدولار) و (سعر مثقال 21) و (سعر مثقال 18) بمسافات.")
        
    # 2. زر البيع والشراء
    elif text in [LANG['ar']['buy'], LANG['ku']['buy'], LANG['en']['buy']]:
        bot.send_message(cid, "قسم الشراء: اختر العيار...")
        
    elif text in [LANG['ar']['sell'], LANG['ku']['sell'], LANG['en']['sell']]:
        bot.send_message(cid, "قسم البيع للزبون: أدخل الوزن.")

# --- التشغيل الاحترافي (بدون خطأ 409) ---
bot.remove_webhook()
bot.infinity_polling(timeout=60, long_polling_timeout=60)
