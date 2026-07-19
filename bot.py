import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta

# توكن البوت الخاص بك
TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

# 1. دالة تصفير الملفات وقاعدة البيانات والبدء من جديد
def init_db(reset=False):
    conn = sqlite3.connect('gold_nucleus.db')
    cursor = conn.cursor()
    
    if reset:
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS system_config")
    
    # جدول المستخدمين (يدعم المناطق، اللغات الثلاث، وحالة الاشتراك الفوري والزمني)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            shop_name TEXT,
            region TEXT,
            language TEXT,
            status TEXT DEFAULT 'pending', -- pending, active, expired
            reg_date TEXT,
            trial_end TEXT
        )
    ''')
    
    # جدول إعدادات النظام (حفظ الفترة المجانية بالدقائق لتسهيل التحكم بالساعات ونصف الساعة)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # القيمة الافتراضية للفترة المجانية (7 أيام = 10080 دقيقة)
    cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('trial_minutes', '10080')")
    
    conn.commit()
    conn.close()

# استدعاء الدالة للتأكد من تصفير وبناء النظام بنظافة
init_db(reset=True)

# --- دالات مساعدة لإدارة الوقت والنظام ---

def get_trial_minutes():
    conn = sqlite3.connect('gold_nucleus.db')
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_config WHERE key='trial_minutes'")
    res = cursor.fetchone()
    conn.close()
    return int(res[0]) if res else 10080

def set_trial_minutes(minutes):
    conn = sqlite3.connect('gold_nucleus.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE system_config SET value=? WHERE key='trial_minutes'", (str(minutes),))
    conn.commit()
    conn.close()

def format_duration(minutes):
    if minutes >= 1440:
        return f"{minutes // 1440} أيام"
    elif minutes >= 60:
        return f"{minutes // 60} ساعة"
    else:
        return f"{minutes} دقيقة"

def check_user_status(user_id):
    conn = sqlite3.connect('gold_nucleus.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status, trial_end FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return "not_registered"
    
    status, trial_end_str = user
    if status == 'active':
        return "active"
        
    # التحقق من الوقت المجاني الديناميكي
    trial_end = datetime.strptime(trial_end_str, '%Y-%m-%d %H:%M:%S')
    if datetime.now() < trial_end:
        return "trial"
    else:
        return "expired"

# --- تدفق واجهة المستخدم (الترحيب والاستمارة) ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    status = check_user_status(user_id)
    trial_min = get_trial_minutes()
    duration_text = format_duration(trial_min)
    
    # رسالة ترحيبية تعريفية متكاملة قبل بدء الاستمارة
    welcome_text = (
        f"👑 *مرحباً بك في نظام بوت حسابات الذهب الذكي* 👑\n"
        f"المطور خصيصاً لخدمة صاغة الذهب والمجوهرات بأعلى سرعة وأقل استهلاك للإنترنت.\n\n"
        f"✨ *مميزات النظام:*\n"
        f"• دعم كامل لثلاث لغات (العربية، الكوردية، الإنجليزية).\n"
        f"• حسابات دقيقة وفورية للأوزان والأجور والأرباح لحظة بلحظة.\n"
        f"• يعمل بكفاءة استثنائية حتى في ظروف الإنترنت الضعيف.\n\n"
        f"🎁 نوفر لك فترة تجريبية مجانية بالكامل مدتها: *{duration_text}*.\n\n"
        f"اضغط على الزر أدناه للبدء في ملء استمارة الاشتراك وتفعيل حسابك فوراً."
    )
    
    markup = types.InlineKeyboardMarkup()
    if status == "not_registered":
        markup.add(types.InlineKeyboardButton("📝 البدء وملء استمارة الحساب", callback_data="start_reg"))
    else:
        markup.add(types.InlineKeyboardButton("🚀 الدخول إلى لوحة التحكم", callback_data="main_menu"))
        
    bot.send_message(user_id, welcome_text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.message.chat.id
    
    # حل مشكلة ضعف النت: تعديل نفس الرسالة لمنع التكرار وتوفير البيانات
    if call.data == "start_reg":
        # بدء استمارة المعلومات خطوة بخطوة عبر الأزرار لتسريع العملية
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("العربية 🇸🇦", callback_data="set_lang_ar"))
        markup.add(types.InlineKeyboardButton("Kurdî ☀️", callback_data="set_lang_ku"))
        markup.add(types.InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en"))
        bot.edit_message_text("الرجاء اختيار لغة النظام المعتمدة المريحة لك:\nتکایە زمانی پەسەندکراوی سیستمەکە هەڵبژێرە:\nPlease select your preferred system language:", 
                              chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)

    elif call.data.startswith("set_lang_"):
        lang = call.data.split("_")[2]
        # حفظ مبدئي للمستخدم والانتقال للمناطق
        conn = sqlite3.connect('gold_nucleus.db')
        cursor = conn.cursor()
        trial_min = get_trial_minutes()
        trial_end_time = (datetime.now() + timedelta(minutes=trial_min)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("INSERT OR REPLACE INTO users (user_id, language, reg_date, trial_end, status) VALUES (?, ?, ?, ?, 'pending')", 
                       (user_id, lang, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), trial_end_time))
        conn.commit()
        conn.close()
        
        # اختيار المنطقة لغرض الجرد لاحقاً
        markup = types.InlineKeyboardMarkup()
        # أمثلة لمناطق الكاظمية ومناطق أخرى لتسهيل الجرد الإداري
        markup.add(types.InlineKeyboardButton("سوق الكاظمية التجاري", callback_data="set_reg_الكاظمية"))
        markup.add(types.InlineKeyboardButton("بغداد - الكرخ", callback_data="set_reg_الكرخ"))
        markup.add(types.InlineKeyboardButton("بغداد - الرصافة", callback_data="set_reg_الرصافة"))
        markup.add(types.InlineKeyboardButton("منطقة أخرى", callback_data="set_reg_أخرى"))
        
        bot.edit_message_text("📍 يرجى تحديد المنطقة الجغرافية لمتجرك لتنظيم الفواتير والجرد الخاص بك:", 
                              chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)

    elif call.data.startswith("set_reg_"):
        region = call.data.split("_")[2]
        conn = sqlite3.connect('gold_nucleus.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET region=? WHERE user_id=?", (region, user_id))
        conn.commit()
        conn.close()
        
        # رسالة اكتمال التسجيل بنجاح مع الفحص الفوري للاشتراك
        bot.edit_message_text("✅ تم تسجيل معلوماتك بنجاح! يتم الآن تفعيل الفترة المجانية الخاصة بك والدخول للنظام تلقائياً.", 
                              chat_id=user_id, message_id=call.message.message_id)
        # إرسال إشعار للمطور/الأدمن فوراً للموافقة أو المتابعة
        
    # --- لوحة تحكم الإدارة وجرد المناطق وتغيير الوقت المجاني لحظياً ---
    elif call.data == "admin_panel":
        show_admin_panel(user_id, call.message.message_id)
        
    elif call.data == "admin_jard_region":
        conn = sqlite3.connect('gold_nucleus.db')
        cursor = conn.cursor()
        cursor.execute("SELECT region, COUNT(*) FROM users GROUP BY region")
        rows = cursor.fetchall()
        conn.close()
        
        report = "📊 *جرد إحصائيات العملاء حسب المناطق الحالية:*\n\n"
        for row in rows:
            report += f"📍 {row[0]}: {row[1]} عميل/محال\n"
            
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ العودة للوحة الإدارة", callback_data="admin_panel"))
        bot.edit_message_text(report, chat_id=user_id, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup)

    elif call.data == "admin_change_trial":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⏱️ نصف ساعة (30 دقيقة)", callback_data="conf_trial_30"))
        markup.add(types.InlineKeyboardButton("⏳ ساعتان (120 دقيقة)", callback_data="conf_trial_120"))
        markup.add(types.InlineKeyboardButton("📅 3 أيام", callback_data="conf_trial_4320"))
        markup.add(types.InlineKeyboardButton("📅 7 أيام (الافتراضي)", callback_data="conf_trial_10080"))
        markup.add(types.InlineKeyboardButton("⬅️ العودة", callback_data="admin_panel"))
        bot.edit_message_text("⚙️ *إعدادات التحكم بالفترة التجريبية للأنظمة والتعريف التلقائي:*\nاختر المدة التي ستظهر تلقائياً للعملاء الجدد في رسائل الترحيب:", 
                              chat_id=user_id, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup)

    elif call.data.startswith("conf_trial_"):
        minutes = int(call.data.split("_")[2])
        set_trial_minutes(minutes)
        duration_txt = format_duration(minutes)
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ العودة للوحة الإدارة", callback_data="admin_panel"))
        bot.edit_message_text(f"🎯 تم تحديث النظام بنجاح! الفترة المجانية للترحيب والتعريف أصبحت الآن: *{duration_txt}* وتطبق فوراً على الحسابات الجديدة والملفات المصفرة.", 
                              chat_id=user_id, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_admin_panel(user_id, message_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 جرد العملاء حسب المناطق", callback_data="admin_jard_region"))
    markup.add(types.InlineKeyboardButton("⏱️ تعديل وزيادة/تقليل الفترة المجانية", callback_data="admin_change_trial"))
    bot.edit_message_text("🛠️ *لوحة الإدارة والتحكم الذكي لنظام آرامكي الرقمي*:\nيمكنك تعديل الإعدادات والتحقق من حسابات العملاء بسلاسة وسرعة عبر الأزرار المختصرة.", 
                          chat_id=user_id, message_id=message_id, parse_mode='Markdown', reply_markup=markup)
