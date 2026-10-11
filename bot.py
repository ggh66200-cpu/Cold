import os
import re
import time
import threading
import urllib.request
import traceback
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

# خيط منع سيرفر Render من النوم 24/7
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
COMPANY_HEADER = admin.COMPANY_HEADER
SUPPORT_NUMBER = "07766083622" 

USER_STATE = {}
CALC_BUFFERS = {}  # تخزين القيم الحية لكل مستخدم

def fmt(value):
    try:
        d = Decimal(str(value))
        if d == d.to_integral_value():
            return f"{int(d):,}"
        else:
            return f"{d:,.2f}"
    except Exception:
        return str(value)

TEXTS = {
    "welcome": "👋 أهلاً بك في منصة <b>SMART GOLD SYSTEM</b>\n\nالمنظومة الذكية الأسرع والأدق لإدارة حسابات الذهب بدقة الحاسبة المكتبية المباشرة.\n🔑 <i>رقم العضوية:</i> <b>#{serial} صايغ معتمد</b>\n\nاختر العملية المطلوبة من الأزرار المثبتة أدناه للبدء فوراً 👇",
    "btn_sell": "🛍️ بيع للزبون",
    "btn_buy": "📥 شراء من الزبون",
    "btn_dollar": "💵 سعر الدولار والتعديل",
    "btn_info": "📖 معلومات النظام",
    "invoice_sell": "🧾 <b>فاتورة بيع ذهب للزبون</b> 🧾",
    "invoice_buy": "📥 <b>فاتورة شراء ذهب من الزبون</b> 📥",
    "shop": "🔷 المحل العامر: ",
    "weight_tot": "⚖️ الوزن الإجمالي بالغرام: {w} غرام",
    "wage_sell": "🔨 أجور صياغة الغرام: {wage} دينار",
    "total_iqd": "💵 <b>السعر الكلي بالدينار العراقي:</b>\n👉 <b>{total} دينار</b>",
    "total_usd": "💵 <b>صافي الحساب بالورق والدينار:</b>\n👉 <b>{usd} ورقة و {rem} دينار</b>",
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
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("🛠️ لوحة تحكم الإدارة (خاص)"))
    return markup

# صانع الحاسبة الحية التفاعلية (أزرار تحت الرسالة تنبض بالحياة)
def get_live_calculator_markup(current_text=""):
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("1️⃣", callback_data="calc_1"),
        types.InlineKeyboardButton("2️⃣", callback_data="calc_2"),
        types.InlineKeyboardButton("3️⃣", callback_data="calc_3"),
        types.InlineKeyboardButton("4️⃣", callback_data="calc_4"),
        types.InlineKeyboardButton("5️⃣", callback_data="calc_5"),
        types.InlineKeyboardButton("6️⃣", callback_data="calc_6"),
        types.InlineKeyboardButton("7️⃣", callback_data="calc_7"),
        types.InlineKeyboardButton("8️⃣", callback_data="calc_8"),
        types.InlineKeyboardButton("9️⃣", callback_data="calc_9"),
        types.InlineKeyboardButton("0️⃣", callback_data="calc_0"),
        types.InlineKeyboardButton("🔸 .", callback_data="calc_dot"),
        types.InlineKeyboardButton("⌫ مسح حرف", callback_data="calc_back"),
        types.InlineKeyboardButton("⏎ سطر جديد (إنتر)", callback_data="calc_newline"),
        types.InlineKeyboardButton("❌ إلغاء", callback_data="calc_cancel"),
        types.InlineKeyboardButton("✅ تم الحساب", callback_data="calc_done")
    )
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
            COMPANY_HEADER + TEXTS["welcome"].format(serial=serial), 
            parse_mode="HTML", 
            reply_markup=markup
        )
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    try:
        gs = utils.get_goldsmith(user_id) or {}
        is_admin = (user_id == ADMIN_ID)
        
        if not gs.get('is_registered', False):
            USER_STATE[user_id] = "WAITING_REGISTRATION_FULL"
            CALC_BUFFERS[user_id] = ""
            bot.send_message(
                message.chat.id, 
                f"{COMPANY_HEADER}🌟 <b>مرحباً بك في منظومة ARAMKY الاحترافية!</b> 🌟\n\n"
                "لتفعيل حسابك، أرسل اسم المحل ورقم هاتفك:", 
                parse_mode="HTML"
            )
            return

        remaining_days = gs.get('remaining_days', 0)
        if remaining_days <= 0 and not is_admin:
            show_subscription_form(message, expired=True)
            return

        USER_STATE.pop(user_id, None)
        CALC_BUFFERS.pop(user_id, None)
        send_main_menu(message, user_id)
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_info"])
def show_system_info(message):
    user_id = message.from_user.id
    try:
        gs = utils.get_goldsmith(user_id) or {}
        remaining_days = gs.get('remaining_days', 0)
        info_text = (
            f"{COMPANY_HEADER}"
            "📖 <b>تفاصيل النظام ومعلومات الحساب:</b>\n\n"
            f"⏳ الأيام المتبقية للاشتراك: <b>{remaining_days} يوم</b>\n"
            "🔹 حاسبة أزرار تفاعلية حية داخل البوت\n"
            "🔹 مطابقة تامة لنتائج الحاسبة المكتبية بدون تقريب\n"
            "🔹 يعمل أونلاين بالخلفية 24/7 دون انقطاع\n\n"
            f"📞 <b>الدعم الفني والطوارئ:</b> <code>{SUPPORT_NUMBER}</code>"
        )
        bot.send_message(message.chat.id, info_text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

def show_subscription_form(message, expired=False):
    user_id = message.from_user.id
    try:
        USER_STATE[user_id] = "WAITING_RECEIPT"
        prefix = "🚨 <b>انتهت فترتك التجريبية! يرجى التجديد للاستمرار:</b>\n\n" if expired else ""
        sub_text = (
            f"{COMPANY_HEADER}{prefix}"
            f"🔹 <b>الاشتراك الشهري:</b> <b>{MONTHLY_PRICE}</b>\n"
            f"🔹 <b>ماستر كارد التحويل:</b> <code>{MASTER_CARD}</code>\n"
            f"📞 <b>الدعم الفني:</b> <code>{SUPPORT_NUMBER}</code>\n\n"
            "📸 أرسل صورة وصل التحويل هنا لتفعيل اشتراكك."
        )
        bot.send_message(message.chat.id, sub_text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
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
            f"{COMPANY_HEADER}"
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
        bot.answer_callback_query(call.id, text="🧮 فتح الحاسبة الحية...")
        USER_STATE[user_id] = "WAITING_SINGLE_PRICE_VALUE"
        CALC_BUFFERS[user_id] = ""
        
        text = (
            f"💵 <b>أدخل سعر صرف الـ 100$ الجديد عبر الحاسبة الحية:</b>\n\n"
            f"📥 <i>القيمة المتراكمة حالياً:</i>\n<code>(فارغ)</code>"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=get_live_calculator_markup())
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_sell"])
def customer_sell_init(message):
    user_id = message.from_user.id
    try:
        USER_STATE[user_id] = "WAITING_SELL_INPUTS"
        CALC_BUFFERS[user_id] = ""
        
        text = (
            f"{COMPANY_HEADER}🛍️ <b>حساب بيع زبون (حاسبة تفاعلية حية):</b>\n\n"
            "استخدم أزرار الحاسبة أدناه لإدخال:\n"
            "1️⃣ سعر المثقال ⟵ ⏎ سطر جديد\n"
            "2️⃣ الوزن ⟵ ⏎ سطر جديد\n"
            "3️⃣ أجور الصياغة\nثم اضغط <b>✅ تم الحساب</b>\n\n"
            f"📥 <i>القيمة المدخلة حالياً:</i>\n<code>(فارغ)</code>"
        )
        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=get_live_calculator_markup())
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_buy"])
def customer_buy_init(message):
    user_id = message.from_user.id
    try:
        USER_STATE[user_id] = "WAITING_BUY_INPUTS"
        CALC_BUFFERS[user_id] = ""
        
        text = (
            f"{COMPANY_HEADER}📥 <b>حساب شراء كسر (حاسبة تفاعلية حية):</b>\n\n"
            "استخدم أزرار الحاسبة أدناه لإدخال:\n"
            "1️⃣ سعر شراء المثقال ⟵ ⏎ سطر جديد\n"
            "2️⃣ الوزن ⟵ ⏎ سطر جديد\n"
            "3️⃣ أجور الخصم\nثم اضغط <b>✅ تم الحساب</b>\n\n"
            f"📥 <i>القيمة المدخلة حالياً:</i>\n<code>(فارغ)</code>"
        )
        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=get_live_calculator_markup())
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

# معالج ضغطات أزرار الحاسبة الحية التفاعلية
@bot.callback_query_handler(func=lambda call: call.data.startswith("calc_") or call.data in ["confirm_invoice", "cancel_invoice"])
def handle_calculator_callbacks(call):
    user_id = call.from_user.id
    try:
        data = call.data
        
        if data in ["confirm_invoice", "cancel_invoice"]:
            if data == "confirm_invoice":
                bot.answer_callback_query(call.id, text="✅ تمت العملية بنجاح!")
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                bot.send_message(call.message.chat.id, "✅ <b>تم اعتماد الفاتورة بنجاح!</b> 💛", parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
            else:
                bot.answer_callback_query(call.id, text="❌ تم إلغاء العملية")
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                bot.send_message(call.message.chat.id, "❌ <b>تم إلغاء الفاتورة.</b>", parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
            USER_STATE.pop(user_id, None)
            CALC_BUFFERS.pop(user_id, None)
            return

        current_buf = CALC_BUFFERS.get(user_id, "")
        state = USER_STATE.get(user_id)

        if data == "calc_cancel":
            USER_STATE.pop(user_id, None)
            CALC_BUFFERS.pop(user_id, None)
            bot.answer_callback_query(call.id, text="❌ تم إلغاء العملية")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            bot.send_message(call.message.chat.id, "❌ <b>تم الإلغاء.</b>", parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
            return

        elif data.startswith("calc_") and data not in ["calc_cancel", "calc_done", "calc_back", "calc_newline"]:
            char = data.replace("calc_", "")
            current_buf += char
            CALC_BUFFERS[user_id] = current_buf
            bot.answer_callback_query(call.id, text=f"إضافه: {char}")

        elif data == "calc_back":
            current_buf = current_buf[:-1]
            CALC_BUFFERS[user_id] = current_buf
            bot.answer_callback_query(call.id, text="⌫ مسح حرف")

        elif data == "calc_newline":
            current_buf += "\n"
            CALC_BUFFERS[user_id] = current_buf
            bot.answer_callback_query(call.id, text="⏎ سطر جديد")

        elif data == "calc_done":
            bot.answer_callback_query(call.id, text="✅ جاري التنفيذ والحساب...")
            text = to_english_numbers(current_buf)
            
            if state == "WAITING_SINGLE_PRICE_VALUE":
                clean_val = text.replace('\n', '').strip()
                if re.match(r'^\d+(\.\d+)?$', clean_val):
                    val = Decimal(clean_val)
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
                    CALC_BUFFERS.pop(user_id, None)
                    try:
                        bot.delete_message(call.message.chat.id, call.message.message_id)
                    except Exception:
                        pass
                    bot.send_message(call.message.chat.id, f"✅ <b>تم تحديث سعر صرف الـ 100$ بنجاح إلى:</b> <code>{fmt(usd_100_val)} دينار</code>", parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
                return

            elif state == "WAITING_SELL_INPUTS":
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
                        f"{COMPANY_HEADER}{TEXTS['invoice_sell']}\n━━━━━━━━━━━━━━━━━\n"
                        f"{TEXTS['shop']}{shop_name}\n"
                        f"🟡 <b>سعر المثقال المعتمد:</b> <code>{fmt(mithqal_price)} دينار</code>\n"
                        f"{TEXTS['weight_tot'].format(w=float(w))}\n"
                        f"{TEXTS['wage_sell'].format(wage=fmt(wage))}\n"
                        f"━━━━━━━━━━━━━━━━━\n"
                        f"💰 <b>سعر غرام الصافي:</b> <code>{fmt(gram_price)} دينار</code>\n"
                        f"💵 <b>سعر غرام مع الأجور:</b> <code>{fmt(gram_full)} دينار</code>\n"
                        f"{TEXTS['total_iqd'].format(total=fmt(total_iqd))}\n\n"
                        f"{TEXTS['total_usd'].format(usd=usd_bills, rem=fmt(rem_iqd))}\n━━━━━━━━━━━━━━━━━\n{TEXTS['footer']}"
                    )
                    USER_STATE.pop(user_id, None)
                    CALC_BUFFERS.pop(user_id, None)
                    try:
                        bot.delete_message(call.message.chat.id, call.message.message_id)
                    except Exception:
                        pass
                    bot.send_message(call.message.chat.id, invoice, parse_mode="HTML", reply_markup=markup)
                return

            elif state == "WAITING_BUY_INPUTS":
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
                        f"{COMPANY_HEADER}{TEXTS['invoice_buy']}\n━━━━━━━━━━━━━━━━━\n"
                        f"{TEXTS['shop']}{shop_name}\n"
                        f"📥 <b>سعر شراء المثقال:</b> <code>{fmt(mithqal_buy_price)} دينار</code>\n"
                        f"{TEXTS['weight_tot'].format(w=float(w))}\n"
                        f"🔨 <b>أجور الخصم للغرام:</b> {fmt(wage_cut)} دينار\n"
                        f"━━━━━━━━━━━━━━━━━\n"
                        f"💰 <b>سعر غرام الكسر الصافي:</b> <code>{fmt(net_gram_price)} دينار</code>\n"
                        f"{TEXTS['total_iqd'].format(total=fmt(total_iqd))}\n\n"
                        f"{TEXTS['total_usd'].format(usd=usd_bills, rem=fmt(rem_iqd))}\n━━━━━━━━━━━━━━━━━\n{TEXTS['footer']}"
                    )
                    USER_STATE.pop(user_id, None)
                    CALC_BUFFERS.pop(user_id, None)
                    try:
                        bot.delete_message(call.message.chat.id, call.message.message_id)
                    except Exception:
                        pass
                    bot.send_message(call.message.chat.id, invoice, parse_mode="HTML", reply_markup=markup)
                return

        # تحديث شاشة الحاسبة الحية بالقيم الجديدة فوراً
        display_text = current_buf if current_buf else "(فارغ)"
        updated_msg = (
            f"🧮 <b>الحاسبة التفاعلية الحية:</b>\n\n"
            f"📥 <i>القيمة المدخلة حالياً:</i>\n<code>{display_text}</code>"
        )
        try:
            bot.edit_message_text(
                updated_msg,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="HTML",
                reply_markup=get_live_calculator_markup(current_buf)
            )
        except Exception:
            pass

    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

admin.register_admin_handlers(bot)

# جدولة إرسال تذكير صباحي يومي الساعة 10:00 صباحاً
def morning_reminder_scheduler():
    while True:
        try:
            now = time.localtime()
            if now.tm_hour == 10 and now.tm_min == 0:
                all_users = utils.get_all_goldsmiths()
                for u in all_users:
                    u_id = u.get('user_id')
                    if u_id:
                        try:
                            bot.send_message(
                                u_id,
                                f"{COMPANY_HEADER}☀️ <b>صباح الخير ومبارك رزقكم!</b>\n\n"
                                "جاهزون لإدارة حسابات اليوم بدقة تامة ومطابقة للحاسبة. أرسل العمليات مباشرة عبر الأزرار أدناه 💛",
                                parse_mode="HTML"
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
