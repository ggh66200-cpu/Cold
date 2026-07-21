import os
from datetime import datetime
import telebot
from telebot import types
import utils

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID")) # معرّفك المأخوذ من سيرفر ريندر

bot = telebot.TeleBot(BOT_TOKEN)

# ================= فلاتر الحماية ومنع التكرار =================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    
    # منع التكرار الفوري والتعليق
    if utils.is_action_locked(user_id, delay=3):
        return 

    # إرسال إشعار فوري سريع لإشغال العميل وطمأنته
    loading_msg = bot.send_message(message.chat.id, "⏳ جاري تحميل الناتج والتحقق من الحساب...")

    goldsmith = utils.get_goldsmith(user_id)
    
    if not goldsmith:
        # كود التسجيل الجديد (حفظ اللغات، الاسم، المنطقة)
        # الافتراضي يضاف للفترة المحددة بالنظام
        bot.delete_message(message.chat.id, loading_msg.message_id)
        bot.send_message(message.chat.id, "مرحباً بك في منظومة نواة الذهب. يرجى إرسال بيانات المحل للتفعيل...")
        return

    # التحقق من صلاحية الحساب
    bot.delete_message(message.chat.id, loading_msg.message_id)
    
    if not goldsmith['is_active']:
        bot.send_message(message.chat.id, "❌ حسابك غير مفعّل حالياً. يرجى التواصل مع الإدارة.")
        return

    # توجيه للقائمة الرئيسية (حسب اللغة المخزنة)
    bot.send_message(message.chat.id, f"أهلاً بك يا شيخ الكار في محلك: {goldsmith['full_name']}")

# ================= لوحة تحكم الإدارة (ADMIN PANEL) =================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
        
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🟢 تفعيل / 🔴 إلغاء عميل", callback_data="admin_toggle_user"),
        types.InlineKeyboardButton("⏱️ تغيير وقت الفترة المجانية العامة", callback_data="admin_change_global_trial"),
        types.InlineKeyboardButton("👤 تعديل وقت صلاحية عميل محدد", callback_data="admin_change_user_trial")
    )
    bot.send_message(message.chat.id, "👑 أهلاً بك في لوحة تحكم إدارة منظومة نواة الذهب:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def handle_admin_callbacks(call):
    if call.from_user.id != ADMIN_ID: return

    if call.data == "admin_toggle_user":
        msg = bot.send_message(call.message.chat.id, "أرسل (ID العميل) المُراد تفعيله أو إلغاء تفعيله:")
        bot.register_next_step_handler(msg, process_toggle_user)
        
    elif call.data == "admin_change_global_trial":
        current_days = utils.get_default_trial_days()
        msg = bot.send_message(call.message.chat.id, f"الفترة المجانية الحالية هي {current_days} أيام.\nأدخل العدد الجديد للأيام لتغيير رسالة الترحيب تلقائياً:")
        bot.register_next_step_handler(msg, process_global_trial)
        
    elif call.data == "admin_change_user_trial":
        msg = bot.send_message(call.message.chat.id, "أرسل البيانات بالصيغة التالية:\n(ID العميل:عدد الأيام الجديد)\nمثال: 12345678:30")
        bot.register_next_step_handler(msg, process_user_trial)

def process_toggle_user(message):
    try:
        target_id = int(message.text.strip())
        user = utils.get_goldsmith(target_id)
        if user:
            new_status = not user['is_active']
            utils.update_goldsmith_status(target_id, new_status)
            status_text = "🟢 تم التفعيل بنجاح" if new_status else "🔴 تم إلغاء التفعيل بنجاح"
            bot.send_message(message.chat.id, f"الصائغ: {user['full_name']}\nالحالة الجديدة: {status_text}")
        else:
            bot.send_message(message.chat.id, "❌ لم يتم العثور على هذا العميل.")
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ خطأ في الإدخال. تأكد من إرسال أرقام فقط.")

def process_global_trial(message):
    try:
        days = int(message.text.strip())
        utils.set_default_trial_days(days)
        bot.send_message(message.chat.id, f"✅ تم تحديث الفترة المجانية الافتراضية إلى {days} أيام. ستتغير الرسائل الترحيبية تلقائياً للعملاء الجدد!")
    except:
        bot.send_message(message.chat.id, "⚠️ يرجى إدخال عدد أيام صحيح.")

def process_user_trial(message):
    try:
        target_id, days = map(int, message.text.strip().split(":"))
        user = utils.get_goldsmith(target_id)
        if user:
            utils.update_trial_duration(target_id, days)
            bot.send_message(message.chat.id, f"✅ تم تعديل صلاحية الصائغ ({user['full_name']}) بنجاح لتنتهي بعد {days} يوماً من الآن.")
        else:
            bot.send_message(message.chat.id, "❌ العميل غير موجود.")
    except:
        bot.send_message(message.chat.id, "⚠️ صيغة خاطئة. يرجى الالتزام بـ ID:الأيام")

if __name__ == "__main__":
    bot.infinity_polling()
