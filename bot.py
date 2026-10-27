import os
import re
import time
import threading
import urllib.request
import traceback
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import telebot
from telebot import types
from flask import Flask
import utils
import admin

BOT_TOKEN = os.environ.get("BOT_TOKEN")

try:
    ADMIN_ID = int(os.environ.get("ADMIN_ID", getattr(admin, "ADMIN_ID", 0)))
except Exception:
    ADMIN_ID = 0

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "SMART GOLD SYSTEM IS LIVE 24/7"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive_ping():
    port = os.environ.get("PORT", 10000)
    url = f"http://127.0.0.1:{port}/"
    while True:
        try:
            time.sleep(300)
            urllib.request.urlopen(url)
        except Exception as e:
            print(f"Keep-alive ping status: {e}")

MASTER_CARD = admin.MASTER_CARD
MONTHLY_PRICE = admin.MONTHLY_PRICE
COMPANY_HEADER = getattr(admin, "COMPANY_HEADER", "⚜️ <b>ARAMKY | SMART GOLD SYSTEM</b> ⚜️\n")
SUPPORT_NUMBER = "07766083622" 

USER_STATE = {}

def fmt(value):
    try:
        if value is None:
            return "0"
        d = Decimal(str(value))
        if d == d.to_integral_value():
            return f"{int(d):,}"
        else:
            s = str(value).strip()
            if '.' in s:
                parts = s.split('.')
                dec_clean = parts[1].rstrip('0')
                if not dec_clean:
                    return f"{int(parts[0]):,}"
                return f"{int(parts[0]):,}.{dec_clean}"
            return f"{d:,.2f}"
    except Exception:
        return str(value)

TEXTS = {
    "welcome": "👋 أهلاً بك في منصة <b>SMART GOLD SYSTEM</b>\n\nالمنظومة الذكية الأسرع والأدق لإدارة حسابات الذهب بدقة الحاسبة المكتبية المباشرة.\n🔑 <i>رقم العضوية:</i> <b>#{serial} صايغ معتمد</b>\n\nاختر العملية المطلوبة من الأزرار المثبتة أدناه للبدء فوراً 👇",
    "btn_sell": "🛍️ بيع للزبون",
    "btn_buy": "📥 شراء من الزبون",
    "btn_dollar": "💵 سعر الدولار والتعديل",
    "btn_info": "📖 معلومات النظام",
    "btn_rate": "⭐ تقييم المنظومة",
    "btn_ref": "🎁 دعوة صايغ (أسبوع مجاني)",
    "footer": "نظام آراُمكي - دقة وأمان لحساباتك اليومية"
}

def notify_admin_error(user_id, error_msg, traceback_str=""):
    if not ADMIN_ID:
        return
    try:
        error_report = (
            f"🚨 <b>تقرير خطأ (Exception Alert)</b> 🚨\n\n"
            f"👤 <b>معرف المستخدم:</b> <code>{user_id}</code>\n"
            f"⚠️ <b>السبب:</b>\n<code>{error_msg}</code>\n\n"
            f"📜 <b>التفاصيل:</b>\n<pre>{traceback_str[:3000]}</pre>"
        )
        bot.send_message(ADMIN_ID, error_report, parse_mode="HTML")
    except Exception as e:
        print(f"Failed to send error notification to admin: {e}")

def to_english_numbers(text):
    if not text:
        return ""
    arabic_nums = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    persian_nums = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    return text.translate(arabic_nums).translate(persian_nums)

def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton(TEXTS["btn_sell"]), types.KeyboardButton(TEXTS["btn_buy"]))
    markup.add(types.KeyboardButton(TEXTS["btn_dollar"]), types.KeyboardButton(TEXTS["btn_info"]))
    markup.add(types.KeyboardButton(TEXTS["btn_rate"]), types.KeyboardButton(TEXTS["btn_ref"]))
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("🛠️ لوحة تحكم الإدارة (خاص)"))
    return markup

def send_main_menu(message, user_id):
    try:
        markup = get_main_keyboard(user_id)
        serial = 145
        try:
            all_users = utils.get_all_goldsmiths()
            for u in all_users:
                if str(u.get('user_id')) == str(user_id):
                    serial = u.get('member_serial', 145)
                    break
        except Exception:
            pass
        
        bot.send_message(
            message.chat.id, 
            COMPANY_HEADER + "\n" + TEXTS["welcome"].format(serial=serial), 
            parse_mode="HTML", 
            reply_markup=markup
        )
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    try:
        args = message.text.split()
        referrer_id = None
        if len(args) > 1 and args[1].startswith("ref_"):
            try:
                referrer_id = int(args[1].replace("ref_", ""))
            except Exception:
                referrer_id = None

        gs = utils.get_goldsmith(user_id) or {}
        is_admin = (user_id == ADMIN_ID)
        
        if not gs.get('is_registered', False) or not gs.get('full_name'):
            USER_STATE[user_id] = {"state": "WAITING_REGISTRATION_FULL", "referrer": referrer_id}
            bot.send_message(
                message.chat.id, 
                f"{COMPANY_HEADER}\n🌟 <b>مرحباً بك في منظومة ARAMKY الاحترافية!</b> 🌟\n\n"
                "لتفعيل حسابك وتدشين فترتك التجريبية بدقة، أرسل بيانات محلك بالترتيب التالي:\n\n"
                "🏢 <b>اسم المحل:</b> (مثال: مجوهرات الذهب الأخضر)\n"
                "📱 <b>رقم الهاتف:</b> (مثال: 07800000000)\n\n"
                "✍️ <i>أرسل المعلومات في رسالة واحدة:</i>", 
                parse_mode="HTML",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        remaining_days = gs.get('remaining_days', 0)
        if remaining_days <= 0 and not is_admin:
            show_subscription_form(message, expired=True)
            return

        USER_STATE.pop(user_id, None)
        send_main_menu(message, user_id)
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())
@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_ref"])
def show_referral_program(message):
    user_id = message.from_user.id
    try:
        gs = utils.get_goldsmith(user_id) or {}
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
        ref_count = gs.get('referral_count', 0)
        
        ref_text = (
            f"{COMPANY_HEADER}\n"
            "🎁 <b>برنامج إحالة ودعوة الصاغة:</b>\n\n"
            "شارك رابطك الخاص مع زملائك الصاغة، وعند اشتراك أي صايغ ودفعه لاشتراكه الشهري عن طريقك، <b>تكتسب أسبوعاً مجانياً (+7 أيام)</b> يضاف لاشتراكك تلقائياً وبدون حد أقصى!\n\n"
            f"👥 <b>عدد المشتركين المدفوعين عن طريقك:</b> <code>{ref_count} صايغ</code>\n\n"
            f"🔗 <b>رابط الدعوة الخاص بك:</b>\n<code>{ref_link}</code>"
        )
        bot.send_message(message.chat.id, ref_text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_info"])
def show_system_info(message):
    user_id = message.from_user.id
    try:
        gs = utils.get_goldsmith(user_id) or {}
        remaining_days = gs.get('remaining_days', 0)
        info_text = (
            f"{COMPANY_HEADER}\n"
            "📖 <b>تفاصيل النظام ومعلومات الحساب:</b>\n\n"
            f"⏳ الأيام المتبقية للاشتراك: <b>{remaining_days} يوم</b>\n"
            "🔹 نظام حساب حر مباشر (سعر المثقال + الوزن + الأجور)\n"
            "🔹 مطابقة تامة لنتائج الحاسبة المكتبية\n\n"
            f"📞 <b>الدعم الفني والطوارئ:</b>\n<code>{SUPPORT_NUMBER}</code>"
        )
        bot.send_message(message.chat.id, info_text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_rate"])
def rate_system_menu(message):
    user_id = message.from_user.id
    try:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("⭐⭐⭐⭐⭐ ممتاز جداً (5 نجوم)", callback_data="rate_5"),
            types.InlineKeyboardButton("⭐⭐⭐⭐ جيد جداً (4 نجوم)", callback_data="rate_4"),
            types.InlineKeyboardButton("⭐⭐⭐ جيد (3 نجوم)", callback_data="rate_3"),
            types.InlineKeyboardButton("💬 إرسال مقترح / ملاحظة للإدارة", callback_data="rate_feedback")
        )
        text = (
            f"{COMPANY_HEADER}\n"
            "📊 <b>التقييم العام للمنظومة:</b> ⭐⭐⭐⭐⭐ <b>4.9 / 5.0</b>\n"
            "<i>(استناداً إلى تقييمات صاغة العراق المعتمدين)</i>\n\n"
            "يرجى اختيار تقييمك للمنظومة أدناه 👇"
        )
        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.callback_query_handler(func=lambda call: call.data.startswith("rate_"))
def handle_rating_callbacks(call):
    user_id = call.from_user.id
    try:
        data = call.data
        gs = utils.get_goldsmith(user_id) or {}
        shop_name = gs.get('full_name', 'غير محدد')
        phone = gs.get('phone', 'غير محدد')

        if data in ["rate_5", "rate_4", "rate_3"]:
            stars = "5 نجوم" if data == "rate_5" else ("4 نجوم" if data == "rate_4" else "3 نجوم")
            bot.answer_callback_query(call.id, text=f"🌟 شكراً لتقييمك ({stars})!")
            
            if ADMIN_ID:
                report = (
                    f"⭐ <b>تقييم جديد للمنظومة:</b>\n\n"
                    f"🏢 <b>المحل:</b> {shop_name}\n"
                    f"📱 <b>الهاتف:</b> <code>{phone}</code>\n"
                    f"🆔 <b>المعرف:</b> <code>{user_id}</code>\n"
                    f"🌟 <b>التقييم:</b> {stars}"
                )
                bot.send_message(ADMIN_ID, report, parse_mode="HTML")

            bot.send_message(
                call.message.chat.id, 
                f"💛 <b>شكراً لتقييمكم ({stars})!</b>\n\nنحن مستمرون بالتطوير لضمان دقة وسرعة حساباتكم دائماً.",
                parse_mode="HTML",
                reply_markup=get_main_keyboard(user_id)
            )

        elif data == "rate_feedback":
            bot.answer_callback_query(call.id, text="💬 اكتب ملاحظتك...")
            USER_STATE[user_id] = "WAITING_FEEDBACK_TEXT"
            bot.send_message(
                call.message.chat.id, 
                "✍️ <b>اكتب مقترحك أو ملاحظتك هنا وسيقوم فريق الدعم الفني بمراجعتها فوراً:</b>",
                parse_mode="HTML",
                reply_markup=types.ReplyKeyboardRemove()
            )
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

def show_subscription_form(message, expired=False):
    user_id = message.from_user.id
    try:
        USER_STATE[user_id] = "WAITING_RECEIPT"
        prefix = "🚨 <b>انتهت فترتك التجريبية! يرجى التجديد للاستمرار:</b>\n\n" if expired else ""
        sub_text = (
            f"{COMPANY_HEADER}\n{prefix}"
            f"🔹 <b>الاشتراك الشهري:</b> <b>{MONTHLY_PRICE}</b>\n"
            f"🔹 <b>ماستر كارد التحويل:</b> <code>{MASTER_CARD}</code>\n"
            f"📞 <b>الدعم الفني:</b> <code>{SUPPORT_NUMBER}</code>\n\n"
            "📸 أرسل صورة وصل التحويل هنا لتفعيل اشتراكك."
        )
        bot.send_message(message.chat.id, sub_text, parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == "🛠️ لوحة تحكم الإدارة (خاص)")
def admin_panel_shortcut(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        try:
            admin.admin_panel_start(message, bot)
        except Exception as e:
            notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_dollar"])
def dollar_management_menu(message):
    user_id = message.from_user.id
    try:
        current_p = utils.get_goldsmith_prices(user_id) or {}
        usd_rate = Decimal(str(current_p.get('usd_rate', 1530)))
        usd_100_display = usd_rate * Decimal('100') if usd_rate < Decimal('5000') else usd_rate
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔄 تعديل سعر الـ 100$ الآن", callback_data="edit_price_usd"))
        
        text = (
            f"{COMPANY_HEADER}\n"
            f"💵 <b>سعر صرف 100$ الحالي بالدينار:</b>\n\n"
            f"👉 <code>{fmt(usd_100_display)} دينار</code>\n\n"
            "اضغط الزر أدناه لتحديث السعر عند تغير البورصة:"
        )
        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.callback_query_handler(func=lambda call: call.data == "edit_price_usd")
def handle_dollar_edit_callback(call):
    user_id = call.from_user.id
    try:
        bot.answer_callback_query(call.id, text="⏳ أرسل السعر الجديد...")
        USER_STATE[user_id] = "WAITING_SINGLE_PRICE_VALUE"
        bot.send_message(
            call.message.chat.id, 
            "📝 <b>أرسل سعر صرف الـ 100$ الجديد:</b>\n<i>(مثال: 153000)</i>", 
            parse_mode="HTML",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_sell"])
def customer_sell_init(message):
    user_id = message.from_user.id
    try:
        USER_STATE[user_id] = "WAITING_SELL_INPUTS"
        bot.send_message(
            message.chat.id, 
            f"{COMPANY_HEADER}\n🛍️ <b>حساب بيع زبون:</b>\n\n"
            "✍️ أرسل المعطيات في رسالة واحدة (كل قيمة بسطر):\n\n"
            "1️⃣ سعر المثقال\n"
            "2️⃣ الوزن بالغرام\n"
            "3️⃣ أجور صياغة الغرام\n\n"
            "💡 <i>مثال:</i>\n<code>520000\n10.5\n5000</code>", 
            parse_mode="HTML",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_buy"])
def customer_buy_init(message):
    user_id = message.from_user.id
    try:
        USER_STATE[user_id] = "WAITING_BUY_INPUTS"
        bot.send_message(
            message.chat.id, 
            f"{COMPANY_HEADER}\n📥 <b>حساب شراء (كسر) من الزبون:</b>\n\n"
            "✍️ أرسل المعطيات في رسالة واحدة (كل قيمة بسطر):\n\n"
            "1️⃣ سعر شراء المثقال\n"
            "2️⃣ الوزن بالغرام\n"
            "3️⃣ أجور الخصم للغرام\n\n"
            "💡 <i>مثال:</i>\n<code>510000\n15.2\n2000</code>", 
            parse_mode="HTML",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.callback_query_handler(func=lambda call: call.data in ["confirm_invoice", "cancel_invoice"])
def handle_invoice_confirmation(call):
    user_id = call.from_user.id
    try:
        if call.data == "confirm_invoice":
            bot.answer_callback_query(call.id, text="✅ تمت العملية بنجاح!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id, "✅ <b>تم اعتماد الفاتورة بنجاح!</b>", parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
        else:
            bot.answer_callback_query(call.id, text="❌ تم إلغاء العملية")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id, "❌ <b>تم إلغاء الفاتورة.</b>", parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(content_types=['photo'])
def handle_receipt_photo(message):
    user_id = message.from_user.id
    try:
        raw_state = USER_STATE.get(user_id)
        state = raw_state.get("state") if isinstance(raw_state, dict) else raw_state

        gs = utils.get_goldsmith(user_id) or {}
        is_admin = (user_id == ADMIN_ID)
        remaining_days = gs.get('remaining_days', 0)

        if state == "WAITING_RECEIPT" or (remaining_days <= 0 and not is_admin):
            photo_id = message.photo[-1].file_id
            shop_name = gs.get('full_name', 'غير محدد')
            phone = gs.get('phone', 'غير محدد')

            if ADMIN_ID:
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("✅ تفعيل اشتراك (شهر)", callback_data=f"admin_sub_30_{user_id}"),
                    types.InlineKeyboardButton("❌ رفض الوصل", callback_data=f"admin_sub_zero_{user_id}")
                )
                
                caption = (
                    f"🚨 <b>وصول وصل تحويل اشتراك جديد!</b>\n\n"
                    f"🏢 <b>المحل:</b> {shop_name}\n"
                    f"📱 <b>الهاتف:</b> <code>{phone}</code>\n"
                    f"🆔 <b>المعرف:</b> <code>{user_id}</code>"
                )
                bot.send_photo(ADMIN_ID, photo_id, caption=caption, parse_mode="HTML", reply_markup=markup)

            USER_STATE.pop(user_id, None)
            bot.send_message(
                message.chat.id, 
                "✅ <b>تم إرسال وصل التحويل إلى الإدارة بنجاح!</b>\n\n<i>سيتم مراجعته وتفعيل اشتراكك وتحديث رصيد الإحلاّت في أقرب وقت. شكراً لصبرك 💛</i>", 
                parse_mode="HTML", 
                reply_markup=get_main_keyboard(user_id)
            )
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    user_id = message.from_user.id
    try:
        text = to_english_numbers(message.text.strip()) if message.text else ""
        raw_state = USER_STATE.get(user_id)
        
        state = raw_state.get("state") if isinstance(raw_state, dict) else raw_state

        if state == "WAITING_FEEDBACK_TEXT":
            gs = utils.get_goldsmith(user_id) or {}
            shop_name = gs.get('full_name', 'غير محدد')
            phone = gs.get('phone', 'غير محدد')
            
            if ADMIN_ID:
                feedback_report = (
                    f"💬 <b>ملاحظة / مقترح جديد من صايغ:</b>\n\n"
                    f"🏢 <b>المحل:</b> {shop_name}\n"
                    f"📱 <b>الهاتف:</b> <code>{phone}</code>\n"
                    f"🆔 <b>المعرف:</b> <code>{user_id}</code>\n\n"
                    f"✍️ <b>الملاحظة:</b>\n{text}"
                )
                bot.send_message(ADMIN_ID, feedback_report, parse_mode="HTML")
            
            USER_STATE.pop(user_id, None)
            bot.send_message(
                message.chat.id, 
                "✅ <b>تم إرسال ملاحظتك بنجاح إلى فريق الإدارة. شكراً لاهتمامك ببركة المنظومة!</b>", 
                parse_mode="HTML", 
                reply_markup=get_main_keyboard(user_id)
            )
            return

        if state == "WAITING_REGISTRATION_FULL":
            loading = bot.send_message(message.chat.id, "⏳ <i>جاري تأسيس الحساب...</i>", parse_mode="HTML")
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            shop_name = lines[0] if len(lines) >= 1 else text
            phone = lines[1] if len(lines) >= 2 else "غير محدد"
            
            referrer = raw_state.get("referrer") if isinstance(raw_state, dict) else None
            utils.register_goldsmith_details(user_id, shop_name, phone, referrer_id=referrer)

            USER_STATE.pop(user_id, None)
            bot.delete_message(message.chat.id, loading.message_id)
            
            bot.send_message(
                message.chat.id, 
                "💎 <b>تم تسجيل محلك وتفعيل الفترة التجريبية بنجاح!</b>\n\nاختر العملية المطلوبة من الأزرار أدناه للبدء 👇", 
                parse_mode="HTML", 
                reply_markup=get_main_keyboard(user_id)
            )
            return

        if state == "WAITING_SINGLE_PRICE_VALUE":
            loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري تحديث سعر الدولار...</i>", parse_mode="HTML")
            if re.match(r'^\d+(\.\d+)?$', text):
                val = Decimal(text)
                usd_r = (val / Decimal('100') if val > Decimal('5000') else val)
                usd_100_val = usd_r * Decimal('100')
                
                current_p = utils.get_goldsmith_prices(user_id) or {}
                utils.update_morning_prices(
                    user_id,
                    p24=float(current_p.get('price_24', 1020000)),
                    p22=float(current_p.get('price_22', 935000)),
                    p21=float(current_p.get('price_21', 900000)),
                    p18=float(current_p.get('price_18', 450000)),
                    p9=float(current_p.get('price_9', 400000)),
                    w24=float(current_p.get('wage_24', 3000)),
                    w22=float(current_p.get('wage_22', 3500)),
                    w21=float(current_p.get('wage_21', 4500)),
                    w18=float(current_p.get('wage_18', 7500)),
                    w9=float(current_p.get('wage_9', 2500)),
                    usd_r=float(usd_r)
                )
                USER_STATE.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, f"✅ <b>تم تحديث سعر صرف الـ 100$ بنجاح إلى:</b> <code>{fmt(usd_100_val)} دينار</code>", parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
            return

        if state == "WAITING_SELL_INPUTS":
            loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري الحساب...</i>", parse_mode="HTML")
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if len(lines) >= 3:
                mithqal_price = Decimal(lines[0])
                w = Decimal(lines[1])
                wage = Decimal(lines[2])
                
                gram_price = mithqal_price / Decimal('5')
                gram_full = gram_price + wage
                total_iqd = gram_full * w
                
                prices = utils.get_goldsmith_prices(user_id) or {}
                goldsmith = utils.get_goldsmith(user_id) or {}
                
                usd_rate_single = Decimal(str(prices.get('usd_rate', 1530)))
                sheet_price = usd_rate_single * Decimal('100') if usd_rate_single < Decimal('5000') else usd_rate_single
                usd_bills = int(total_iqd // sheet_price) if sheet_price > 0 else 0
                rem_iqd = total_iqd % sheet_price if sheet_price > 0 else total_iqd
                
                shop_name = goldsmith.get('full_name') or 'محلي الموقر'
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("✅ تأكيد العملية", callback_data="confirm_invoice"),
                    types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_invoice")
                )
                
                invoice = (
                    f"{COMPANY_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧾 <b>فاتورة بيع ذهب للزبون</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔷 <b>المحل العامر:</b> {shop_name}\n\n"
                    f"🟡 <b>سعر المثقال المعتمد:</b> {fmt(mithqal_price)} دينار\n"
                    f"⚖️ <b>الوزن الإجمالي:</b> {fmt(w)} غرام\n"
                    f"🔨 <b>أجور صياغة الغرام:</b> {fmt(wage)} دينار\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 <b>سعر الغرام الصافي:</b> {fmt(gram_price)} دينار\n"
                    f"✨ <b>سعر الغرام مع الأجور:</b> {fmt(gram_full)} دينار\n\n"
                    f"💵 <b>إجمالي الحساب بالدينار:</b>\n"
                    f"👉 <b>{fmt(total_iqd)} دينار</b>\n\n"
                    f"💵 <b>صافي الحساب (ورق ودينار):</b>\n"
                    f"👉 <b>{fmt(usd_bills)} ورقة و {fmt(rem_iqd)} دينار</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['footer']}"
                )
                USER_STATE.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                
                bot.send_message(message.chat.id, invoice, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
                bot.send_message(message.chat.id, "📌 <b>يرجى اعتماد أو إلغاء الفاتورة أعلاه:</b>", parse_mode="HTML", reply_markup=markup)
            return

        if state == "WAITING_BUY_INPUTS":
            loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري الحساب...</i>", parse_mode="HTML")
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if len(lines) >= 3:
                mithqal_buy_price = Decimal(lines[0])
                w = Decimal(lines[1])
                wage_cut = Decimal(lines[2])
                
                gram_buy_price = mithqal_buy_price / Decimal('5')
                net_gram_price = gram_buy_price - wage_cut
                total_iqd = net_gram_price * w
                
                prices = utils.get_goldsmith_prices(user_id) or {}
                goldsmith = utils.get_goldsmith(user_id) or {}
                
                usd_rate_single = Decimal(str(prices.get('usd_rate', 1530)))
                sheet_price = usd_rate_single * Decimal('100') if usd_rate_single < Decimal('5000') else usd_rate_single
                usd_bills = int(total_iqd // sheet_price) if sheet_price > 0 else 0
                rem_iqd = total_iqd % sheet_price if sheet_price > 0 else total_iqd
                
                shop_name = goldsmith.get('full_name') or 'محلي الموقر'
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("✅ تأكيد العملية", callback_data="confirm_invoice"),
                    types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_invoice")
                )
                
                invoice = (
                    f"{COMPANY_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📥 <b>فاتورة شراء ذهب (كسر)</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔷 <b>المحل العامر:</b> {shop_name}\n\n"
                    f"📥 <b>سعر شراء المثقال:</b> {fmt(mithqal_buy_price)} دينار\n"
                    f"⚖️ <b>الوزن الإجمالي:</b> {fmt(w)} غرام\n"
                    f"🔨 <b>أجور الخصم للغرام:</b> {fmt(wage_cut)} دينار\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 <b>سعر غرام الكسر الصافي:</b> {fmt(gram_buy_price)} دينار\n"
                    f"✨ <b>سعر الغرام بعد الخصم:</b> {fmt(net_gram_price)} دينار\n\n"
                    f"💵 <b>إجمالي صافي الحساب بالدينار:</b>\n"
                    f"👉 <b>{fmt(total_iqd)} دينار</b>\n\n"
                    f"💵 <b>صافي الحساب (ورق ودينار):</b>\n"
                    f"👉 <b>{fmt(usd_bills)} ورقة و {fmt(rem_iqd)} دينار</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['footer']}"
                )
                USER_STATE.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                
                bot.send_message(message.chat.id, invoice, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
                bot.send_message(message.chat.id, "📌 <b>يرجى اعتماد أو إلغاء الفاتورة أعلاه:</b>", parse_mode="HTML", reply_markup=markup)
            return
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

admin.register_admin_handlers(bot)

def morning_reminder_scheduler():
    iraq_tz = timezone(timedelta(hours=3))
    last_sent_date = None

    while True:
        try:
            now_iraq = datetime.now(iraq_tz)
            current_date_str = now_iraq.strftime("%Y-%m-%d")

            if now_iraq.hour == 10 and now_iraq.minute == 0 and last_sent_date != current_date_str:
                last_sent_date = current_date_str
                all_users = utils.get_all_goldsmiths()
                for u in all_users:
                    u_id = u.get('user_id')
                    if u_id:
                        try:
                            bot.send_message(
                                u_id,
                                f"{COMPANY_HEADER}\n☀️ <b>صباح الخير ومبارك رزقكم!</b>\n\n"
                                "جاهزون لإدارة حسابات اليوم بدقة تامة ومطابقة للحاسبة. أرسل العمليات مباشرة عبر الأزرار أدناه 💛",
                                parse_mode="HTML",
                                reply_markup=get_main_keyboard(u_id)
                            )
                        except Exception:
                            pass
                time.sleep(60)
        except Exception as e:
            print(f"Reminder error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    keep_alive_thread = threading.Thread(target=keep_alive_ping)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    reminder_thread = threading.Thread(target=morning_reminder_scheduler)
    reminder_thread.daemon = True
    reminder_thread.start()

    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    bot.infinity_polling(skip_pending=True)
