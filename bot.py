import telebot, os, time, math
from flask import Flask
from threading import Thread

# استدعاء الملفات المعزولة
from langs import LANG
from sub import is_subscribed

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# السيرفر الوهمي
app = Flask(__name__)
@app.route('/')
def home(): return "Dubai Master - System Online"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
Thread(target=run).start()

user_prefs = {}     
daily_settings = {} 
calc_temp = {}      

# ==========================================
# 1. لوحة التحكم
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
    markup.add(LANG[lang]['settings'])
    markup.add(LANG[lang]['lang'], LANG[lang]['sub'])
    
    bot.send_message(cid, f"**Dubai Master System** 💎\nمرحباً بك في نظام سوق الذهب.", reply_markup=markup, parse_mode="Markdown")

# ==========================================
# 2. الإعدادات الصباحية (نظام الرسالة الواحدة السريع)
# ==========================================
@bot.message_handler(func=lambda m: m.text in [LANG['ar']['settings'], LANG['ku']['settings'], LANG['en']['settings']])
def morning_settings(message):
    cid = message.chat.id
    msg = bot.send_message(cid, """☀️ **الإعدادات الصباحية:**

أرسل الأسعار الثلاثة في رسالة واحدة فقط (يفصل بينها مسافة)، بالترتيب التالي:
1️⃣ سعر 100$
2️⃣ سعر مثقال 21
3️⃣ سعر مثقال 18

**مثال للنسخ والتعديل:**
`155000 480000 410000`""", parse_mode="Markdown")
    bot.register_next_step_handler(msg, save_all_settings)

def save_all_settings(message):
    cid = message.chat.id
    try:
        # تنظيف النص وفصل الأرقام
        text = message.text.replace('\n', ' ').replace('-', ' ').strip()
        parts = [float(x) for x in text.split() if x]
        
        if len(parts) >= 3:
            daily_settings[cid] = {'usd_100': parts[0], 'm21': parts[1], 'm18': parts[2]}
            bot.send_message(cid, f"✅ **تم حفظ الإعدادات بنجاح!**\n\n💵 الدولار: {parts[0]:,.0f}\n⚖️ مثقال 21: {parts[1]:,.0f}\n⚖️ مثقال 18: {parts[2]:,.0f}\n\nالنظام الآن جاهز للعمل السريع ⚡️", parse_mode="Markdown")
        else:
            bot.send_message(cid, "⚠️ خطأ! يرجى إرسال 3 أرقام بالضبط كما في المثال.")
    except Exception as e:
        bot.send_message(cid, "⚠️ حدث خطأ في الإدخال، تأكد من كتابة الأرقام فقط بمسافات.")

# ==========================================
# 3. نظام الحاسبة السريع (شراء)
# ==========================================
@bot.message_handler(func=lambda m: m.text in [LANG['ar']['buy'], LANG['ku']['buy'], LANG['en']['buy']])
def start_buy(message):
    cid = message.chat.id
    if cid not in daily_settings:
        bot.send_message(cid, "⚠️ يرجى ضبط **الإعدادات الصباحية ☀️** أولاً!", parse_mode="Markdown")
        return
        
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("عيار 21", callback_data="carat_21"))
    markup.add(telebot.types.InlineKeyboardButton("عيار 18", callback_data="carat_18"))
    bot.send_message(cid, "👇 **اختر عيار الذهب:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('carat_'))
def select_carat(call):
    cid = call.message.chat.id
    carat = call.data.split('_')[1]
    calc_temp[cid] = {'carat': carat}
    
    bot.delete_message(cid, call.message.message_id)
    msg = bot.send_message(cid, f"⚖️ العيار المختار: **{carat}**\n✏️ **أرسل الوزن بالغرام فقط:**", parse_mode="Markdown")
    bot.register_next_step_handler(msg, final_invoice)

def final_invoice(message):
    cid = message.chat.id
    try:
        weight = float(message.text)
    except:
        bot.send_message(cid, "⚠️ خطأ! يرجى إرسال أرقام فقط.")
        return

    carat = calc_temp[cid]['carat']
    rate_100 = daily_settings[cid]['usd_100']
    mithqal_price = daily_settings[cid]['m21'] if carat == '21' else daily_settings[cid]['m18']
    gram_price = mithqal_price / 5  
    
    loading_msg = bot.send_message(cid, "⏳ **جاري التصفية...**", parse_mode="Markdown")
    time.sleep(1.5)
    
    total_iqd = weight * gram_price
    papers_needed = math.ceil(total_iqd / rate_100) * 100
    paid_iqd_value = (papers_needed / 100) * rate_100
    change_iqd = paid_iqd_value - total_iqd
    change_usd = change_iqd / (rate_100 / 100)
    
    trend_num = int(time.time()) % 1000 + 1000
    
    invoice = f"""
<b>Dubai Master System | الترند: {trend_num}</b>
━━━━━━━━━━━━━━━━━━
<b>📊 تصفية الحسبة (سوق الذهب):</b>

🔄 <b>العملية:</b> 🔴 شراء من زبون
⚖️ <b>الوزن:</b> {weight} غرام (عيار {carat})
💎 <b>سعر الغرام:</b> {gram_price:,.0f} د.ع <i>(المثقال: {mithqal_price:,.0f})</i>
💵 <b>سعر 100$:</b> {rate_100:,.0f} د.ع
━━━━━━━━━━━━━━━━━━
💰 <b>الصافي بالدينار:</b> <b>{total_iqd:,.0f} د.ع</b>

<b>💵 التصفية بالدولار:</b>
💵 المستلم ورقي: <b>{papers_needed}$</b>
↩️ يُرجع بالدينار: <b>{change_iqd:,.0f} د.ع</b>
<i>*(كسر الدولار المتبقي: {change_usd:.2f}$)*</i>
━━━━━━━━━━━━━━━━━━
✅ <i>تم إنجاز الحسبة بدقة.</i>
"""
    bot.delete_message(cid, loading_msg.message_id)
    bot.send_message(cid, invoice, parse_mode="HTML")

bot.polling(none_stop=True)
