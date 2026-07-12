import utils

def handle(m, bot):
    # فحص الاشتراك
    if not utils.is_subscribed(m.chat.id):
        bot.send_message(m.chat.id, "❌ عذراً، اشتراكك منتهي أو غير مفعل. تواصل مع الإدارة.")
        return
    
    msg = bot.send_message(m.chat.id, "⚖️ تدلل، شكد وزن الذهب اللي تريد تشتريه؟ (بالغرام)")
    bot.register_next_step_handler(msg, process, bot)

def process(m, bot):
    weight = float(m.text)
    # أكمل باقي منطق الحساب هنا كما كان عندك...
    # وعند الانتهاء استدعي utils.generate_invoice لإرسال الفاتورة
