import utils
import time

def handle(m, bot):
    msg = bot.send_message(m.chat.id, "💰 أدخل وزن الذهب (بيع للزبون):")
    bot.register_next_step_handler(msg, process, bot)

def process(m, bot):
    try:
        weight = float(m.text)
        load_msg = bot.send_message(m.chat.id, "⏳ جاري حساب فاتورة البيع...")
        
        data = utils.get_data()
        total = weight * (data['sell_21'] / 5)
        
        invoice = utils.format_invoice(int(time.time()), weight, total, type="sell")
        
        bot.edit_message_text(invoice, m.chat.id, load_msg.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(m, "⚠️ خطأ في الإدخال، يرجى كتابة الأرقام فقط.")
