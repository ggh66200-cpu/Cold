import telebot, os
from handlers import buy, sell, settings

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

@bot.message_handler(commands=['start'])
def start(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("⚖️ شراء من زبون", "💰 بيع للزبون", "☀️ الإعدادات الصباحية")
    bot.send_message(m.chat.id, "💎 **Dubai Master System**\nمرحباً بك في النظام الرئيسي.", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text == "⚖️ شراء من زبون": buy.handle(m, bot)
    elif m.text == "💰 بيع للزبون": sell.handle(m, bot)
    elif m.text == "☀️ الإعدادات الصباحية": settings.handle(m, bot)

if __name__ == "__main__":
    bot.infinity_polling()
