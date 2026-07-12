import utils

def handle(m, bot):
    # رسالة ترحيبية مهذبة ومختصرة وبنفس الوقت واضحة للتعليمات
    text = (
        "☀️ صباح الخير والرزق الوفير!\n\n"
        "حتى نبلش يومنا بحسابات مضبوطة، ياريت تعطينا الأسعار اليوم (بمسافات بينهم) بهذا الترتيب:\n\n"
        "سعر الـ100$ | شراء21 | بيع21 | شراء18 | بيع18\n\n"
        "مثال: 150000 75000 76000 65000 66000"
    )
    msg = bot.send_message(m.chat.id, text)
    bot.register_next_step_handler(msg, process, bot)

def process(m, bot):
    try:
        # استلام الأرقام
        p = [int(x) for x in m.text.split()]
        
        # التأكد من وصول 5 أرقام
        if len(p) != 5:
            raise ValueError
            
        d = utils.get_data()
        d.update({
            'usd_100': p[0], 
            'buy_21': p[1], 
            'sell_21': p[2], 
            'buy_18': p[3], 
            'sell_18': p[4]
        })
        utils.save_data(d)
        
        bot.reply_to(m, "✅ تم حفظ الأسعار بنجاح.. يومك مبارك ورزقك واسع!")
    except: 
        bot.reply_to(m, "⚠️ عذراً، الأسعار لازم تكون 5 أرقام بمسافات. حاول مرة ثانية وتدلل.")
