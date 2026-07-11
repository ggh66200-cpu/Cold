import telebot, os, time, math
from flask import Flask
from threading import Thread

# ==========================================
# 1. إعدادات السيرفر
# ==========================================
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "Dubai Master Bot is Running"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
Thread(target=run).start()

# ==========================================
# 2. ملف اللغات (العربية، الكردية السورانية، الإنكليزية)
# ==========================================
LANG = {
    'ar': {'buy': '⚖️ شراء من زبون', 'sell': '💰 بيع للزبون', 'lang': '🌐 تغيير اللغة', 'sub': '💳 الاشتراك'},
    'ku': {'buy': '⚖️ کڕینی زێڕ', 'sell': '💰 فرۆشتنی زێڕ', 'lang': '🌐 گۆڕینی زمان', 'sub': '💳 بەشداریکردن'},
    'en': {'buy': '⚖️ Buy Gold', 'sell': '💰 Sell Gold', 'lang': '🌐 Language', 'sub': '💳 Subscription'}
}
user_prefs = {}
user_data = {} # لحفظ الأرقام أثناء الحساب

# ==========================================
# 3. قسم الاشتراك الإجباري (المعزول)
# ==========================================
# هنا يمكنك مستقبلاً ربط قاعدة بيانات، حالياً سنسمح للكل بالتجربة
def is_subscribed(user_id):
    # إذا كان المستخدم هو الأدمن، فهو مشترك دائماً
    if str(user_id) == str(ADMIN_ID): return True
    return True # غيرها إلى False لاحقاً لتفعيل الحظر على غير المشتركين

# ==========================================
# 4. لوحة التحكم واللغات
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    if not is_subscribed(cid):
        bot.send_message(cid, "⚠️ اشتراكك منتهي. يرجى التجديد.")
        return
        
    user_prefs[cid] = user_prefs.get(cid, 'ar')
    lang = user_prefs[cid]
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(LANG[lang]['buy'], LANG[lang]['sell'])
    markup.add(LANG[lang]['lang'], LANG[lang]['sub'])
    
    bot.send_message(cid, f"**Dubai Master System**\nمرحباً بك في نظام تصفية الحسابات المتقدم 📊", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in [LANG['ar']['lang'], LANG['ku']['lang'], LANG['en']['lang']])
def choose_lang(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("العربية 🇮🇶", callback_data="lang_ar"))
    markup.add(telebot.types.InlineKeyboardButton("Kurdî (Sorani) ☀️", callback_data="lang_ku"))
    markup.add(telebot.types.InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"))
    bot.reply_to(message, "اختر اللغة / زمان هەڵبژێرە / Select Language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_lang(call):
    cid = call.message.chat.id
    user_prefs[cid] = call.data.split('_')[1]
    bot.delete_message(cid, call.message.message_id)
    start(call.message)

# ==========================================
# 5. نظام الحاسبة والخدع البصرية والفاتورة
# ==========================================
@bot.message_handler(func=lambda m: m.text in [LANG['ar']['buy'], LANG['ku']['buy'], LANG['en']['buy']])
def start_calc(message):
    cid = message.chat.id
    msg = bot.send_message(cid, "✏️ **أدخل وزن الذهب بالغرام (مثال: 12.5):**", parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_weight)

def get_weight(message):
    cid = message.chat.id
    try:
        user_data[cid] = {'weight': float(message.text)}
        msg = bot.send_message(cid, "✏️ **أدخل سعر الغرام بالدينار (مثال: 49000):**", parse_mode="Markdown")
        bot.register_next_step_handler(msg, get_gram_price)
    except:
        bot.send_message(cid, "⚠️ خطأ! أرسل رقماً فقط. حاول مرة أخرى.")

def get_gram_price(message):
    cid = message.chat.id
    try:
        user_data[cid]['gram_price'] = float(message.text)
        msg = bot.send_message(cid, "💵 **أدخل سعر صرف الـ 100 دولار اليوم (مثال: 155000):**", parse_mode="Markdown")
        bot.register_next_step_handler(msg, final_calculation)
    except:
        bot.send_message(cid, "⚠️ خطأ! أرسل رقماً فقط.")

def final_calculation(message):
    cid = message.chat.id
    try:
        rate_100 = float(message.text)
        weight = user_data[cid]['weight']
        gram_price = user_data[cid]['gram_price']
        
        # --- الخدعة البصرية (التحميل الوهمي) ---
        loading_msg = bot.send_message(cid, "⏳ **جاري الاتصال ببيانات السوق...**", parse_mode="Markdown")
        time.sleep(1)
        bot.edit_message_text("🧮 **يتم الآن تصفية الحساب واستخراج الفاتورة...**", cid, loading_msg.message_id, parse_mode="Markdown")
        time.sleep(1)
        
        # --- العمليات الحسابية (الطريقة العراقية) ---
        total_iqd = weight * gram_price
        # حساب كم ورقة 100$ يحتاج (نجبر الكسر للأعلى)
        papers_needed = math.ceil(total_iqd / rate_100) * 100
        # حساب الباقي الذي يجب إرجاعه للزبون بالدينار
        paid_iqd_value = (papers_needed / 100) * rate_100
        change_iqd = paid_iqd_value - total_iqd
        change_usd_fraction = change_iqd / (rate_100 / 100)
        
        # رقم الترند الوهمي
        trend_num = int(time.time()) % 1000 + 1000
        
        # --- تصميم الفاتورة (أرتب من الصورة) ---
        invoice = f"""
<b>Dubai Master System | الترند: {trend_num}</b>
━━━━━━━━━━━━━━━━━━
<b>📊 تصفية الحسبة النهائية (سوق الذهب):</b>

🔄 <b>العملية:</b> 🔴 شراء من زبون
⚖️ <b>الوزن:</b> {weight} غرام
💎 <b>سعر الغرام:</b> {gram_price:,.0f} د.ع
💵 <b>سعر صرف الـ 100$:</b> {rate_100:,.0f} د.ع
━━━━━━━━━━━━━━━━━━
💰 <b>الصافي بالدينار:</b> <b>{total_iqd:,.0f} د.ع</b>

<b>💵 في حال الدفع بالدولار (التصفية):</b>
💵 المستلم بالورق الصافي: <b>{papers_needed}$</b>
↩️ يُرجع للزبون بالدينار: <b>{change_iqd:,.0f} د.ع</b>
<i>*(قيمة الـ {change_usd_fraction:.2f}$ المتبقية بالكسر)*</i>
━━━━━━━━━━━━━━━━━━
✅ <i>تم إنجاز الحسبة بدقة.</i>
"""
        bot.delete_message(cid, loading_msg.message_id)
        bot.send_message(cid, invoice, parse_mode="HTML")
        
    except Exception as e:
        bot.send_message(cid, "⚠️ حدث خطأ في الأرقام، حاول مجدداً.")

bot.polling(none_stop=True)
    
