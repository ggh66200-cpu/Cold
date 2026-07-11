import telebot, os, json, time, math
from flask import Flask
from threading import Thread

# === 1. إعدادات السيرفر والأمان ===
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')
bot = telebot.TeleBot(TOKEN)
DATA_FILE = "gold_data.json"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Active - 24/7"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
Thread(target=run).start()

# === 2. قاعدة بيانات اللغات المدمجة ===
LANG = {
    'ar': {
        'buy': '⚖️ شراء ذهب من زبون', 'sell': '💰 بيع ذهب للزبون', 'settings': '☀️ الإعدادات الصباحية', 
        'lang': '🌐 تغيير اللغة', 'trend': 'الترند', 'calc_done': '✅ تم إنجاز الحسبة بدقة.'
    },
    'ku': {
        'buy': '⚖️ Kirîna zêr', 'sell': '💰 Firotina zêr', 'settings': '☀️ Mîhengên sibehê', 
        'lang': '🌐 Ziman', 'trend': 'Trend', 'calc_done': '✅ Hesab bi serkeftî hate kirin.'
    },
    'en': {
        'buy': '⚖️ Buy Gold', 'sell': '💰 Sell Gold', 'settings': '☀️ Morning Settings', 
        'lang': '🌐 Language', 'trend': 'Trend', 'calc_done': '✅ Calculation done accurately.'
    }
}

user_prefs = {} # لحفظ لغة كل مستخدم

# === 3. الأزرار والخدع البصرية (الترند) ===
@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    user_prefs[cid] = user_prefs.get(cid, 'ar') # اللغة الافتراضية عربي
    lang = user_prefs[cid]
    
    # بناء الأزرار بناءً على الصورة المرفقة
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(LANG[lang]['buy'], LANG[lang]['sell'])
    markup.add(LANG[lang]['settings'])
    markup.add(LANG[lang]['lang']) # زر إضافي لتغيير اللغة
    
    # الخدعة البصرية: رقم الترند الوهمي
    fake_trend = 1000 + (cid % 50) 
    
    bot.send_message(cid, f"Dubai Master\n{fake_trend}\n\n**تصفية الحسبة النهائية (سوق الذهب):**", reply_markup=markup, parse_mode="Markdown")

# === 4. تغيير اللغات ===
@bot.message_handler(func=lambda m: m.text in [LANG['ar']['lang'], LANG['ku']['lang'], LANG['en']['lang']])
def choose_lang(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("العربية 🇮🇶", callback_data="setlang_ar"))
    markup.add(telebot.types.InlineKeyboardButton("Kurdî ☀️", callback_data="setlang_ku"))
    markup.add(telebot.types.InlineKeyboardButton("English 🇬🇧", callback_data="setlang_en"))
    bot.reply_to(message, "اختر لغتك / Zimanê xwe hilbijêre / Choose your language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('setlang_'))
def set_lang_callback(call):
    cid = call.message.chat.id
    selected_lang = call.data.split('_')[1]
    user_prefs[cid] = selected_lang
    bot.answer_callback_query(call.id, "تم تغيير اللغة بنجاح!")
    bot.delete_message(cid, call.message.message_id)
    start(call.message) # إعادة إرسال القائمة باللغة الجديدة

# === 5. حاسبة السوق العراقي (فئة 100 دولار) والخدع البصرية ===
@bot.message_handler(func=lambda m: m.text in [LANG['ar']['buy'], LANG['ku']['buy'], LANG['en']['buy']])
def calculate_iraqi_market(message):
    cid = message.chat.id
    lang = user_prefs.get(cid, 'ar')
    
    # 1. الخدعة البصرية (حركة التحميل)
    msg = bot.reply_to(message, "⏳ جاري الاتصال بالبورصة وتحديث الأسعار...")
    time.sleep(1.5)
    bot.edit_message_text("🧮 يتم الآن تصفية الحساب...", cid, msg.message_id)
    time.sleep(1)
    
    # 2. أرقام تجريبية (البرمجة الحقيقية ستأخذ هذه الأرقام من الزبون لاحقاً)
    weight = 12.5
    exchange_rate_100 = 155000
    
    # 3. الحساب العراقي الدقيق (على أساس 100 دولار)
    total_iqd = 612500 # افتراضي كمثال
    
    # كم "ورقة أم 100" نحتاج لتغطية المبلغ؟ (نقرب للأعلى)
    paper_100_value_in_iqd = exchange_rate_100
    papers_needed = math.ceil(total_iqd / paper_100_value_in_iqd) * 100
    
    # الباقي بالدينار للزبون
    paid_in_iqd = (papers_needed / 100) * exchange_rate_100
    change_iqd = paid_in_iqd - total_iqd
    fraction_usd = change_iqd / (exchange_rate_100 / 100)
    
    # 4. طباعة الفاتورة بنفس تصميم صورتك بالضبط
    invoice = f"""
**تصفية الحسبة النهائية (سوق الذهب):**
━━━━━━━━━━━━━━━━━━
🔄 العملية: 🔴 شراء من زبون
⚖️ الوزن: {weight} غرام (عيار 21)
💵 سعر صرف الـ 100$: {exchange_rate_100:,.1f} د.ع
━━━━━━━━━━━━━━━━━━
💰 صافي السعر بالدينار: **{total_iqd:,.0f} د.ع**

💵 **في حال الدفع بالدولار (التصفية):**
💵 المستلم بالورق الصافي: **{papers_needed}$**
↩️ يُرجع باقي للزبون بالدينار: **{change_iqd:,.0f} د.ع**
*(قيمة الـ ${fraction_usd:.2f} المتبقية بالكسر)*
    """
    bot.edit_message_text(invoice, cid, msg.message_id, parse_mode="Markdown")

bot.polling(none_stop=True)
