@bot.message_handler(func=lambda m: True)
def router(m):
    # إضافة سطر طباعة لمعرفة ماذا يرسل الزر بالضبط
    print(f"DEBUG: Received text = '{m.text}'") 
    
    if m.text == "💳 الاشتراك":
        bot.send_message(m.chat.id, "💳 للتحويل الماستر كارد:\n`910400201646`", parse_mode="Markdown")
        return
        
    if not utils.check_access(m.chat.id):
        bot.send_message(m.chat.id, "❌ انتهت الفترة التجريبية. اشترك للمتابعة.")
        return
    
    # استخدام مقارنة مرنة (في حال كان هناك فراغات)
    if "شراء" in m.text: 
        buy.handle(m, bot)
    elif "بيع" in m.text: 
        sell.handle(m, bot)
    elif "الإعدادات" in m.text: 
        settings.handle(m, bot)
    else:
        bot.send_message(m.chat.id, f"لم أتعرف على الأمر: {m.text}")
