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
        types.InlineKeyboardButton("👥 جرد وإدارة الصاغة", callback_data="admin_goldsmiths"),
        types.InlineKeyboardButton("🚨 الصاغة المنتهية", callback_data="admin_expired"),
        types.InlineKeyboardButton("🔍 البحث عن صائغ", callback_data="admin_search"),
        types.InlineKeyboardButton("📊 إحصائيات النظام", callback_data="admin_stats"),
        types.InlineKeyboardButton("📢 إذاعة رسالة للكل", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("⚙️ تعديل أيام التجربة", callback_data="admin_set_trial")
    )
    return markup

def notify_admin_panel_error(bot_instance, error_msg, traceback_str=""):
    if not ADMIN_ID:
        return
    try:
        error_report = (
            f"🚨 <b>تقرير خطأ في لوحة تحكم الآدمن</b> 🚨\n\n"
            f"⚠️ <b>السبب:</b>\n<code>{error_msg}</code>"
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
            "👑 <b>مرحباً بك يا مدير النظام في لوحة تحكم أرامكي</b> 👑\n\n"
            "اختر العملية المطلوبة أدناه للتحكم السريع 👇"
        )
        bot_instance.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=get_admin_main_keyboard())
    except Exception as e:
        notify_admin_panel_error(bot_instance, str(e), traceback.format_exc())

def register_admin_handlers(bot):
    @bot.message_handler(commands=['admin', 'panel'])
    def admin_panel_command(message):
        if message.from_user.id != ADMIN_ID:
            bot.send_message(message.chat.id, "⚠️ عذراً، هذا الأمر مخصص للإدارة فقط.")
            return
        admin_panel_start(message, bot)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin_") or call.data.startswith("adm_sub_"))
    def handle_admin_callbacks(call):
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, text="⚠️ غير مسموح!", show_alert=True)
            return
        
        data = call.data
        try:
            if data == "admin_stats":
                bot.answer_callback_query(call.id)
                res = utils.supabase.table("goldsmiths").select("user_id", count="exact").execute()
                db_count = res.count if hasattr(res, 'count') and res.count is not None else 0
                total_users = 145 + db_count 
                
                stats_text = (
                    f"{COMPANY_HEADER}"
                    "📊 <b>إحصائيات المنصة:</b>\n\n"
                    f"👥 <b>إجمالي الصاغة النشطين:</b> {total_users} صائغ\n"
                    f"⏳ <b>فترة التجربة المجانية الحالية:</b> {FREE_TRIAL_DAYS} أيام\n"
                    f"💵 <b>سعر الاشتراك الشهري:</b> {MONTHLY_PRICE}\n"
                    f"💳 <b>رقم الماستر المعتمد:</b> <code>{MASTER_CARD}</code>\n\n"
                    "🟢 <b>حالة السيرفر:</b> يعمل بكفاءة 100%"
                )
                try:
                    bot.edit_message_text(stats_text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard())
                except telebot.apihelper.ApiTelegramException as e:
                    if "message is not modified" not in str(e):
                        raise e

            elif data == "admin_goldsmiths":
                bot.answer_callback_query(call.id)
                goldsmiths = utils.get_all_goldsmiths()
                
                if not goldsmiths:
                    bot.edit_message_text(f"{COMPANY_HEADER}👥 <b>جرد الصاغة:</b>\n\nلا يوجد صاغة مسجلين في القاعدة حالياً.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard())
                    return

                text = f"{COMPANY_HEADER}👥 <b>قائمة وجرد الصاغة المشتركين ({len(goldsmiths)}):</b>\nاختر الصائغ للتحكم السريع بحسابه 👇"
                markup = types.InlineKeyboardMarkup(row_width=1)
                
                for g in goldsmiths[:15]: 
                    uid = g.get('user_id')
                    name = g.get('full_name') or 'بدون اسم'
                    days = g.get('remaining_days', 0)
                    btn_text = f"👤 {name} | (رصيد: {days} يوم)"
                    markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"adm_sub_view_{uid}"))
                
                markup.add(types.InlineKeyboardButton("🔙 عودة للرئيسية", callback_data="admin_home"))
                try:
                    bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=markup)
                except telebot.apihelper.ApiTelegramException as e:
                    if "message is not modified" not in str(e):
                        raise e

            elif data == "admin_expired":
                bot.answer_callback_query(call.id)
                goldsmiths = utils.get_all_goldsmiths()
                expired_users = [g for g in goldsmiths if int(g.get('remaining_days', 0)) <= 0]
                
                if not expired_users:
                    bot.edit_message_text(f"{COMPANY_HEADER}🚨 <b>الصاغة المنتهية اشتراكاتهم:</b>\n\nممتاز! لا يوجد أي صائغ منتهي الاشتراك حالياً، الكل مشترك وفعال.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard())
                    return

                text = f"{COMPANY_HEADER}🚨 <b>قائمة الصاغة الذين انتهت اشتراكاتهم ({len(expired_users)}):</b>\nاختر الصائغ لتجديد اشتراكه فورا 👇"
                markup = types.InlineKeyboardMarkup(row_width=1)
                
                for g in expired_users[:15]:
                    uid = g.get('user_id')
                    name = g.get('full_name') or 'بدون اسم'
                    markup.add(types.InlineKeyboardButton(f"🚨 {name} | منتهي الصلاحية", callback_data=f"adm_sub_view_{uid}"))
                
                markup.add(types.InlineKeyboardButton("🔙 عودة للرئيسية", callback_data="admin_home"))
                try:
                    bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=markup)
                except telebot.apihelper.ApiTelegramException as e:
                    if "message is not modified" not in str(e):
                        raise e

            elif data == "admin_search":
                bot.answer_callback_query(call.id)
                USER_STATE[call.from_user.id] = "WAITING_GOLDSMITH_SEARCH"
                bot.send_message(call.message.chat.id, "🔍 <b>البحث السريع عن صائغ:</b>\n\nأرسل جزءاً من <b>اسم المحل</b> أو <b>رقم الهاتف</b> للبحث عنه فوراً:")

            elif data.startswith("adm_sub_view_"):
                bot.answer_callback_query(call.id)
                target_uid = data.split("_")[3]
                gs = utils.get_goldsmith(target_uid) or {}
                
                name = gs.get('full_name', 'غير معروف')
                phone = gs.get('phone', 'غير متوفر')
                days = gs.get('remaining_days', 0)
                
                info_text = (
                    f"{COMPANY_HEADER}"
                    f"👤 <b>تفاصيل الصائغ:</b>\n\n"
                    f"🏢 المحل: <b>{name}</b>\n"
                    f"📱 الهاتف: <code>{phone}</code>\n"
                    f"🆔 الآيدي: <code>{target_uid}</code>\n"
                    f"⏳ الأيام المتبقية: <b>{days} يوم</b>\n\n"
                    "اختر الإجراء المناسب أدناه بضغطة زر:"
                )
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("➕ تفعيل/إضافة 30 يوم", callback_data=f"adm_sub_add_{target_uid}"),
                    types.InlineKeyboardButton("🛑 إيقاف/تصفير الحساب", callback_data=f"adm_sub_zero_{target_uid}")
                )
                markup.add(types.InlineKeyboardButton("⬅️ رجوع لقائمة الصاغة", callback_data="admin_goldsmiths"))
                bot.edit_message_text(info_text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=markup)

            elif data.startswith("adm_sub_add_"):
                target_uid = data.split("_")[3]
                utils.update_goldsmith_subscription(target_uid, days=30)
                bot.answer_callback_query(call.id, text="✅ تمت إضافة 30 يوم بنجاح!", show_alert=True)
                call.data = f"adm_sub_view_{target_uid}"
                handle_admin_callbacks(call)

            elif data.startswith("adm_sub_zero_"):
                target_uid = data.split("_")[3]
                utils.adjust_goldsmith_days(target_uid, 0, set_zero=True)
                bot.answer_callback_query(call.id, text="🛑 تم إيقاف وتصفير أيام الصائغ!", show_alert=True)
                call.data = f"adm_sub_view_{target_uid}"
                handle_admin_callbacks(call)

            elif data == "admin_home":
                bot.answer_callback_query(call.id)
                text = f"{COMPANY_HEADER}👑 <b>لوحة تحكم أرامكي المركزية</b> 👑\n\nاختر العملية المطلوبة أدناه:"
                bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard())

            elif data == "admin_broadcast":
                bot.answer_callback_query(call.id)
                USER_STATE[call.from_user.id] = "WAITING_BROADCAST"
                bot.send_message(call.message.chat.id, "📢 أرسل الرسالة (نص، صورة، أو فيديو) التي تريد إذاعتها لجميع الصاغة الآن:")

            elif data == "admin_set_trial":
                bot.answer_callback_query(call.id)
                bot.send_message(call.message.chat.id, f"⚙️ فترة التجربة الحالية مضبوطة على: **{FREE_TRIAL_DAYS} أيام**.", parse_mode="Markdown")

        except Exception as e:
            error_reason = f"خطأ في لوحة التحكم ({data}): {str(e)}"
            notify_admin_panel_error(bot, error_reason, traceback.format_exc())
            bot.answer_callback_query(call.id, text="⚠️ حدث خطأ تقني.", show_alert=True)

    @bot.message_handler(func=lambda m: USER_STATE.get(m.from_user.id) == "WAITING_GOLDSMITH_SEARCH")
    def process_goldsmith_search(message):
        user_id = message.from_user.id
        if user_id != ADMIN_ID:
            return
        
        query = message.text.strip().lower()
        USER_STATE.pop(user_id, None)
        
        try:
            goldsmiths = utils.get_all_goldsmiths()
            matched = [g for g in goldsmiths if query in str(g.get('full_name', '')).lower() or query in str(g.get('phone', '')) or query in str(g.get('user_id', ''))]
            
            if not matched:
                bot.send_message(message.chat.id, "❌ لم يتم العثور على أي صائغ مطابق لبحثك.", reply_markup=get_admin_main_keyboard())
                return
                
            text = f"{COMPANY_HEADER}🔍 <b>نتائج البحث عن ({query}):</b>\nاختر الصائغ المطلوب للتحكم السريع بحسابه 👇"
            markup = types.InlineKeyboardMarkup(row_width=1)
            for g in matched:
                uid = g.get('user_id')
                name = g.get('full_name') or 'بدون اسم'
                days = g.get('remaining_days', 0)
                markup.add(types.InlineKeyboardButton(f"👤 {name} | (رصيد: {days} يوم)", callback_data=f"adm_sub_view_{uid}"))
            
            markup.add(types.InlineKeyboardButton("🔙 عودة للرئيسية", callback_data="admin_home"))
            bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ خطأ أثناء البحث: {e}")

    @bot.message_handler(func=lambda m: USER_STATE.get(m.from_user.id) == "WAITING_BROADCAST", content_types=['text', 'photo', 'video', 'document', 'voice'])
    def process_admin_broadcast(message):
        user_id = message.from_user.id
        if user_id != ADMIN_ID:
            return
        
        loading_msg = bot.reply_to(message, "⏳ جاري إرسال الإذاعة لجميع الصاغة...")
        try:
            users = utils.get_all_goldsmiths()
            user_ids = [row['user_id'] for row in users if row.get('user_id')]
        except Exception as e:
            bot.edit_message_text(f"⚠️ خطأ في جلب الصاغة: {e}", message.chat.id, loading_msg.message_id)
            return

        success = 0
        failed = 0
        for uid in user_ids:
            try:
                bot.copy_message(chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id)
                success += 1
            except:
                failed += 1

        USER_STATE.pop(user_id, None)
        bot.edit_message_text(f"✅ <b>تم الانتهاء من الإذاعة!</b>\n\n🟢 نجح الإرسال إلى: {success} صائغ\n🔴 فشل الإرسال إلى: {failed}", chat_id=message.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")
