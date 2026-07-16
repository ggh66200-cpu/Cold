import telebot, os, utils
from telebot import types

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

@bot.message_handler(commands=['start'])
def start(m):
    # هنا يتم فحص الاشتراك (نظام معزول)
    is_active, count, lang = utils.check_user(m.chat.id)
    
    # رسالة اختيار اللغة في البداية
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("العربية 🇮🇶", callback_data="lang_ar"))
    markup.add(types.InlineKeyboardButton("Kurdî ☀️", callback_data="lang_ku"))
    markup.add(types.InlineKeyboardButton("English 🇺🇸", callback_data="lang_en"))
    
    bot.send_message(m.chat.id, "👋 أهلاً بك! يرجى اختيار لغتك المفضلة:\n\nPlease select your preferred language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    lang = call.data.split("_")[1]
    utils.set_lang(call.message.chat.id, lang)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    msg = "تم حفظ اللغة بنجاح!" if lang == 'ar' else ("زمانەکە هەڵبژێردرا!" if lang == 'ku' else "Language saved!")
    bot.send_message(call.message.chat.id, msg, reply_markup=utils.get_keyboard(lang))

@bot.message_handler(func=lambda m: True)
def router(m):
    # جلب اللغة الحالية للمستخدم
    data = utils.get_data()
    user_data = data['users'].get(str(m.chat.id))
    if not user_data: 
        bot.send_message(m.chat.id, "يرجى الضغط على /start")
        return
    
    lang = user_data.get('lang', 'ar')
    text = m.text.strip()
    
    # هنا تتعامل مع الأزرار بناءً على اللغة
    if text == utils.get_text(lang, 'settings'):
        bot.send_message(m.chat.id, "⚙️ " + utils.get_text(lang, 'settings'))
        # كمل باقي منطق الإعدادات بنفس الطريقة...
    elif text == utils.get_text(lang, 'sell'):
        bot.send_message(m.chat.id, "💰 " + utils.get_text(lang, 'sell'))
        # كمل باقي منطق البيع...
