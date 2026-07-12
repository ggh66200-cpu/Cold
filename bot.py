import telebot, os, time, math
from flask import Flask
from threading import Thread
from langs import LANG
from sub import is_subscribed

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- تفعيل السيرفر (لا تلمسه) ---
app = Flask(__name__)
@app.route('/')
def home(): return "Online"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# --- القائمة الرئيسية (سريعة جداً) ---
@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    lang = 'ar' # الافتراضي
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(LANG[lang]['buy'], LANG[lang]['sell'])
    markup.add(LANG[lang]['settings'], LANG[lang]['lang'])
    bot.send_message(cid, "💎 **Dubai Master**\nنظام تصفية الحسابات السريع:", reply_markup=markup, parse_mode="Markdown")

# --- زر بيع للزبون (منفصل ومستقل) ---
@bot.message_handler(func=lambda m: m.text == LANG['ar']['sell'])
def sell_process(message):
    # لمسة جمالية: رسالة فورية ومختلفة
    bot.reply_to(message, "💰 **أهلاً بك في قسم البيع للزبون**\nيرجى إرسال الوزن المطلوب:")
    # هنا ستكمل البرمجة الخاصة بالبيع ليكون مستقلاً عن الشراء

# --- إصلاح زر اللغات (استجابة فورية) ---
@bot.message_handler(func=lambda m: m.text == LANG['ar']['lang'])
def lang_menu(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("العربية 🇮🇶", callback_data="lang_ar"))
    bot.reply_to(message, "اختر اللغة:", reply_markup=markup)

bot.polling(none_stop=True)
