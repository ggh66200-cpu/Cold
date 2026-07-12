import utils
import time

def handle(m, bot):
    msg = bot.send_message(m.chat.id, "⚖️ أدخل وزن الذهب (شراء من الزبون):")
    bot.register_next_step_handler(msg, process, bot)

def process(m, bot):
    try:
        weight = float(m.text)
        load_msg = bot.send_message(m.chat.id, "⏳ جاري حساب فاتورة الشراء...")
        
        data = utils.get_data()
        
        # العملية الحسابية
        total = weight * (data['buy_21'] / 5)
        usd_100_price = data['usd_100']
        
        # حساب كم ورقة فئة 100$ والباقي بالعراقي
        papers = (total // usd_100_price) * 100
        rem = total - ((papers / 100) * usd_100_price)
        
        # إنشاء الفاتورة
        invoice = utils.format_invoice(int(time.time()), weight, total, papers, rem, "buy")
        
        bot.edit_message_text(invoice, m.chat.id, load_msg.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(m, "⚠️ خطأ في الإدخال، يرجى كتابة الأرقام فقط.")
