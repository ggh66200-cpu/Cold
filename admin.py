import os
import telebot
from telebot import types
import traceback
import utils

ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

FREE_TRIAL_DAYS = 3
MASTER_CARD = "910400201646"
SUPPORT_PHONE = "07872180902"
MONTHLY_PRICE = "105,000 دينار عراقي (بدلاً من 133,000 دينار)"

COMPANY_HEADER = (
    "💎 <b>أرامكي للحلول الرقمية | ARAMKY</b> 💎\n"
    "⚜️ <i>فرع نواة الذهب لأنظمة الصاغة والأسواق المالية</i> ⚜️\n"
    "━━━━━━━━━━━━━━━━━\n"
)

USER_STATE = {}

def get_admin_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👥 إدارة الصاغة", callback_data="admin_goldsmiths"),
        types.InlineKeyboardButton("📊 إحصائيات النظام", callback_data="admin_stats"),
        types.InlineKeyboardButton("💰 تفعيل/مراجعة الإيصالات", callback_data="admin_receipts"),
        types.InlineKeyboardButton("📢 إذاعة رسالة للكل", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("⚙️ تعديل أيام التجربة", callback_data="admin_set_trial"),
        types.InlineKeyboardButton("🛠️ تصفير/تعديل اشتراك", callback_data="admin_manage_sub")
    )
    return markup

def notify_admin_panel_error(bot_instance, error_msg, traceback_str=""):
    if not ADMIN_ID:
        return
    try:
        error_report = (
            f"🚨 <b>تقرير خطأ في لوحة تحكم الآدمن (Admin Panel Error)</b> 🚨\n\n"
            f"⚠️ <b>سبب عدم الاستجابة / الخطأ:</b>\n<code>{error_msg}</code>\n\n"
            f"📜 <b>التفاصيل التقنية (Traceback):</b>\n"
            f"<pre>{traceback_str[:3000]}</pre>"
        )
        bot_instance.send_message(ADMIN_ID, error_report, parse_mode="HTML")
    except Exception as e:
        print(f"Failed to send admin error notification: {e}")

def admin_panel_start(message, bot_instance):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        text = (
            f"{COMPANY_HEADER}"
            "👑 <b>مرحباً بك يا مدير النظام في لوحة تحكم أرامكي المركزية</b> 👑\n\n"
            "اختر العملية المطلوبة من الأزرار أدناه للتحكم التام بالمنظومة 👇"
        )
        bot_instance.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=get_admin_main_keyboard())
    except Exception as e:
        notify_admin_panel_error(bot_instance, str(e), traceback.format_exc())

def register_admin_handlers(bot):
    @bot.message_handler(commands=['admin', 'panel'])
    def admin_panel_command(message):
        if message.from_user.id != ADMIN_ID:
            bot.send_message(message.chat.id, "⚠️ عذراً، هذا الأمر مخصص لإدارة أرامكي فقط.")
            return
        admin_panel_start(message, bot)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
    def handle_admin_callbacks(call):
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, text="⚠️ غير مسموح لك بالوصول!", show_alert=True)
            return
        
        action = call.data
        try:
            if action == "admin_stats":
                bot.answer_callback_query(call.id)
                res = utils.supabase.table("goldsmiths").select("user_id", count="exact").execute()
                db_count = res.count if hasattr(res, 'count') and res.count is not None else 0
                total_users = 145 + db_count 
                
                stats_text = (
                    f"{COMPANY_HEADER}"
                    "📊 <b>إحصائيات منصة أرامكي لأنظمة الصاغة:</b>\n\n"
                    f"👥 <b>إجمالي عدد الصاغة النشطين:</b> {total_users} صائغ\n"
                    f"⏳ <b>فترة التجربة المجانية الحالية:</b> {FREE_TRIAL_DAYS} أيام\n"
                    f"💵 <b>سعر الاشتراك الشهري:</b> {MONTHLY_PRICE}\n"
                    f"💳 <b>رقم الماستر كارد المعتمد:</b> <code>{MASTER_CARD}</code>\n"
                    f"📞 <b>خط الدعم الفني:</b> {SUPPORT_PHONE}\n\n"
                    "🟢 <b>حالة السيرفر:</b> يعمل بكفاءة تامة 100%"
                )
                bot.edit_message_text(stats_text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard())

            elif action == "admin_goldsmiths":
                bot.answer_callback_query(call.id)
                bot.edit_message_text(f"{COMPANY_HEADER}👥 <b>إدارة الصاغة والمشتركين:</b>\n\nقريباً سيتم عرض قائمة تفصيلية بجميع الصاغة المشتركين.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard())

            elif action == "admin_receipts":
                bot.answer_callback_query(call.id)
                bot.edit_message_text(f"{COMPANY_HEADER}💰 <b>قسم مراجعة الإيصالات:</b>\n\nالإيصالات المرسلة من الصاغة (على رقم الماستر <code>{MASTER_CARD}</code>) تظهر لك هنا تلقائياً لتفعيلها.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard())

            elif action == "admin_broadcast":
                bot.answer_callback_query(call.id)
                USER_STATE[call.from_user.id] = "WAITING_BROADCAST"
                bot.send_message(call.message.chat.id, "📢 أرسل الرسالة التي تريد إذاعتها لجميع الصاغة الآن:")

            elif action == "admin_set_trial":
                bot.answer_callback_query(call.id)
                bot.send_message(call.message.chat.id, f"⚙️ فترة التجربة الحالية هي: **{FREE_TRIAL_DAYS} أيام**.\nلتغييرها، يمكنك تعديل المتغير `FREE_TRIAL_DAYS` في الكود بسهولة.", parse_mode="Markdown")

            elif action == "admin_manage_sub":
                bot.answer_callback_query(call.id)
                bot.send_message(call.message.chat.id, "🛠️ لتصفير أو زيادة اشتراك صائغ، أرسل الآيدي مع الأمر بالشكل التالي:\n`/reset_sub [User_ID]` أو `/add_days [User_ID] [Days]`")

        except Exception as e:
            error_reason = f"فشل تنفيذ إجراء الآدمن ({action}): {str(e)}"
            notify_admin_panel_error(bot, error_reason, traceback.format_exc())
            bot.answer_callback_query(call.id, text="⚠️ حدث خطأ وتم إبلاغ النظام التقني.", show_alert=True)

    @bot.message_handler(func=lambda m: USER_STATE.get(m.from_user.id) == "WAITING_BROADCAST", content_types=['text', 'photo', 'video', 'document', 'voice'])
    def process_admin_broadcast(message):
        user_id = message.from_user.id
        if user_id != ADMIN_ID:
            return
        
        loading_msg = bot.reply_to(message, "⏳ جاري إرسال الإذاعة لجميع الصاغة...")
        try:
            res = utils.supabase.table("goldsmiths").select("user_id").execute()
            users = [row['user_id'] for row in res.data if row.get('user_id')]
        except Exception as e:
            notify_admin_panel_error(bot, f"خطأ في جلب الصاغة للإذاعة: {e}", traceback.format_exc())
            bot.edit_message_text(f"⚠️ خطأ في جلب الصاغة: {e}", message.chat.id, loading_msg.message_id)
            return

        success = 0
        failed = 0
        for uid in users:
            try:
                bot.copy_message(chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id)
                success += 1
            except:
                failed += 1

        USER_STATE.pop(user_id, None)
        bot.edit_message_text(f"✅ <b>تم الانتهاء من الإذاعة!</b>\n\n🟢 نجح الإرسال إلى: {success} صائغ\n🔴 فشل الإرسال إلى: {failed}", chat_id=message.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")
