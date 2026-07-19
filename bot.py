# bot.py
import os
import time
import telebot
from telebot import types
from utils import (
    LANG_PACKS, reset_user_session, format_currency_iqd_usd,
    generate_aramky_invoice, generate_customer_invoice
)

# 1️⃣ جلب مفتاح التوكن والآدمن من بيئة السيرفر
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_SERVER_HIDDEN_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))

bot = telebot.TeleBot(BOT_TOKEN)

# قاعدة البيانات الافتراضية للجلسات
USERS_DB = {}
SYSTEM_CONFIG = {
    'trial_duration_text': "3 أيام",  
    'trial_seconds': 3 * 24 * 60 * 60
}

# فحص صلاحية المشترك الفورية (حل مشكلة تعليق القفل)
def check_user_access(user_id):
    if user_id == ADMIN_ID:
        return True
    user = USERS_DB.get(user_id)
    if not user:
        return False
    if user.get('is_active') is True:
        return True
    if time.time() < user.get('trial_end', 0):
        return True
    return False

# 2️⃣ دالة إرسال القائمة الرئيسية بنظافة واختصار
def send_main_menu(user_id):
    USERS_DB[user_id]['step'] = 'main_menu' # تثبيت الحالة لمنع التداخل
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("⚖️ ابدأ حساب عملية ذهبية جديدة", callback_data="op_start_calc"),
        types.InlineKeyboardButton("⚙️ إعدادات الحساب والدعم", callback_data="op_settings")
    )
    bot.send_message(
        user_id, 
        "📋 *القائمة الرئيسية لنظام نواة الذهب:*\nيرجى اختيار العملية المطلوبة من الأزرار أدناه:", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

# 3️⃣ أوامر البداية والتسجيل وتصفير البيانات
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.chat.id
    
    # تصفير الملفات القديمة بالكامل والبدء من جديد بنظافة
    reset_user_session(user_id, USERS_DB)
    user = USERS_DB[user_id]
    
    welcome_text = (
        f"{LANG_PACKS[user['lang']]['welcome']}\n\n"
        f"{LANG_PACKS[user['lang']]['trial_msg'].format(SYSTEM_CONFIG['trial_duration_text'])}\n\n"
        f"----------------------------------------\n"
        f"{LANG_PACKS[user['lang']]['register_start']}"
    )
    bot.send_message(user_id, welcome_text, parse_mode="Markdown")
    bot.send_message(user_id, "📍 يرجى إرسال *اسم محل الذهب* الخاص بك للبدء:")
    USERS_DB[user_id]['step'] = 'get_shop_name'

# 4️⃣ معالجة ضغط أزرار القائمة الرئيسية (تغيير الحالة الفوري)
@bot.callback_query_handler(func=lambda call: call.data.startswith("op_"))
def handle_main_menu_buttons(call):
    user_id = call.message.chat.id
    action = call.data
    
    bot.answer_callback_query(call.id)
    
    if not check_user_access(user_id):
        bot.send_message(user_id, LANG_PACKS['ar']['locked'], parse_mode="Markdown")
        return

    if action == "op_start_calc":
        # تغيير الحالة فوراً لمنع تكرار رسالة "يرجى الاختيار"
        USERS_DB[user_id]['step'] = 'waiting_for_gold_weight'
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "✍️ ممتاز، الآن أرسل *وزن الذهب بالغرام* فقط (مثال: 24.5):")

    elif action == "op_settings":
        USERS_DB[user_id]['step'] = 'inside_settings'
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "⚙️ واجهة الإعدادات: نظامك نشط ومحدث. للتواصل مع الدعم الفني لشركة آرامكي: @Aramky_Support")
        time.sleep(2)
        send_main_menu(user_id)

# 5️⃣ مستقبل النصوص الذكي (يتحكم بالخطوات ويمنع لغوة الـ Loop)
@bot.message_handler(func=lambda msg: True)
def handle_all_text_inputs(message):
    user_id = message.chat.id
    
    # تأمين وجود الحساب في الذاكرة
    if user_id not in USERS_DB:
        reset_user_session(user_id, USERS_DB)
        
    user_data = USERS_DB[user_id]
    current_step = user_data.get('step', '')

    # خطوة أ: استلام اسم المحل أثناء التسجيل
    if current_step == 'get_shop_name':
        USERS_DB[user_id]['shop_name'] = message.text
        markup = types.InlineKeyboardMarkup(row_width=2)
        regions = ["الكاظمية", "المنصور", "الكرادة", "شارع النهر", "المحافظات"]
        buttons = [types.InlineKeyboardButton(r, callback_data=f"set_region_{r}") for r in regions]
        markup.add(*buttons)
        bot.send_message(user_id, "🗺️ اختر منطقة المحل لتصنيف حسابك في النظام:", reply_markup=markup)
        
    # خطوة ب: استلام وزن الذهب وحساب الفاتورة
    elif current_step == 'waiting_for_gold_weight':
        try:
            weight = float(message.text)
            
            # خدعة جاري تحميل العمليات الذهبية لامتصاص ضعف النت
            load = bot.send_message(user_id, LANG_PACKS['ar']['loading'])
            time.sleep(1.8)
            bot.delete_message(user_id, load.message_id)
            
            # توليد وإرسال الفاتورة الفخمة للزبائن
            shop_name = user_data.get('shop_name', 'محل الذهب')
            inv = generate_customer_invoice(shop_name, "زبون كريم", weight, weight * 62.5, lang=user_data.get('lang', 'ar'))
            bot.send_message(user_id, inv, parse_mode="Markdown")
            
            # إعادة المستخدم إلى القائمة الرئيسية بنظافة وتأمين حالته الجديدة
            send_main_menu(user_id)
            
        except ValueError:
            bot.send_message(user_id, "❌ عذراً، يرجى إدخال وزن الذهب كأرقام فقط (مثال: 21.4):")
            
    # خطوة ج: إذا كان في القائمة الرئيسية وكتب نصاً عشوائياً بدلاً من الضغط على الأزرار
    elif current_step == 'main_menu':
        bot.send_message(user_id, "⚠️ تنبيه: يرجى استخدام *الأزرار الظاهرة أسفل الشاشة* واختيار العملية المطلوبة، لا تكتب نصاً مباشراً.")

# 6️⃣ معالجة اختيار المنطقة وإكمال التسجيل الافتراضي
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_region_"))
def process_region(call):
    user_id = call.message.chat.id
    region = call.data.split("_")[2]
    
    USERS_DB[user_id]['region'] = region
    USERS_DB[user_id]['trial_end'] = time.time() + SYSTEM_CONFIG['trial_seconds']
    
    bot.delete_message(user_id, call.message.message_id)
    
    # تفعيل واجهة العميل الرئيسية فوراً
    send_main_menu(user_id)
    
    # إشعار صامت للآدمن بالجرد
    admin_alert = f"🔔 *عميل جديد سجل في النظام*\n🆔 المعرف: `{user_id}`\n🏪 المحل: {USERS_DB[user_id]['shop_name']}\n📍 المنطقة: {region}"
    bot.send_message(ADMIN_ID, admin_alert, parse_mode="Markdown")

# 7️⃣ لوحة تحكم الإدارة (الآدمن)
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📊 جرد العملاء حسب المناطق", callback_data="admin_view_regions"),
        types.InlineKeyboardButton("⏱️ تعديل وقت الفترة المجانية", callback_data="admin_change_trial"),
        types.InlineKeyboardButton("🔓 تفعيل يدوي فوري لمشترك (فك القفل)", callback_data="admin_activate_user")
    )
    bot.send_message(ADMIN_ID, "👑 *لوحة إدارة نظام نواة الذهب المنسقة*", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def process_admin_callbacks(call):
    if call.message.chat.id != ADMIN_ID:
        return
    action = call.data
    
    if action == "admin_view_regions":
        report = "📋 *تقرير جرد وتعداد العملاء الفعلي حسب المناطق:*\n\n"
        regions_list = ["الكاظمية", "المنصور", "الكرادة", "شارع النهر", "المحافظات"]
        for reg in regions_list:
            report += f"📍 *منطقة {reg}:*\n"
            count = 0
            for uid, data in USERS_DB.items():
                if data.get('region') == reg:
                    status_icon = "🟢 نشط" if check_user_access(uid) else "🔴 مقفل"
                    report += f"  ← 🏬 {data.get('shop_name')} (`{uid}`) - {status_icon}\n"
                    count += 1
            if count == 0:
                report += "  ← _لا يوجد عملاء_\n"
            report += "---------------------\n"
        bot.send_message(ADMIN_ID, report, parse_mode="Markdown")
        
    elif action == "admin_change_trial":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("⏱️ نصف ساعة", callback_data="set_time_30m"),
            types.InlineKeyboardButton("⏳ 3 ساعات", callback_data="set_time_3h"),
            types.InlineKeyboardButton("📅 3 أيام", callback_data="set_time_3d"),
            types.InlineKeyboardButton("📅 7 أيام", callback_data="set_time_7d")
        )
        bot.send_message(ADMIN_ID, "⏱️ *اختر مدة الفترة المجانية الافتراضية الجديدة:*", reply_markup=markup, parse_mode="Markdown")

    elif action == "admin_activate_user":
        msg = bot.send_message(ADMIN_ID, "✍️ يرجى إرسال (ID المعرف) الخاص بالعميل لتفعيله فوراً وفك قفل النظام عنه:")
        bot.register_next_step_handler(msg, process_manual_activation)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_time_"))
def process_time_change(call):
    time_code = call.data.split("_")[2]
    if time_code == "30m":
        SYSTEM_CONFIG['trial_duration_text'] = "30 دقيقة"
        SYSTEM_CONFIG['trial_seconds'] = 30 * 60
    elif time_code == "3h":
        SYSTEM_CONFIG['trial_duration_text'] = "3 ساعات"
        SYSTEM_CONFIG['trial_seconds'] = 3 * 60 * 60
    elif time_code == "3d":
        SYSTEM_CONFIG['trial_duration_text'] = "3 أيام"
        SYSTEM_CONFIG['trial_seconds'] = 3 * 24 * 60 * 60
    elif time_code == "7d":
        SYSTEM_CONFIG['trial_duration_text'] = "7 أيام"
        SYSTEM_CONFIG['trial_seconds'] = 7 * 24 * 60 * 60
    bot.send_message(ADMIN_ID, f"✅ تم تعديل النظام! المدة المعتمدة الآن: *{SYSTEM_CONFIG['trial_duration_text']}*", parse_mode="Markdown")

def process_manual_activation(message):
    try:
        target_id = int(message.text)
        if target_id in USERS_DB:
            # الحل النهائي والمباشر لفك القفل بدون تعليق
            USERS_DB[target_id]['is_active'] = True  
            USERS_DB[target_id]['status'] = 'active'
            
            shop_name = USERS_DB[target_id].get('shop_name', 'محل الذهب')
            aramky_inv = generate_aramky_invoice(target_id, shop_name, "الباقة الماسية المدعومة", "سنوي / دائم")
            
            bot.send_message(ADMIN_ID, f"✅ تم تفعيل العميل بنجاح!\n\n{aramky_inv}", parse_mode="Markdown")
            bot.send_message(target_id, f"🔓 *تهانينا! تم قبول اشتراكك وفك قفل النظام بنجاح.*\n\n{aramky_inv}", parse_mode="Markdown")
            time.sleep(1.5)
            send_main_menu(target_id)
        else:
            bot.send_message(ADMIN_ID, "❌ المعرف غير مسجل بالنظام حالياً.")
    except ValueError:
        bot.send_message(ADMIN_ID, "❌ يرجى إرسال أرقام صحيحة فقط.")

# تشغيل مستمر ومحمي ضد تقطيع الإنترنت بالعراق
if __name__ == "__main__":
    print("🚀 GoldenCalc_Bot is fully updated and running perfectly...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
