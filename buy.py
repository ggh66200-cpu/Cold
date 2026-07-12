# داخل دالة ask_weight
msg = bot.send_message(m.chat.id, "⚖️ تدلل، شكد وزن الذهب اللي تريد تشتريه؟ (بالغرام)")

# داخل دالة process
# بعد الحساب، نستخدم الدالة الجديدة:
papers = (total // usd_100_price) * 100
rem = total - ((papers / 100) * usd_100_price)
frac_dollars = (rem / usd_100_price) * 100 # هذا الكسر المتبقي

invoice = utils.generate_invoice(
    "🔴 شراء من زبون", weight, karat, total, 
    usd_100_price, int(papers), rem, frac_dollars
)
bot.send_message(m.chat.id, invoice, parse_mode="Markdown")
