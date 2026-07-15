import telebot, os, utils, buy, sell
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Active & Sleeping Disabled"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    print(f"🔥 Flask server is starting on port {port}...")
    app.run(host='0.0.0.0', port=port)

Thread(target=run_server).start()

print("🔑 Connecting to Telegram API...")
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
bot.remove_webhook()
print("🤖 Telegram Bot has started polling successfully and is ready to receive messages!")

@bot.message_handler(commands=['start'])
def start(m):
    is_active, count = utils.check_user(m.chat.id)
    if not is_active:
        bot.send_message(m.chat.id, "⚠️ عذراً، انتهت الفترة التجريبية المجانية (7 أيام). يرجى الاشتراك لتفعيل الخدمة.")
        return
        
    welcome_text = (
        f"👋 **أهلاً بك في نظام الصياغة الذكي**\n\n"
        f"👥 أنت العميل رقم: `{count}` في نظامنا المتكامل.\n"
        f"🎁 لقد حصلت على اشتراك تجريبي مجاني لمدة **7 أيام**.\n\n"
        f"استخدم الأزرار بالأسفل لبدء العمليات فوراً وبكل دقة 👇"
    )
    utils.send_main_menu(bot, m.chat.id, welcome_text)

@bot.message_handler(func=lambda m: m.text == "⚙️ إعدادات الصباح")
def morning_settings(m):
    is_active, _ = utils.check_user(m.chat.id)
    if not is_active: return
    
    data = utils.get_data()
    s = data['settings']
    
    msg = (f"⚙️ **إعدادات الصباح الحالية**\n"
           f"━━━━━━━━━━━━━━━━━━\n"
           f"🔹 سعر مثقال 21: {s['mithqal_21']:,.0f} د.ع\n"
           f"🔹 سعر مثقال 18: {s['mithqal_18']:,.0f} د.ع\n"
           f"🔨 صياغة غرام 21: {s['labor_21']:,.0f} د.ع\n"
           f"🔨 صياغة غرام 18: {s['labor_18']:,.0f} د.ع\n"
           f"💵 سعر الـ 100 دولار: {s['usd_100']:,.0f} د.ع\n"
           f"━━━━━━━━━━━━━━━━━━\n"
           f"💡 لتحديث أي قيمة، أرسل الأمر التالي:\n"
           f"`/set [المفتاح] [السعر]`\n\n"
           f"⚙️ **المفاتيح المتاحة:**\n"
           f"• `mithqal_21`\n"
           f"• `mithqal_18`\n"
           f"• `labor_21`\n"
           f"• `labor_18`\n"
           f"• `usd_100`\n\n"
           f"مثال لتحديث الدولار:\n`/set usd_100 153500`")
    bot.send_message(m.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['set'])
def update_val(m):
    try:
        parts = m.text.split()
        if len(parts) != 3:
            bot.reply_to(m, "⚠️ صيغة خاطئة. اكتبها هكذا: `/set usd_100 153000`")
            return
        key, val = parts[1], parts[2]
        utils.update_setting(key, val)
        bot.reply_to(m, f"✅ تم تحديث الإعداد `{key}` إلى `{int(val):,}` بنجاح!")
    except:
        bot.reply_to(m, "⚠️ حدث خطأ في إدراج البيانات.")

@bot.message_handler(func=lambda m: True)
def router(m):
    is_active, _ = utils.check_user(m.chat.id)
    if not is_active:
        bot.send_message(m.chat.id, "⚠️ انتهى اشتراكك. يرجى التواصل مع الدعم لتفعيل الحساب.")
        return

    if m.text == "💰 بيع للزبون":
        sell.handle(m, bot)
    elif m.text == "⚖️ شراء من زبون":
        buy.handle(m, bot)

bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
