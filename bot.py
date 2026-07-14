# استبدل دالة set_setting القديمة بهذه النسخة:
@bot.message_handler(commands=['set'])
def set_setting(m):
    try:
        # نقسم الرسالة (مثلاً: /set mithqal_21 450000)
        parts = m.text.split()
        if len(parts) != 3:
            bot.reply_to(m, "⚠️ خطأ! استخدم الأمر كالتالي:\n`/set [المفتاح] [القيمة]`\nمثال: `/set mithqal_21 450000`")
            return
            
        key, val = parts[1], parts[2]
        utils.update_setting(key, val)
        bot.reply_to(m, f"✅ تم تحديث {key} إلى {val} بنجاح!")
    except Exception as e:
        bot.reply_to(m, f"⚠️ حدث خطأ: {e}")

# وتأكد أن دالة الإعدادات (⚙️ إعدادات الصباح) تظهر للجميع أيضاً:
@bot.message_handler(func=lambda m: m.text == "⚙️ إعدادات الصباح")
def show_settings(m):
    data = utils.get_data()
    msg = (f"⚙️ **إعدادات المحل الحالية:**\n"
           f"💰 مثقال 21: {data['settings']['mithqal_21']:,}\n"
           f"💰 مثقال 18: {data['settings']['mithqal_18']:,}\n"
           f"🔨 أجور الغرام: {data['settings']['labor_gram']:,}\n"
           f"💵 سعر الدولار: {data['settings']['usd_100']:,}\n\n"
           f"💡 لتغيير أي سعر، أرسل:\n"
           f"`/set [المفتاح] [القيمة]`")
    bot.send_message(m.chat.id, msg, parse_mode="Markdown")
