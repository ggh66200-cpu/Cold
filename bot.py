import os
import re
import traceback
import telebot
from telebot import types
from flask import Flask
import threading
import utils
import admin

BOT_TOKEN = os.environ.get("BOT_TOKEN")

try:
    ADMIN_ID = int(os.environ.get("ADMIN_ID", getattr(admin, "ADMIN_ID", 0)))
except:
    ADMIN_ID = 0

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "SMART GOLD SYSTEM IS LIVE 24/7"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

MASTER_CARD = admin.MASTER_CARD
MONTHLY_PRICE = admin.MONTHLY_PRICE
COMPANY_HEADER = admin.COMPANY_HEADER
SUPPORT_NUMBER = "07872180902" 

USER_STATE = {}
INVOICE_DATA = {}

TEXTS = {
    "welcome": "👋 أهلاً بك في عمالقة الصياغة <b>SMART GOLD SYSTEM</b>\n\nالمنظومة الذكية الأسرع والأدق لإدارة حسابات الصياغة محلياً ودولياً بمعايير المصارف العالمية.\n🔑 <i>رقم عضويتك التسلسلي في النخبة:</i> <b>#{serial} صايغ معتمد</b>\n\nالرعاة الرسميون لنجاح عملك.. استخدم الأزرار أدناه للبدء بالعمليات اليومية 👇",
    "btn_prices": "⚙️ إدخال أسعار الصباح اليومية",
    "btn_sell": "📥 حساب بيع لزبون",
    "btn_buy": "📤 حساب شراء من زبون",
    "btn_info": "📖 شرح النظام والمواصفات",
    "btn_clients": "👥 جرد العملاء والعمليات",
    "btn_admin_panel": "🛠️ لوحة تحكم الإدارة (خاص)",
    "invoice_sell": "🧾 <b>فاتورة بيع ذهب للزبون</b> 🧾",
    "invoice_buy": "📥 <b>فاتورة شراء ذهب من الزبون</b> 📥",
    "shop": "🔷 المحل العامر: ",
    "type_sell": "🔷 العيار ونوع الحساب: عيار {carat} (حساب بيع بالغرام)",
    "type_buy": "🔷 العيار ونوع الحساب: عيار {carat} (حساب شراء بالغرام)",
    "weight_req": "🔷 الوزن المطلوب: {w} غرام",
    "weight_tot": "⚖️ الوزن الإجمالي بالجرام: {w} غرام",
    "wage_sell": "🔨 أجور صياغة الغرام (مضافة): {wage:,.0f} دينار",
    "wage_buy": "🔨 كسر أجور الصياغة (مخصومة): {wage:,.0f} دينار",
    "clean_p": "💰 سعر غرام الذهب الصافي: {p:,.0f} دينار",
    "full_p": "💵 سعر الغرام مع أجور الصائغ: {p:,.0f} دينار",
    "total_iqd": "💵 <b>السعر الكلي بالدينار العراقي:</b>\n👉 <b>{total:,.0f} دينار</b>",
    "total_usd": "💵 <b>صافي الحساب بالورق والدينار:</b>\n👉 <b>{usd} ورقة و {rem:,.0f} دينار</b>",
    "footer": "🌸 ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب! 💛",
    "req_weight_sell": "⚖️ <b>عيار {carat} (حساب بيع للزبون):</b>\nأرسل وزن الذهب بالغرام فقط (مثال: 8.963):",
    "req_buy_inputs": "📥 <b>عيار {carat} (حساب شراء من زبون):</b>\nيرجى إرسال البيانات المطلوبة بالترتيب في رسالة واحدة (كل قيمة بسطر):\n\n<code>1️⃣ سعر المثقال للشراء\n2️⃣ الوزن بالغرام\n3️⃣ أجور الكسر للغرام</code>\n\n💡 <i>مثال للنسخ والتعديل:</i>\n<code>780000\n15.420\n2000</code>"
}

def notify_admin_error(user_id, error_msg, traceback_str=""):
    if not ADMIN_ID:
        return
    try:
        error_report = (
            f"🚨 <b>تقرير خطأ أو تعثر استجابة (Exception Alert)</b> 🚨\n\n"
            f"👤 <b>معرف المستخدم (User ID):</b> <code>{user_id}</code>\n"
            f"⚠️ <b>السبب / رسالة الخطأ:</b>\n<code>{error_msg}</code>\n\n"
            f"📜 <b>التفاصيل التقنية (Traceback):</b>\n"
            f"<pre>{traceback_str[:3000]}</pre>"
        )
        bot.send_message(ADMIN_ID, error_report, parse_mode="HTML")
    except Exception as e:
        print(f"Failed to send error notification to admin: {e}")

def to_english_numbers(text):
    arabic_nums = str.maketrans('٠١ي٣٤٥٦٧٨٩', '0123456789')
    persian_nums = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    return text.translate(arabic_nums).translate(persian_nums)

def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton(TEXTS["btn_prices"]))
    markup.add(types.KeyboardButton(TEXTS["btn_sell"]), types.KeyboardButton(TEXTS["btn_buy"]))
    markup.add(types.KeyboardButton(TEXTS["btn_info"]), types.KeyboardButton(TEXTS["btn_clients"]))
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton(TEXTS["btn_admin_panel"]))
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
        except:
            pass
        
        bot.send_message(
            message.chat.id, 
            COMPANY_HEADER + TEXTS["welcome"].format(serial=serial), 
            parse_mode="HTML", 
            reply_markup=markup
        )
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())
        raise e

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    try:
        gs = utils.get_goldsmith(user_id) or {}
        is_admin = (user_id == ADMIN_ID)
        
        if not gs.get('is_registered', False):
            USER_STATE[user_id] = "WAITING_REGISTRATION_FULL"
            bot.send_message(
                message.chat.id, 
                f"{COMPANY_HEADER}🌟 <b>مرحباً بك في قمة الاحتراف الرقمي لعالم الصياغة!</b> 🌟\n\n"
                "لتفعيل فترتك التجريبية الحصرية (3 أيام مجاناً)، يرجى إرسال بيانات محلك برسالة واحدة كالتالي:\n\n"
                "🏢 <b>اسم المحل:</b>\n"
                "📱 <b>رقم الهاتف:</b>\n\n"
                "💡 <i>مثال:</i>\n<code>مجوهرات البركة\n07800000000</code>", 
                parse_mode="HTML"
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

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_info"])
def show_system_info(message):
    user_id = message.from_user.id
    try:
        info_text = (
            f"{COMPANY_HEADER}"
            "📖 <b>شرح النظام والمواصفات الفنية:</b>\n\n"
            "1️⃣ <b>إدخال أسعار الصباح:</b> لتحديث أسعار الذهب والعيارات مع أجورها والدولار (11 حقلاً عمودياً).\n"
            "2️⃣ <b>حساب البيع والشراء:</b> لاحتساب دقيق ومباشر لجميع العيارات.\n"
            "3️⃣ <b>جرد العملاء:</b> لمتابعة الأيام المتبقية وحالة الاشتراك.\n\n"
            f"📞 <b>الدعم الفني:</b> <code>{SUPPORT_NUMBER}</code>"
        )
        bot.send_message(message.chat.id, info_text, parse_mode="HTML")
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

def show_subscription_form(message, expired=False):
    user_id = message.from_user.id
    try:
        USER_STATE[user_id] = "WAITING_RECEIPT"
        prefix = "🚨 <b>انتهت فترتك التجريبية المجانية! بادر بتجديد اشتراكك:</b>\n\n" if expired else ""
        sub_text = (
            f"{COMPANY_HEADER}{prefix}"
            f"🔹 <b>الاشتراك الشهري:</b> <b>{MONTHLY_PRICE}</b>\n"
            f"🔹 <b>ماستر كارد التحويل:</b> <code>{MASTER_CARD}</code>\n"
            f"📞 <b>الدعم الفني:</b> <code>{SUPPORT_NUMBER}</code>\n\n"
            "📸 أرسل صورة وصل التحويل هنا لتفعيل اشتراكك."
        )
        bot.send_message(message.chat.id, sub_text, parse_mode="HTML")
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_clients"])
def show_clients_summary(message):
    user_id = message.from_user.id
    try:
        gs = utils.get_goldsmith(user_id) or {}
        shop_name = gs.get('full_name') or gs.get('shop_name') or 'محلي الموقر'
        remaining_days = gs.get('remaining_days', 0)
        
        summary_text = (
            f"{COMPANY_HEADER}"
            "📊 <b>جرد العمليات وحالة الحساب:</b>\n\n"
            f"🔷 اسم المحل: <b>{shop_name}</b>\n"
            f"⏳ الأيام المتبقية: <b>{remaining_days} يوم</b>\n"
            f"📞 الدعم الفني: <code>{SUPPORT_NUMBER}</code>"
        )
        bot.send_message(message.chat.id, summary_text, parse_mode="HTML")
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_admin_panel"])
def admin_panel_shortcut(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        try:
            admin.admin_panel_start(message, bot)
        except Exception as e:
            notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_prices"])
def morning_prices_start(message):
    user_id = message.from_user.id
    try:
        gs = utils.get_goldsmith(user_id) or {}
        is_admin = (user_id == ADMIN_ID)
        if gs.get('remaining_days', 0) <= 0 and not is_admin:
            return show_subscription_form(message, expired=True)
        
        USER_STATE[user_id] = "AWAITING_ALL_PRICES"
        instruction = (
            f"{COMPANY_HEADER}"
            "☀️ <b>تحديث أسعار البورصة الصباحية (11 حقلاً عمودياً):</b>\n\n"
            "💡 <b>نموذج الإدخال بالترتيب:</b>\n"
            "<code>1020000\n935000\n900000\n450000\n400000\n3000\n3500\n4500\n7500\n2500\n153000</code>\n\n"
            "✍️ <b>تفصيل الأسطر الـ 11:</b>\n"
            "1️⃣ سعر عيار 24\n"
            "2️⃣ سعر عيار 22\n"
            "3️⃣ سعر عيار 21\n"
            "4️⃣ سعر عيار 18\n"
            "5️⃣ سعر عيار 9 (أو المعيار الجديد)\n"
            "6️⃣ أجور غرام 24\n"
            "7️⃣ أجور غرام 22\n"
            "8️⃣ أجور غرام 21\n"
            "9️⃣ أجور غرام 18\n"
            "🔟 أجور غرام 9\n"
            "1️⃣1️⃣ سعر صرف 100$\n\n"
            "👉 <i>أرسل الأسطر الـ 11 الآن.</i>"
        )
        bot.send_message(message.chat.id, instruction, parse_mode="HTML")
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_sell"])
def customer_sell_init(message):
    user_id = message.from_user.id
    try:
        gs = utils.get_goldsmith(user_id) or {}
        is_admin = (user_id == ADMIN_ID)
        if gs.get('remaining_days', 0) <= 0 and not is_admin:
            return show_subscription_form(message, expired=True)

        USER_STATE.pop(user_id, None)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🟡 عيار 24", callback_data="sell_24"),
            types.InlineKeyboardButton("🟡 عيار 22", callback_data="sell_22"),
            types.InlineKeyboardButton("🟡 عيار 21", callback_data="sell_21"),
            types.InlineKeyboardButton("🟡 عيار 18", callback_data="sell_18"),
            types.InlineKeyboardButton("🟡 عيار 9", callback_data="sell_9")
        )
        bot.send_message(message.chat.id, f"{COMPANY_HEADER}📥 <b>اختر عيار البيع للزبون:</b>", parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_buy"])
def customer_buy_init(message):
    user_id = message.from_user.id
    try:
        gs = utils.get_goldsmith(user_id) or {}
        is_admin = (user_id == ADMIN_ID)
        if gs.get('remaining_days', 0) <= 0 and not is_admin:
            return show_subscription_form(message, expired=True)

        USER_STATE.pop(user_id, None)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🪙 عيار 24 (شراء كسر)", callback_data="buy_24"),
            types.InlineKeyboardButton("🪙 عيار 22 (شراء كسر)", callback_data="buy_22"),
            types.InlineKeyboardButton("🪙 عيار 21 (شراء كسر)", callback_data="buy_21"),
            types.InlineKeyboardButton("🪙 عيار 18 (شراء كسر)", callback_data="buy_18"),
            types.InlineKeyboardButton("🪙 عيار 9 (شراء كسر)", callback_data="buy_9")
        )
        bot.send_message(message.chat.id, f"{COMPANY_HEADER}📤 <b>اختر عيار الشراء (الكسر) من الزبون:</b>", parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.callback_query_handler(func=lambda call: call.data.startswith("sell_") or call.data.startswith("buy_"))
def handle_calc_buttons(call):
    user_id = call.from_user.id
    try:
        bot.answer_callback_query(call.id, text="⚡ جاري تفعيل الحاسبة...")
        parts = call.data.split("_")
        mode = parts[0]     
        carat = int(parts[1]) 
        INVOICE_DATA[user_id] = {'carat': carat, 'mode': mode}
        
        if mode == "sell":
            USER_STATE[user_id] = "WAITING_WEIGHT_SELL"
            bot.send_message(call.message.chat.id, TEXTS["req_weight_sell"].format(carat=carat), parse_mode="HTML")
        elif mode == "buy":
            USER_STATE[user_id] = "WAITING_BUY_ALL_INPUTS"
            bot.send_message(call.message.chat.id, TEXTS["req_buy_inputs"].format(carat=carat), parse_mode="HTML")
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_sub_") or call.data.startswith("reject_sub_") or call.data.startswith("time_"))
def handle_admin_actions(call):
    user_id = call.from_user.id
    data = call.data
    try:
        if data.startswith("approve_sub_"):
            target_user = int(data.split("_")[2])
            utils.update_goldsmith_subscription(target_user, days=30)
            bot.answer_callback_query(call.id, text="✅ تم التفعيل بنجاح!")
            try:
                bot.send_message(target_user, f"{COMPANY_HEADER}🎉 <b>تم تفعيل اشتراكك الشهري بنجاح لمدة 30 يوم!</b> 💛", parse_mode="HTML", reply_markup=get_main_keyboard(target_user))
            except:
                pass
        elif data.startswith("reject_sub_"):
            target_user = int(data.split("_")[2])
            bot.answer_callback_query(call.id, text="❌ تم الرفض")
            try:
                bot.send_message(target_user, f"{COMPANY_HEADER}⚠️ <b>عفواً، تم رفض الإيصال من قبل الإدارة.</b>", parse_mode="HTML")
            except:
                pass
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(content_types=['photo'])
def process_customer_receipt(message):
    user_id = message.from_user.id
    if USER_STATE.get(user_id) == "WAITING_RECEIPT":
        USER_STATE.pop(user_id, None)
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري إرسال الإيصال للإدارة...</i>", parse_mode="HTML")
        try:
            gs = utils.get_goldsmith(user_id) or {}
            shop_name = gs.get('full_name') or gs.get('shop_name') or 'غير متوفر'
            phone = gs.get('phone', 'غير متوفر')
            
            photo = message.photo[-1].file_id
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ موافقة وتفعيل (30 يوم)", callback_data=f"approve_sub_{user_id}"),
                types.InlineKeyboardButton("❌ رفض الإيصال", callback_data=f"reject_sub_{user_id}")
            )
            admin_text = f"🚨 <b>طلب اشتراك جديد!</b>\n\n👤 الآيدي: <code>{user_id}</code>\n🔷 المحل: {shop_name}\n📱 الهاتف: {phone}"
            bot.send_photo(ADMIN_ID, photo, caption=admin_text, parse_mode="HTML", reply_markup=markup)
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, "✅ <b>تم إرسال الإيصال بنجاح للإدارة!</b>", parse_mode="HTML")
        except Exception as e:
            notify_admin_error(user_id, str(e), traceback.format_exc())

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    user_id = message.from_user.id
    try:
        text = to_english_numbers(message.text.strip())
        state = USER_STATE.get(user_id)

        if state == "WAITING_REGISTRATION_FULL":
            loading = bot.send_message(message.chat.id, "⏳ <i>جاري تأسيس الحساب...</i>", parse_mode="HTML")
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            shop_name = lines[0] if len(lines) >= 1 else text
            phone = lines[1] if len(lines) >= 2 else "غير محدد"
            
            utils.register_goldsmith_details(user_id, shop_name, phone)
            USER_STATE.pop(user_id, None)
            bot.delete_message(message.chat.id, loading.message_id)
            bot.send_message(message.chat.id, "💎 <b>تم تسجيل محلك وتفعيل 3 أيام تجريبية بنجاح!</b>", parse_mode="HTML")
            send_main_menu(message, user_id)
            return

        if state == "AWAITING_ALL_PRICES":
            loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري حفظ الأسعار والأجور...</i>", parse_mode="HTML")
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if len(lines) == 11:
                usd_100_input = float(lines[10])
                usd_rate_single = usd_100_input / 100.0 if usd_100_input > 1000 else usd_100_input

                utils.update_morning_prices(
                    user_id,
                    p24=float(lines[0]),
                    p22=float(lines[1]),
                    p21=float(lines[2]),
                    p18=float(lines[3]),
                    p9=float(lines[4]),
                    w24=float(lines[5]),
                    w22=float(lines[6]),
                    w21=float(lines[7]),
                    w18=float(lines[8]),
                    w9=float(lines[9]),
                    usd_r=usd_rate_single  
                )
                USER_STATE.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, "✅ <b>تم تحديث أسعار الصباح والأجور للعيارات الخمسة بنجاح تام!</b>", parse_mode="HTML")
            else:
                bot.edit_message_text(f"⚠️ خطأ: يرجى إرسال **11 حقلاً** بالضبط (أنت أرسلت {len(lines)} أسطر).", message.chat.id, loading_msg.message_id, parse_mode="HTML")
            return

        if state == "WAITING_WEIGHT_SELL":
            loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري الحساب...</i>", parse_mode="HTML")
            if re.match(r'^\d+(\.\d+)?$', text):
                w = float(text)
                carat = INVOICE_DATA[user_id]['carat']
                prices = utils.get_goldsmith_prices(user_id) or {}
                goldsmith = utils.get_goldsmith(user_id) or {}
                
                price_key = f"price_{carat}"
                wage_key = f"wage_{carat}"
                
                gram_price = float(prices.get(price_key, 0)) / 5.0
                wage = float(prices.get(wage_key, 0))
                
                gram_full = gram_price + wage
                total_iqd = gram_full * w
                
                usd_rate_single = float(prices.get('usd_rate', 1))
                sheet_price = usd_rate_single * 100 if usd_rate_single < 5000 else usd_rate_single
                usd_bills = int(total_iqd // sheet_price) if sheet_price > 0 else 0
                rem_iqd = total_iqd % sheet_price if sheet_price > 0 else total_iqd
                
                shop_name = goldsmith.get('full_name') or 'محلي الموقر'
                
                invoice = (
                    f"{COMPANY_HEADER}{TEXTS['invoice_sell']}\n━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['shop']}{shop_name}\n"
                    f"{TEXTS['type_sell'].format(carat=carat)}\n"
                    f"{TEXTS['weight_tot'].format(w=w)}\n{TEXTS['wage_sell'].format(wage=wage)}\n"
                    f"━━━━━━━━━━━━━━━━━\n{TEXTS['clean_p'].format(p=gram_price)}\n"
                    f"{TEXTS['full_p'].format(p=gram_full)}\n{TEXTS['total_iqd'].format(total=total_iqd)}\n\n"
                    f"{TEXTS['total_usd'].format(usd=usd_bills, rem=rem_iqd)}\n━━━━━━━━━━━━━━━━━\n{TEXTS['footer']}"
                )
                USER_STATE.pop(user_id, None)
                INVOICE_DATA.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, invoice, parse_mode="HTML")
            return

        if state == "WAITING_BUY_ALL_INPUTS":
            loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري حساب الكسر...</i>", parse_mode="HTML")
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if len(lines) == 3:
                mithqal_buy_price = float(lines[0])
                w = float(lines[1])
                wage_cut = float(lines[2])
                
                carat = INVOICE_DATA[user_id]['carat']
                goldsmith = utils.get_goldsmith(user_id) or {}
                prices = utils.get_goldsmith_prices(user_id) or {}
                
                gram_buy_price = mithqal_buy_price / 5.0
                net_gram_price = gram_buy_price - wage_cut
                total_iqd = net_gram_price * w
                
                usd_rate_single = float(prices.get('usd_rate', 1))
                sheet_price = usd_rate_single * 100 if usd_rate_single < 5000 else usd_rate_single
                usd_bills = int(total_iqd // sheet_price) if sheet_price > 0 else 0
                rem_iqd = total_iqd % sheet_price if sheet_price > 0 else total_iqd
                
                shop_name = goldsmith.get('full_name') or 'محلي الموقر'
                
                invoice = (
                    f"{COMPANY_HEADER}{TEXTS['invoice_buy']}\n━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['shop']}{shop_name}\n"
                    f"{TEXTS['type_buy'].format(carat=carat)}\n"
                    f"📥 <b>سعر شراء المثقال:</b> <code>{mithqal_buy_price:,.0f} دينار</code>\n"
                    f"{TEXTS['weight_tot'].format(w=w)}\n"
                    f"{TEXTS['wage_buy'].format(wage=wage_cut)}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"💰 <b>سعر غرام الكسر الصافي:</b> <code>{net_gram_price:,.0f} دينار</code>\n"
                    f"{TEXTS['total_iqd'].format(total=total_iqd)}\n\n"
                    f"{TEXTS['total_usd'].format(usd=usd_bills, rem=rem_iqd)}\n━━━━━━━━━━━━━━━━━\n{TEXTS['footer']}"
                )
                USER_STATE.pop(user_id, None)
                INVOICE_DATA.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, invoice, parse_mode="HTML")
            return
    except Exception as e:
        notify_admin_error(user_id, str(e), traceback.format_exc())

admin.register_admin_handlers(bot)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    bot.infinity_polling(skip_pending=True)
