import telebot, os, utils, buy, sell
from flask import Flask
from threading import Thread

# تشغيل السيرفر
Thread(target=lambda: Flask('').run(host='0.0.0.0', port=8080)).start()
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
ADMIN_ID = 123456789 # <--- ضع الـ ID الخاص بك

@bot.message_handler(commands=['start'])
def start(m):
    utils.register_user(m.chat.id)
    data = utils.get_data()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if data['settings'].get('buy_btn'): markup.add("⚖️ شراء من زبون")
    if data['settings'].get('sell_btn'): markup.add("💰 بيع للزبون")
    if data['settings'].get('sub_btn'): markup.add("💳 الاشتراك")
    bot.send_message(m.chat.id, "مرحباً بك في نظام الذهب الاحترافي.\nالعمليات محمية ومؤمنة.", reply_markup=markup)

@bot.message_handler(commands=['stats'])
def admin_stats(m):
    if m.chat.id != ADMIN_ID: return
    data = utils.get_data()
    bot.reply_to(m, f"📊 عدد المستخدمين الحالي: {data['total_count']}\n🛠 حالة الأزرار: {data['settings']}")

@bot.message_handler(commands=['toggle'])
def toggle(m):
    if m.chat.id != ADMIN_ID: return
    # مثلاً: /toggle sub_btn True
    cmd = m.text.split()
    utils.toggle_button(cmd[1], cmd[2] == 'True')
    bot.reply_to(m, "✅ تم تحديث الحالة.")

@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text == "⚖️ شراء من زبون": buy.handle(m, bot)
    elif m.text == "💰 بيع للزبون": sell.handle(m, bot)
