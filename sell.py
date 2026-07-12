import utils

def handle(m, bot):
    # فحص الاشتراك
    if not utils.is_subscribed(m.chat.id):
        bot.send_message(m.chat.id, "❌ عذراً، اشتراكك منتهي أو غير مفعل.")
        return

    msg = bot.send_message(m.chat.id, "⚖️ شكد وزن الذهب اللي تريد تبيعه للزبون؟")
    bot.register_next_step_handler(msg, process, bot)

def process(m, bot):
    weight = float(m.text)
    # أكمل باقي منطق الحساب هنا...
    # وعند الانتهاء استدعي utils.generate_invoice
