# bot.py
import os
import time
import telebot
from telebot import types
from utils import (
    LANG_PACKS, reset_user_session, format_currency_iqd_usd,
    generate_aramky_invoice, generate_customer_invoice
)

# جلب مفتاح التوكن والآدمن من السيرفر تلقائياً لضمان الأمان الكامل
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_SERVER_HIDDEN_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))

bot = telebot.TeleBot(BOT_TOKEN)

# قاعدة بيانات وهمية في الذاكرة (يفضل ربطها بـ SQLite أو PostgreSQL لاحقاً بنفس الهيكلية)
USERS_DB = {}
SYSTEM_CONFIG = {
    'trial_duration_text': "3 أيام",  # يمكن للآدمن تعديلها فوراً (أيام، ساعات، أو نصف ساعة)
    'trial_seconds': 3 * 24 * 60 * 60
}

# فحص فوري لحالة المشترك (حل مشكلة بقاء النظام مقفلاً بعد قبول الاشتراك)
def check_user_access(user_id):
    if user_id == ADMIN_ID:
        return True
    
    user = USERS_DB.get(user_id)
    if not user:
        return False
    
    # إذا الآدمن مفعله مباشرة أو فترته التجريبية ما زالت سارية
    if user.get('is_active') is True:
        return True
    
    if time.time() < user.get('trial_end', 0):
        return True
        
    return False

# ----------------- أوامر المشتركين والبدء -----------------

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.chat.id
    
    # تصفير الملفات والبيانات القديمة والبدء من جديد بنظافة تامة
    reset_user_session(user_id, USERS_DB)
    user = USERS_DB[user_id]
    
    # رسالة ترحيبية فخمة لتعريف النظام (كلام معسل رسمي وطيب)
    welcome_text = (
        f"{LANG_PACKS[user['lang']]['welcome']}\n\n"
        f"{LANG_PACKS[user['lang']]['trial_msg'].format(SYSTEM_CONFIG['trial_duration_text'])}\n\n"
        f"----------------------------------------\n"
        f"{LANG_PACKS[user['lang']]['register_start']}"
    )
    
    # بدء استمارة معلومات العميل فوراً بعد الترحيب
    bot.send_message(user_id, welcome_text, parse_mode="Markdown")
    bot.send_message(user_id, "📍 يرجى إرسال *اسم محل الذهب* الخاص بك:")
    USERS_DB[user_id]['step'] = 'get_shop_name'

@bot.message_handler(func=lambda msg: USERS_DB.get(msg.chat.id) and USERS_DB[msg.chat.id]['step'] == 'get_shop_name')
def process_shop_name(message):
    user_id = message.chat.id
    USERS_DB[user_id]['shop_name'] = message.text
    
    # اختيار المنطقة لسهولة جرد العملاء لاحقاً في لوحة التحكم
    markup = types.InlineKeyboardMarkup(row_width=2)
    regions = ["الكاظمية", "المنصور", "الكرادة", "شارع النهر", "المحافظات"]
    buttons = [types.InlineKeyboardButton(r, callback_data=f"set_region_{r}") for r in regions]
    markup.add(*buttons)
    
    bot.send_message(user_id, "🗺️ اختر منطقة المحل لتصنيف حسابك في النظام للمتابعة الدورية:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_region_"))
def process_region(call):
    user_id = call.message.chat.id
    region = call.data.split("_")[2]
    
    USERS_DB[user_id]['region'] = region
    USERS_DB[user_id]['trial_end'] = time.time() + SYSTEM_CONFIG['trial_seconds']
    USERS_DB[user_id]['step'] = 'completed'
    
    # خدعة جاري تحميل العمليات الذهبية (لامتصاص ضعف الإنترنت العراقي)
    loading_msg = bot.send_message(user_id, LANG_PACKS[USERS_DB[user_id]['lang']]['loading'])
    time.sleep(2.5) # إيهام المستخدم بالمعالجة العميقة لضمان ثبات الاتصال
    bot.delete_message(user_id, loading_msg.message_id)
    
    success_text = (
        f"✅ *تم اكتمال التسجيل بنجاح! *\n"
        f"🏢 المحل: {USERS_DB[user_id]['shop_name']}\n"
        f"📍 المنطقة: {region}\n"
        f"🎁 تفعلت باقتك التجريبية بنجاح لمدة ({SYSTEM_CONFIG['trial_duration_text']}).\n\n"
        f"لإجراء عملية حسابية وتوليد فاتورة زبون، أرسل الأمر: /calculate"
    )
    bot.send_message(user_id, success_text, parse_mode="Markdown")
    
    # إشعار تلقائي للآدمن بانضمام عميل جديد من أجل التوثيق والجرد
    admin_alert = f"🔔 *عميل جديد سجل في النظام*\n🆔 المعرف: `{user_id}`\n🏪 المحل: {USERS_DB[user_id]['shop_name']}\n📍 المنطقة: {region}"
    bot.send_message(ADMIN_ID, admin_alert, parse_mode="Markdown")

# ----------------- نظام الفواتير المحمي -----------------

@bot.message_handler(commands=['calculate'])
def start_calculation(message):
    user_id = message.chat.id
    
    # التحقق الفوري والإجباري من القفل والاشتراك (حل جذري للتعليق)
    if not check_user_access(user_id):
        bot.send_message(user_id, LANG_PACKS['ar']['locked'], parse_mode="Markdown")
        return

    # محاكاة سريعة لإنتاج فاتورة زبون تجريبية
    shop_name = USERS_DB[user_id].get('shop_name', "محل الذهب المميز")
    customer_inv = generate_customer_invoice(shop_name, "أبو مصطفى الخفاجي", 24.5, 1250, lang='ar')
    
    # تطبيق خدعة التحميل قبل إرسال الفاتورة الفخمة لحماية تجربة المستخدم عند ضعف النت
    load = bot.send_message(user_id, LANG_PACKS['ar']['loading'])
    time.sleep(1.5)
    bot.delete_message(user_id, load.message_id)
    
    bot.send_message(user_id, customer_inv, parse_mode="Markdown")

# ----------------- ⚙️ لوحة تحكم الإدارة والآدمن المنسقة -----------------

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
    
    bot.send_message(ADMIN_ID, "👑 *لوحة إدارة نظام نواة الذهب المنسقة*\nتحكم بكافة مفاصل النظام والعملاء بكل سهولة وسرعة اختصاراً للوقت وضعف الإنترنت العراقي.", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def process_admin_callbacks(call):
    if call.message.chat.id != ADMIN_ID:
        return
        
    action = call.data
    
    if action == "admin_view_regions":
        # جرد منسق ومنظم للعملاء حسب المناطق
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
                report += "  ← _لا يوجد عملاء مسجلين حالياً_\n"
            report += "---------------------\n"
            
        bot.edit_message_text(report, ADMIN_ID, call.message.message_id, parse_mode="Markdown")
        
    elif action == "admin_change_trial":
        # أزرار التعديل الفوري والديناميكي للوقت (تظهر فوراً في الإعدادات والتعريف)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("⏱️ نصف ساعة", callback_data="set_time_30m"),
            types.InlineKeyboardButton("⏳ 3 ساعات", callback_data="set_time_3h"),
            types.InlineKeyboardButton("📅 3 أيام", callback_data="set_time_3d"),
            types.InlineKeyboardButton("📅 7 أيام", callback_data="set_time_7d")
        )
        bot.edit_message_text("⏱️ *اختر مدة الفترة المجانية الافتراضية الجديدة للعملاء الجدد:*", ADMIN_ID, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif action == "admin_activate_user":
        msg = bot.send_message(ADMIN_ID, "✍️ يرجى إرسال (ID المعرف) الخاص بالعميل لتفعيله فوراً وفك قفل النظام عنه:")
        bot.register_next_step_handler(msg, process_manual_activation)

# معالجة تغيير الوقت ديناميكياً
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
        
    bot.edit_message_text(f"✅ تم تعديل النظام بالكامل! الفترة المجانية الافتراضية المعتمدة الآن هي: *{SYSTEM_CONFIG['trial_duration_text']}* وتظهر تلقائياً في واجهات الترحيب لجميع المشتركين الجدد.", ADMIN_ID, call.message.message_id, parse_mode="Markdown")

def process_manual_activation(message):
    try:
        target_id = int(message.text)
        if target_id in USERS_DB:
            # الحل الجذري لمشكلة البقاء مقفلاً:
            USERS_DB[target_id]['is_active'] = True  # رفع علم التفعيل مباشرة
            USERS_DB[target_id]['status'] = 'active'
            
            # إرسال فاتورة آرامكي الفخمة للآدمن وللعميل لتأكيد قوة واحترافية الشركة
            shop_name = USERS_DB[target_id].get('shop_name', 'محل الذهب')
            aramky_inv = generate_aramky_invoice(target_id, shop_name, "الباقة الماسية المدعومة", "سنوي / دائم")
            
            bot.send_message(ADMIN_ID, f"✅ تم تفعيل العميل بنجاح!\n\n{aramky_inv}", parse_mode="Markdown")
            
            # إشعار وفاتورة فك القفل للعميل نفسه
            bot.send_message(target_id, f"🔓 *تهانينا! تم قبول اشتراكك وفك قفل النظام بنجاح تام.*\n\n{aramky_inv}", parse_mode="Markdown")
        else:
            bot.send_message(ADMIN_ID, "❌ عذراً، هذا المعرف غير مسجل في النظام حالياً. تأكد من الرقم.")
    except ValueError:
        bot.send_message(ADMIN_ID, "❌ يرجى إرسال أرقام صحيحة فقط للمعرف.")

# تشغيل البوت المستمر مع خاصية حماية الاتصال عند تذبذب النت في العراق
if __name__ == "__main__":
    print("🚀 GoldenCalc_Bot is running elegantly...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
