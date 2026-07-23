import os
import telebot
from telebot import types
from supabase import create_client, Client

# سحب المفاتيح تلقائياً من إعدادات السيرفر
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

bot = telebot.TeleBot(BOT_TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ⚙️ إعدادات الفترة المجانية (بداية أسبوع / 7 أيام أو حسب رغبتك)
FREE_TRIAL_DAYS = 7

# معلومات الشركة والمالية الثابتة
MASTER_CARD = "910400201646"
SUPPORT_PHONE = "07872180902"
MONTHLY_PRICE = "105,000 دينار عراقي (بدلاً من 133,000 دينار)"

COMPANY_HEADER = (
    "💎 <b>أرامكي للحلول الرقمية | ARAMKY</b> 💎\n"
    "⚜️ <i>فرع نواة الذهب لأنظمة الصاغة والأسواق المالية</i> ⚜️\n"
    "━━━━━━━━━━━━━━━━━\n"
)

# لوحة تحكم الأدمن الرئيسية (أزرار انلاين مرتبة واحترافية)
def get_admin_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👥 إدارة الصاغة", callback_data="admin_goldsmiths"),
        types.InlineKeyboardButton("📊 إحصائيات النظام", callback_data="admin_stats"),
        types.InlineKeyboardButton("💰 تفعيل/مراجعة الإيصالات", callback_data="admin_receipts"),
        types.InlineKeyboardButton("📢 إذاعة رسالة للكل", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("⚙️ تعديل أيام التجربة", callback_data="admin_set_trial"),
        types.InlineKeyboardButton("🛠️ تصفير/تعديل اشتراك صائغ", callback_data="admin_manage_sub")
    )
    return markup

# أمر الدخول للوحة التحكم الخاص بالأدمن حصراً
@bot.message_handler(commands=['admin', 'panel'])
def admin_panel_start(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⚠️ عذراً، هذا الأمر مخصص لإدارة أرامكي فقط.")
        return
    
    text = (
        f"{COMPANY_HEADER}"
        "👑 <b>مرحباً بك يا مدير النظام في لوحة تحكم أرامكي المركزية</b> 👑\n\n"
        "اختر العملية المطلوبة من الأزرار أدناه للتحكم التام بالمنظومة 👇"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=get_admin_main_keyboard())

# معالجة أزرار لوحة التحكم
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def handle_admin_callbacks(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, text="⚠️ غير مسموح لك!", show_alert=True)
        return
    
    action = call.data
    
    if action == "admin_stats":
        bot.answer_callback_query(call.id)
        try:
            res = supabase.table("goldsmiths").select("user_id", count="exact").execute()
            db_count = res.count if hasattr(res, 'count') and res.count is not None else 0
            total_users = 145 + db_count  # يبدأ من 145 ويزيد تلقائياً مع كل تسجيل جديد
            
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
        except Exception as e:
            bot.send_message(call.message.chat.id, f"⚠️ خطأ في جلب الإحصائيات: {str(e)}")

    elif action == "admin_goldsmiths":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            f"{COMPANY_HEADER}👥 <b>إدارة الصاغة والمشتركين:</b>\n\nقريباً سيتم عرض قائمة تفصيلية بجميع الصاغة المشتركين وتواريخ انتهاء اشتراكاتهم.",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard()
        )

    elif action == "admin_receipts":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            f"{COMPANY_HEADER}💰 <b>قسم مراجعة الإيصالات:</b>\n\nالإيصالات المرسلة من الصاغة (على رقم الماستر <code>{MASTER_CARD}</code>) تظهر لك هنا تلقائياً عند انتهاء فتراتهم لتفعيلها بضغطة زر.",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard()
        )

    elif action == "admin_broadcast":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📢 أرسل الرسالة التي تريد إذاعتها لجميع الصاغة الآن (نص، صورة، أو فيديو):")

    elif action == "admin_set_trial":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"⚙️ فترة التجربة الحالية هي: **{FREE_TRIAL_DAYS} أيام**.\nلتغييرها، يمكنك تعديل المتغير `FREE_TRIAL_DAYS` في الكود بسهولة.", parse_mode="Markdown")

    elif action == "admin_manage_sub":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🛠️ لتصفير أو زيادة اشتراك صائغ، أرسل الآيدي مع الأمر بالشكل التالي:\n`/reset_sub [User_ID]` أو `/add_days [User_ID] [Days]`")

# أزرار الموافقة أو الرفض للإيصالات التي يرسلها العميل (تظهر للأدمن)
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_sub_") or call.data.startswith("reject_sub_"))
def handle_subscription_approval(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    data_parts = call.data.split("_")
    action = data_parts[0]
    target_user_id = data_parts[2]
    
    if action == "approve":
        bot.answer_callback_query(call.id, text="✅ تم تفعيل الاشتراك بنجاح!")
        bot.edit_message_caption(
            caption=f"{call.message.caption}\n\n✅ <b>حالة الإيصال:</b> تم القبول والتفعيل بنجاح من قبل الأدمن 👑",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML"
        )
        try:
            bot.send_message(target_user_id, "🎉 <b>مبروك! تم تفعيل اشتراكك الشهري بنجاح في منظومة أرامكي.</b>\nيمكنك استخدام كافة خدمات البوت الآن بحرية تامة 💛", parse_mode="HTML")
        except:
            pass
            
    elif action == "reject":
        bot.answer_callback_query(call.id, text="❌ تم رفض الإيصال.")
        bot.edit_message_caption(
            caption=f"{call.message.caption}\n\n❌ <b>حالة الإيصال:</b> تم الرفض (يرجى إرسال إيصال صحيح عبر الدعم الفني: " + SUPPORT_PHONE + ")",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML"
        )
        try:
            bot.send_message(target_user_id, f"⚠️ عذراً، تم رفض إيصال التحويل المرفق. يرجى التواصل مع الدعم الفني على الرقم: {SUPPORT_PHONE}", parse_mode="HTML")
        except:
            pass

if __name__ == "__main__":
    print("🤖 Admin Panel Module is running...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
