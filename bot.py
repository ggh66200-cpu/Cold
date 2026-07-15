import os
import json
import telebot
from telebot import types

# 🔑 جلب المفاتيح الخاصة بالبوت بأمان تام من السيرفر
TOKEN = os.getenv("TELEGRAM_TOKEN")

# إذا لم يجد التوكن في البيئة الآمنة، يحاول قراءته من ملف settings.py الخاص بك لضمان عدم التوقف
if not TOKEN:
    try:
        import settings
        TOKEN = getattr(settings, "TOKEN", None) or getattr(settings, "TELEGRAM_TOKEN", None)
    except ImportError:
        TOKEN = None

# إذا لم يعثر على التوكن نهائياً، يطبع تنبيهاً واضحاً في السيرفر
if not TOKEN:
    raise ValueError("⚠️ خطأ أمني: لم يتم العثور على توكن البوت (TELEGRAM_TOKEN) في إعدادات السيرفر أو ملف settings.py!")

bot = telebot.TeleBot(TOKEN)

# 📂 مسار ملف البيانات لإعدادات الصباح
DATA_FILE = "data.json"

# استيراد ملفات الاشتراك والتحكم الخاصة بك إذا كانت موجودة
try:
    import sub
    HAS_SUB_SYSTEM = True
except ImportError:
    HAS_SUB_SYSTEM = False

try:
    import admin
    HAS_ADMIN_SYSTEM = True
except ImportError:
    HAS_ADMIN_SYSTEM = False


# دالة تحميل الإعدادات من السيرفر لضمان قراءة أحدث قيم دائماً
def load_settings():
    default_settings = {
        "mithqal_21": 450000,
        "mithqal_18": 380000,
        "labor_21": 10000,
        "labor_18": 10000,
        "usd_100": 150000
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_settings
    return default_settings

# دالة حفظ الإعدادات على السيرفر
def save_settings(settings):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

# الحالات المؤقتة للمستخدمين
user_states = {}
user_data = {}

# دالة حساب الورق والدينار العراقي الذكية (بدون دنانير)
def calculate_paper_and_dinar(total_iqd, usd_rate):
    if usd_rate <= 0:
        return f"{total_iqd:,.0f} دينار"
    
    papers = int(total_iqd // usd_rate)
    remaining_iqd = int(total_iqd % usd_rate)
    
    result = []
    if papers > 0:
        if papers == 1:
            result.append("1 ورقة")
        elif papers == 2:
            result.append("2 ورقة")
        else:
            result.append(f"{papers} ورقة")
            
    if remaining_iqd > 0:
        result.append(f"{remaining_iqd:,.0f} دينار")
        
    if not result:
        return "0 دينار"
        
    return " و ".join(result)

# القائمة الرئيسية للبوت
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_sell = types.KeyboardButton("💰 بيع للزبون")
    btn_buy = types.KeyboardButton("⚖️ شراء من زبون")
    btn_settings = types.KeyboardButton("⚙️ إعدادات الصباح")
    markup.add(btn_sell, btn_buy)
    markup.add(btn_settings)
    return markup

# زر الرجوع السريع
def back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("⬅️ الرجوع للرئيسية"))
    return markup

# رسالة الترحيب والعدد الوهمي
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_states[message.chat.id] = None
    user_data[message.chat.id] = {}
    
    # التحقق من الاشتراك إذا كان ملف sub.py مفعلاً وموجوداً بالسيرفر
    if HAS_SUB_SYSTEM:
        try:
            if not sub.check_user_subscription(message.chat.id):
                # إذا كان غير مشترك ينقله لصفحة الاشتراك الخاصة بنظامك
                sub.send_subscription_prompt(bot, message.chat.id)
                return
        except Exception as e:
            print(f"Sub check bypass error: {e}")

    welcome_text = (
        "✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\n"
        "مرحباً بك في نظام الصياغة الذكي الأسرع والأدق في العراق! 👑\n"
        "البوت مصمم بالكامل لتسهيل حسابات البيع والشراء اليومية لمحلك بدقة متناهية وبلمسة زر واحدة.\n\n"
        "👥 **عدد الصاغة النشطين في النظام حالياً:** `166 صائغ`\n\n"
        "نسأل الله العلي القدير أن يبارك في تجارتكم ويفتح لكم أبواب الرزق الحلال الوفير. 🌸\n"
        "يرجى اختيار العملية المطلوبة من الأزرار أدناه 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard(), parse_mode="Markdown")

# معالج الرسائل
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text

    if text == "⬅️ الرجوع للرئيسية":
        send_welcome(message)
        return

    # إعدادات الصباح بدون إنجليزي
    if text == "⚙️ إعدادات الصباح":
        settings_data = load_settings()
        morning_text = (
            "☀️ **صباح الرزق والبركة والسعادة يا طيب!** ☀️\n"
            "نسأل الله أن يجعل هذا اليوم يوماً مباركاً، مليئاً بالزبائن والخير الوفير لعملكم وحلالكم. 🌸✨\n\n"
            "📋 **إعدادات الصباح الحالية لمحلك:**\n"
            "🔹 سعر مثقال عيار 21: `" + f"{settings_data['mithqal_21']:,.0f}" + " دينار`\n"
            "🔹 سعر مثقال عيار 18: `" + f"{settings_data['mithqal_18']:,.0f}" + " دينار`\n"
            "🔨 أجور صياغة غرام 21: `" + f"{settings_data['labor_21']:,.0f}" + " دينار`\n"
            "🔨 أجور صياغة غرام 18: `" + f"{settings_data['labor_18']:,.0f}" + " دينار`\n"
            "💵 سعر الـ 100 دولار: `" + f"{settings_data['usd_100']:,.0f}" + " دينار`\n"
            "_____________________________\n"
            "💡 لتحديث جميع هذه الأسعار بسهولة وبدون تعقيد، يرجى الضغط على الزر أدناه وسنسألك عنها خطوة بخطوة! 👇"
        )
        markup = types.InlineKeyboardMarkup()
        btn_update = types.InlineKeyboardButton("📝 تحديث كل الأسعار", callback_data="start_update_settings")
        markup.add(btn_update)
        bot.send_message(chat_id, morning_text, reply_markup=markup, parse_mode="Markdown")
        return

    # بيع للزبون
    if text == "💰 بيع للزبون":
        user_states[chat_id] = "SELECT_SELL_TYPE"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("🟡 غرام عيار 21", "🟡 غرام عيار 18")
        markup.add("🔵 مثقال عيار 21", "🔵 مثقال عيار 18")
        markup.add("⬅️ الرجوع للرئيسية")
        
        bot.send_message(
            chat_id, 
            "💰 **بيع للزبون**\n\nيرجى اختيار العيار وطريقة الحساب المفضلة للعملية الحالية من الأزرار أدناه 👇", 
            reply_markup=markup
        )
        return

    if user_states.get(chat_id) == "SELECT_SELL_TYPE" and text in ["🟡 غرام عيار 21", "🟡 غرام عيار 18", "🔵 مثقال عيار 21", "🔵 مثقال عيار 18"]:
        user_data[chat_id] = {"type": text}
        user_states[chat_id] = "INPUT_SELL_WEIGHT"
        
        unit = "المثقال" if "مثقال" in text else "الغرام"
        bot.send_message(
            chat_id, 
            f"⚖️ لقد اخترت {text}.\n\nيرجى إرسال الوزن المطلوب بيعه للزبون (بالأرقام فقط بـ {unit}):", 
            reply_markup=back_keyboard()
        )
        return

    if user_states.get(chat_id) == "INPUT_SELL_WEIGHT":
        try:
            weight = float(text.replace(",", ""))
            user_data[chat_id]["weight"] = weight
            user_states[chat_id] = "INPUT_SELL_LABOR"
            
            settings_data = load_settings()
            current_type = user_data[chat_id]["type"]
            default_labor = settings_data["labor_21"] if "21" in current_type else settings_data["labor_18"]
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            markup.add(types.KeyboardButton(f"الصياغة الصباحية المعتادة ({default_labor:,.0f} دينار)"))
            markup.add(types.KeyboardButton("⬅️ الرجوع للرئيسية"))
            
            bot.send_message(
                chat_id,
                f"🔨 يرجى إدخال أجور صياغة الغرام الواحد بالدينار العراقي:\n\n(أو اضغط على زر الصياغة الصباحية المعتادة أدناه 👇)",
                reply_markup=markup
            )
        except ValueError:
            bot.send_message(chat_id, "⚠️ يرجى إدخال وزن صحيح بالأرقام فقط (مثال: 5.25 أو 10):")
        return

    if user_states.get(chat_id) == "INPUT_SELL_LABOR":
        settings_data = load_settings()
        current_type = user_data[chat_id]["type"]
        default_labor = settings_data["labor_21"] if "21" in current_type else settings_data["labor_18"]
        
        if "الصياغة الصباحية المعتادة" in text:
            labor = default_labor
        else:
            try:
                labor = float(text.replace(",", "").replace(" دينار", "").strip())
            except ValueError:
                bot.send_message(chat_id, "⚠️ يرجى إدخال أجور صياغة صحيحة بالأرقام أو كبس الزر بالأسفل:")
                return
        
        weight = user_data[chat_id]["weight"]
        
        if "21" in current_type:
            mithqal_price = settings_data["mithqal_21"]
        else:
            mithqal_price = settings_data["mithqal_18"]
            
        gram_price = mithqal_price / 5.0
        
        if "مثقال" in current_type:
            weight_in_grams = weight * 5.0
            display_weight = f"{weight} مثقال ({weight_in_grams:.2f} غرام)"
        else:
            weight_in_grams = weight
            display_weight = f"{weight:.2f} غرام"
            
        total_iqd = (gram_price + labor) * weight_in_grams
        usd_rate = settings_data["usd_100"]
        
        paper_and_dinar_text = calculate_paper_and_dinar(total_iqd, usd_rate)
        
        invoice_text = (
            "🧾 **فاتورة بيع ذهب للزبون**\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"🔹 العيار والطريقة: `{current_type}`\n"
            f"⚖️ الوزن المطلوب: `{display_weight}`\n"
            f"💰 سعر غرام الذهب الصافي اليوم: `{gram_price:,.0f} دينار`\n"
            f"🔨 أجور الصياغة المعتمدة للغرام: `{labor:,.0f} دينار`\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"💵 **إجمالي سعر الفاتورة بالدينار:**\n"
            f"`{total_iqd:,.0f} دينار`\n\n"
            f"💵 **صافي الحساب بالورق والدينار:**\n"
            f"👉 `{paper_and_dinar_text}`\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🌸 **الله يرزقكم ويبارك بحلالكم وتجارتكم يا رب!** ✨"
        )
        
        user_states[chat_id] = None
        bot.send_message(chat_id, invoice_text, reply_markup=main_keyboard(), parse_mode="Markdown")
        return

    # شراء من زبون
    if text == "⚖️ شراء من زبون":
        user_states[chat_id] = "SELECT_BUY_TYPE"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("🟢 غرام عيار 21", "🟢 غرام عيار 18")
        markup.add("🔵 مثقال عيار 21", "🔵 مثقال عيار 18")
        markup.add("⬅️ الرجوع للرئيسية")
        
        bot.send_message(
            chat_id, 
            "⚖️ **شراء الذهب من زبون**\n\nيرجى اختيار العيار وطريقة الحساب المفضلة للعملية الحالية من الأزرار أدناه 👇", 
            reply_markup=markup
        )
        return

    if user_states.get(chat_id) == "SELECT_BUY_TYPE" and text in ["🟢 غرام عيار 21", "🟢 غرام عيار 18", "🔵 مثقال عيار 21", "🔵 مثقال عيار 18"]:
        user_data[chat_id] = {"type": text}
        user_states[chat_id] = "INPUT_BUY_MITHQAL_PRICE"
        
        settings_data = load_settings()
        default_price = settings_data["mithqal_21"] if "21" in text else settings_data["mithqal_18"]
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(types.KeyboardButton(f"استخدام السعر الصباحي المقترح ({default_price:,.0f} دينار للمثقال)"))
        markup.add(types.KeyboardButton("⬅️ الرجوع للرئيسية"))
        
        bot.send_message(
            chat_id,
            "💰 الرجاء إدخال سعر شراء المثقال المتفق عليه حالياً بالدينار العراقي:\n\n(أو اضغط على زر السعر الصباحي المقترح أدناه 👇)",
            reply_markup=markup
        )
        return

    if user_states.get(chat_id) == "INPUT_BUY_MITHQAL_PRICE":
        settings_data = load_settings()
        current_type = user_data[chat_id]["type"]
        default_price = settings_data["mithqal_21"] if "21" in current_type else settings_data["mithqal_18"]
        
        if "السعر الصباحي المقترح" in text:
            buy_price_mithqal = default_price
        else:
            try:
                buy_price_mithqal = float(text.replace(",", "").replace(" دينار للمثقال", "").strip())
            except ValueError:
                bot.send_message(chat_id, "⚠️ يرجى إدخال السعر بشكل صحيح بالأرقام:")
                return
                
        user_data[chat_id]["buy_price_mithqal"] = buy_price_mithqal
        user_states[chat_id] = "INPUT_BUY_FEES"
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(types.KeyboardButton("0 (لا يوجد خصم صهر)"))
        markup.add(types.KeyboardButton("⬅️ الرجوع للرئيسية"))
        
        bot.send_message(
            chat_id,
            "🔥 أدخل أجور الخصم أو الصهر للغرام الواحد بالدينار العراقي:\n\n(أو اضغط على 0 بالأسفل في حال عدم وجود خصم صهر 👇)",
            reply_markup=markup
        )
        return

    if user_states.get(chat_id) == "INPUT_BUY_FEES":
        try:
            clean_text = text.split("(")[0].strip()
            fees = float(clean_text.replace(",", ""))
            user_data[chat_id]["fees"] = fees
            user_states[chat_id] = "INPUT_BUY_WEIGHT"
            
            unit = "المثقال" if "مثقال" in user_data[chat_id]["type"] else "الغرام"
            bot.send_message(
                chat_id,
                f"⚖️ يرجى إدخال الوزن المراد شراؤه من الزبون (بالأرقام بـ {unit}):",
                reply_markup=back_keyboard()
            )
        except ValueError:
            bot.send_message(chat_id, "⚠️ يرجى إدخال أجور الخصم بالأرقام فقط:")
        return

    if user_states.get(chat_id) == "INPUT_BUY_WEIGHT":
        try:
            weight = float(text.replace(",", ""))
            settings_data = load_settings()
            
            current_type = user_data[chat_id]["type"]
            buy_price_mithqal = user_data[chat_id]["buy_price_mithqal"]
            fees = user_data[chat_id]["fees"]
            
            gram_buy_price = (buy_price_mithqal / 5.0) - fees
            
            if "مثقال" in current_type:
                weight_in_grams = weight * 5.0
                display_weight = f"{weight} مثقال ({weight_in_grams:.2f} غرام)"
            else:
                weight_in_grams = weight
                display_weight = f"{weight:.2f} غرام"
                
            total_iqd = gram_buy_price * weight_in_grams
            usd_rate = settings_data["usd_100"]
            
            paper_and_dinar_text = calculate_paper_and_dinar(total_iqd, usd_rate)
            
            invoice_text = (
                "🧾 **فاتورة شراء ذهب من زبون**\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                f"🔹 العيار والطريقة: `{current_type}`\n"
                f"⚖️ الوزن المستلم: `{display_weight}`\n"
                f"💰 سعر الشراء للمثقال المعتمد: `{buy_price_mithqal:,.0f} دينار`\n"
                f"🔥 خصم أجور الصهر للغرام: `{fees:,.0f} دينار`\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                f"💵 **إجمالي المبلغ المدفوع للزبون بالدينار:**\n"
                f"`{total_iqd:,.0f} دينار`\n\n"
                f"💵 **صافي الحساب بالورق والدينار:**\n"
                f"👉 `{paper_and_dinar_text}`\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                "🌸 **تمت عملية الشراء بنجاح وشفافية مطلقة!** ✨"
            )
            
            user_states[chat_id] = None
            bot.send_message(chat_id, invoice_text, reply_markup=main_keyboard(), parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "⚠️ يرجى إدخال وزن صحيح بالأرقام فقط:")
        return

    # معالجة المعالج المتتالي لتحديث أسعار الصباح (Wizard)
    state = user_states.get(chat_id)
    if state and state.startswith("WIZARD_"):
        try:
            val = float(text.replace(",", ""))
            if val < 0:
                raise ValueError
                
            if state == "WIZARD_MITHQAL_21":
                user_data[chat_id]["mithqal_21"] = val
                user_states[chat_id] = "WIZARD_MITHQAL_18"
                bot.send_message(chat_id, "📝 **الخطوة 2/5:**\nأرسل سعر مثقال عيار 18 الجديد (بالأرقام فقط - دينار):", reply_markup=back_keyboard())
                
            elif state == "WIZARD_MITHQAL_18":
                user_data[chat_id]["mithqal_18"] = val
                user_states[chat_id] = "WIZARD_LABOR_21"
                bot.send_message(chat_id, "📝 **الخطوة 3/5:**\nأرسل أجور صياغة غرام 21 الجديدة (بالأرقام فقط - دينار):", reply_markup=back_keyboard())
                
            elif state == "WIZARD_LABOR_21":
                user_data[chat_id]["labor_21"] = val
                user_states[chat_id] = "WIZARD_LABOR_18"
                bot.send_message(chat_id, "📝 **الخطوة 4/5:**\nأرسل أجور صياغة غرام 18 الجديدة (بالأرقام فقط - دينار):", reply_markup=back_keyboard())
                
            elif state == "WIZARD_LABOR_18":
                user_data[chat_id]["labor_18"] = val
                user_states[chat_id] = "WIZARD_USD_100"
                bot.send_message(chat_id, "📝 **الخطوة 5/5 والأخيرة:**\nأرسل سعر صرف الـ 100 دولار مقابل الدينار حالياً (بالأرقام فقط - دينار):", reply_markup=back_keyboard())
                
            elif state == "WIZARD_USD_100":
                user_data[chat_id]["usd_100"] = val
                
                settings_data = load_settings()
                settings_data["mithqal_21"] = user_data[chat_id]["mithqal_21"]
                settings_data["mithqal_18"] = user_data[chat_id]["mithqal_18"]
                settings_data["labor_21"] = user_data[chat_id]["labor_21"]
                settings_data["labor_18"] = user_data[chat_id]["labor_18"]
                settings_data["usd_100"] = user_data[chat_id]["usd_100"]
                save_settings(settings_data)
                
                success_text = (
                    "🎉 **تحديث رائع وموفق!** 🎉\n"
                    "تم تحديث كافة إعدادات الأسعار الصباحية بنجاح تام وحفظها بأمان على النظام! ✅\n\n"
                    "🍀 **يا رب اجعله صباحاً مباركاً تفيض به الأرزاق الحلال، وييسر لكم به كل صعب!** ✨\n\n"
                    "البوت جاهز تماماً الآن لمباشرة حساباتكم السلسة بالأسعار الجديدة."
                )
                user_states[chat_id] = None
                bot.send_message(chat_id, success_text, reply_markup=main_keyboard(), parse_mode="Markdown")
                
        except ValueError:
            bot.send_message(chat_id, "⚠️ يرجى إدخال قيمة رقمية صحيحة فقط وبدون رموز (مثال: 450000):")
        return

    bot.send_message(chat_id, "⚠️ يرجى اختيار عملية من القائمة أدناه للبدء 👇", reply_markup=main_keyboard())

# معالجة الضغط على زر "تحديث كل الأسعار"
@bot.callback_query_handler(func=lambda call: call.data == "start_update_settings")
def callback_update_settings(call):
    chat_id = call.message.chat.id
    user_states[chat_id] = "WIZARD_MITHQAL_21"
    user_data[chat_id] = {}
    
    bot.delete_message(chat_id, call.message.message_id)
    bot.send_message(
        chat_id,
        "⚙️ **البدء بتحديث أسعار الصباح**\n\n"
        "📝 **الخطوة 1/5:**\nأرسل سعر مثقال عيار 21 الجديد (بالأرقام فقط - دينار، مثال: 450000):",
        reply_markup=back_keyboard()
    )

if __name__ == '__main__':
    print("🤖 البوت متصل الآن بنجاح ويعمل بأقصى سرعة...")
    bot.infinity_polling()
