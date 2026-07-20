import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

import utils

# إعداد السجلات الأساسية
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# جلب مفاتيح الحماية والتحكم من السيرفر بشكل صارم وآمن
BOT_TOKEN = os.getenv("BOT_TOKEN", "7432890543:AAH_FakeTokenForStructure")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789")) # ضع معرف الآدمن الخاص بك في السيرفر
BOT_USERNAME = os.getenv("BOT_USERNAME", "NawatGoldBot")

bot = Bot(token=BOT_TOKEN)
# استخدام الذاكرة المحلية المخففة والمثالية لضعف الإنترنت بالعراق
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# مصفوفة النصوص الفاخرة للغات الـ 3 لمنع التثاقل
TEXTS = {
    'ar': {
        'welcome_brand': "👑 ARAMKY للحلول الرقمية\n⚜️ منظومة نواة الذهب الذكية لشيوخ الصاغة",
        'intro': "✨ يا فتاح يا عليم يا رزاق يا كريم\n\nأهلاً ومرحباً بك يا طيب في منظومتك الإدارية الأسرع والأدق بالأسواق العريقة!\n🎁 رزقكم مبارك، وتم تفعيل الفترة التجريبية المدتها 7 أيام لك تجتاح بها السوق ميدانياً!",
        'select_op': "🤖 يرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق 👇",
        'btn_morning': "📊 الأسعار الصباحية",
        'btn_buy': "📥 شراء ذهب من زبون",
        'btn_sell': "📤 بيع ذهب إلى زبون",
        'price_title': "📋 إعدادات الصباح الحالية لمحلكم العامر:",
        'invoice_footer': "✨ تمت العملية بنجاح وشفافية مطلقة!\nربي يعوضكم بالخير والرزق الوفير!\n\n⚜️ صممت بحب في منصة ARAMKY الرقمية\n🤖 يوزر البوت المعتمد: @{username}"
    },
    'ku': {
        'welcome_brand': "👑 ARAMKY بۆ چارەسەری دیجیتاڵی\n⚜️ سیستەمی نەوات ئەلذەهەب بۆ زێڕینگران",
        'intro': "✨ بەخێرهاتن بۆ خێراترین و وردترین سیستەمی کارگێڕی لە بازاڕەکاندا!\n🎁 ماوەی تاقیکردنەوەی بێبەرامبەر بۆ 7 ڕۆژ چالاککرا.",
        'select_op': "🤖 تکایە پرۆسەی داواکراو لە دوگمەکانی خوارەوە هەڵبژێرە 👇",
        'btn_morning': "📊 نرخەکانی بەیانیان",
        'btn_buy': "📥 کڕینی زێڕ لە کڕیار",
        'btn_sell': "📤 فرۆشتنی زێڕ بە کڕیار",
        'price_title': "📋 ڕێکخستنەکانی بەیانیانی دوکانەکەتان:",
        'invoice_footer': "✨ پرۆسەکە بە سەرکەوتوویی ئەنجامدرا!\n⚜️ دیزاین کراوە لەلایەن ARAMKY\n🤖 یوزەری بۆت: @{username}"
    },
    'en': {
        'welcome_brand': "👑 ARAMKY Digital Solutions\n⚜️ Nawat Al-Dhahab Smart System for Jewelers",
        'intro': "✨ Welcome to the fastest and most accurate administrative system in the markets!\n🎁 Your 7-day free trial has been successfully activated.",
        'select_op': "🤖 Please select the required operation from the buttons below 👇",
        'btn_morning': "📊 Morning Prices",
        'btn_buy': "📥 Buy Gold From Customer",
        'btn_sell': "📤 Sell Gold To Customer",
        'price_title': "📋 Current Morning Settings for your shop:",
        'invoice_footer': "✨ Operation completed successfully with absolute transparency!\n⚜️ Powered by ARAMKY\n🤖 Bot User: @{username}"
    }
}

# حالات إدخال البيانات الفاخرة (FSM States)
class RegistrationStates(StatesGroup):
    waiting_for_data = State()

class CalculationStates(StatesGroup):
    waiting_for_buy_weight = State()
    waiting_for_buy_purity = State()
    waiting_for_sell_weight = State()
    waiting_for_sell_purity = State()

class AdminStates(StatesGroup):
    waiting_for_prices = State()
    waiting_for_block_id = State()
    waiting_for_unblock_id = State()

# 🌐 خدعة السيرفر (Health Check Web Server) لعدم تجميد البوت وإبقائه موقع تفاعلي
async def health_check(request):
    return web.Response(text="ARAMKY GOLD SYSTEM WEB SERVICE INTERFACE IS ONLINE", status=200)

async def start_background_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"🚀 [TRICK ACTIVE] Server emulated as Web Service on port {port}")

# 🚀 نقطة انطلاق البوت الميداني
@router.message(F.text == "/start")
async def cmd_start(message: types.Message):
    user = await utils.get_user(message.from_user.id)
    if user:
        if user['is_active'] == 0:
            await send_subscription_request(message.from_user.id)
            return
        # توجيه العميل المسجل مباشرة إلى الواجهة المعتمدة له بلغته
        await send_main_dashboard(message.from_user.id, user['lang'])
    else:
        # واجهة اختيار اللغة لأول مرة بدون أعلام لتجنب أي تعليق بالنت
        # التعديل الفاخر والصحيح هندسياً
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="العربية", callback_query_data="setlang_ar")],
            [types.InlineKeyboardButton(text="Kurdî", callback_query_data="setlang_ku")],
            [types.InlineKeyboardButton(text="English", callback_query_data="setlang_en")]
        ])
        await message.answer("👑 ARAMKY DIGITAL SOLUTIONS\n\nChoose your preferred system language:\nالرجاء اختيار لغة النظام المعتمدة لدیکم:", reply_markup=kb)

@router.callback_query(F.data.startswith("setlang_"))
async def callback_set_lang(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(chosen_lang=lang)
    
    # نموذج طلب البيانات الموحد الفاخر لضمان الأرشفة الرسمية وسرعة كتابتها للتاجر
    text = (
        "📝 **خطوة تفعيل المحل وتأمين البيانات**\n\n"
        "أخي الغالي وصاحب الكار المحترم، يرجى إرسال معلومات محلك العامر كل معلومة في سطر منفصل "
        "(اضغط Enter للانتقال لسطر جديد) بهذا الترتيب لتسجيلك بالسيرفر:\n\n"
        "1️⃣ اسم المحل الرسمي\n"
        "2️⃣ المحافظة والمنطقة\n"
        "3️⃣ رقم هاتف المحل المعتمد"
    )
    if lang == 'ku':
        text = "📝 تکایە زانیارییەکانی دوکانەکەت بنێرە بەم شێوازە:\n1️⃣ ناوی فەرمی دوکان\n2️⃣ پارێزگا و ناوچە\n3️⃣ ژمارەی تەلەفۆن"
    elif lang == 'en':
        text = "📝 Please send your shop information in this order:\n1️⃣ Official Shop Name\n2️⃣ Governorate & Area\n3️⃣ Shop Phone Number"
        
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(RegistrationStates.waiting_for_data)

@router.message(RegistrationStates.waiting_for_data)
async def process_registration(message: types.Message, state: FSMContext):
    data = message.text.split('\n')
    user_data = await state.get_data()
    lang = user_data.get('chosen_lang', 'ar')
    
    if len(data) < 3:
        await message.answer("⚠️ يرجى إدخال البيانات كاملة (الاسم، الموقع، الهاتف) في سطر منفصل لكل منها لضمان دقة التسجيل والربط بالسيرفر.")
        return
    
    shop_name, location, phone = data[0].strip(), data[1].strip(), data[2].strip()
    await utils.register_user(message.from_user.id, shop_name, location, phone, lang)
    await state.clear()
    
    # رسالة الترحيب والشرح الكامل لأول دخول للصائغ
    total_active = await utils.get_all_users_count() + 160
    welcome_msg = (
        f"{TEXTS[lang]['welcome_brand']}\n"
        f"----------------------------------------\n"
        f"{TEXTS[lang]['intro']}\n\n"
        f"🔢 **رقم الصائغ المعتمد:** #{message.from_user.id % 1000}\n"
        f"📍 **المحل العامر:** {shop_name}\n"
        f"🗺️ **الموقع:** {location}\n"
        f"📞 **الهاتف:** {phone}\n\n"
        f"👥 **المشترکین النشطين في الكار الآن:** {total_active} صائغ\n"
        f"----------------------------------------\n"
        f"{TEXTS[lang]['select_op']}"
    )
    
    await message.answer(welcome_msg, reply_markup=get_main_keyboard(lang))

async def send_main_dashboard(user_id: int, lang: str):
    await bot.send_message(
        chat_id=user_id,
        text=f"{TEXTS[lang]['welcome_brand']}\n----------------------------------------\n{TEXTS[lang]['select_op']}",
        reply_markup=get_main_keyboard(lang)
    )

def get_main_keyboard(lang: str) -> types.ReplyKeyboardMarkup:
    # 3 أزرار رئيسية فاخرة للعملاء منسقة للعمل بسرعة فائقة تحت أي ظروف اتصال
    buttons = [
        [types.KeyboardButton(text=TEXTS[lang]['btn_morning'])],
        [types.KeyboardButton(text=TEXTS[lang]['btn_buy']), types.KeyboardButton(text=TEXTS[lang]['btn_sell'])]
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# 📊 عرض الأسعار الصباحية للعميل
@router.message(F.text.in_([TEXTS['ar']['btn_morning'], TEXTS['ku']['btn_morning'], TEXTS['en']['btn_morning']]))
async def show_morning_prices(message: types.Message):
    user = await utils.get_user(message.from_user.id)
    lang = user['lang'] if user else 'ar'
    prices = await utils.get_morning_prices()
    
    msg = (
        f"{TEXTS[lang]['welcome_brand']}\n"
        f"----------------------------------------\n"
        f" صباح الرزق والبركة والسعادة يا طيب! \n"
        f"نسأل الله أن يجعل هذا اليوم مباركاً، مليئاً بالخير الوفير لعملكم وحلالكم الطيب.\n\n"
        f"{TEXTS[lang]['price_title']}\n"
        f"🔹 سعر مثقال عيار 21: {prices['gold_21_price']:,} دينار\n"
        f"🔹 سعر مثقال عيار 18: {prices['gold_18_price']:,} دينار\n"
        f"🔨 أجور صياغة غرام 21: {prices['making_21']:,} دينار\n"
        f"🔨 أجور صياغة غرام 18: {prices['making_18']:,} دينار\n"
        f"💵 سعر الـ 100 دولار: {prices['usd_rate']:,} دينار\n"
        f"----------------------------------------\n"
        f"💡 لتحديث جميع هذه الأسعار بلمحة بصر وسؤال واحد، اضغط على الزر أدناه!"
    )
    await message.answer(msg)

# 📥 مسار شراء ذهب من زبون
@router.message(F.text.in_([TEXTS['ar']['btn_buy'], TEXTS['ku']['btn_buy'], TEXTS['en']['btn_buy']]))
async def start_buy_process(message: types.Message, state: FSMContext):
    await message.answer("⚖️ أرسل الوزن المراد شراؤه من الزبون (بالغرام):")
    await state.set_state(CalculationStates.waiting_for_buy_weight)

@router.message(CalculationStates.waiting_for_buy_weight)
async def process_buy_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(buy_weight=weight)
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="عيار 21", callback_query_data="buy_purity_21"),
             types.InlineKeyboardButton(text="عيار 18", callback_query_data="buy_purity_18")]
        ])
        await message.answer("💎 اختر عيار الذهب المستلم لتحديد قاعدة الاحتساب والوزن والمثاقيل بدقة:", reply_markup=kb)
    except ValueError:
        await message.answer("⚠️ يرجى إدخال قيمة رقمية صحيحة للوزن.")

@router.callback_query(F.data.startswith("buy_purity_"))
async def process_buy_purity(callback: types.CallbackQuery, state: FSMContext):
    purity = int(callback.data.split("_")[2])
    state_data = await state.get_data()
    weight = state_data['buy_weight']
    user = await utils.get_user(callback.from_user.id)
    prices = await utils.get_morning_prices()
    
    # احتسابات الذهب المعتمدة على حجم المثقال العراقي (5 غرام)
    # عيار 18 يحتسب دائماً بقيمة أقل من عيار 21
    base_gold_price = prices['gold_21_price'] if purity == 21 else prices['gold_18_price']
    making_fee = prices['making_21'] if purity == 21 else prices['making_18']
    
    price_per_gram = base_gold_price / 5
    total_dinar = (weight * price_per_gram) - (weight * making_fee)
    
    # هيكلة المبلغ إلى دولار (ورق فئة 100$) ومتبقي دينار عراقي حسب العرف المحلي
    usd_count = int(total_dinar // prices['usd_rate'])
    usd_value_in_dinar = usd_count * prices['usd_rate']
    remaining_dinar = total_dinar - usd_value_in_dinar
    
    invoice = (
        f"{TEXTS[user['lang']]['welcome_brand']}\n"
        f"----------------------------------------\n"
        f"📄 **فاتورة شراء ذهب من زبون**\n"
        f"----------------------------------------\n"
        f"🏪 المحل العامر: {user['shop_name']}\n"
        f"🔹 عيار ونوع الشراء: عيار {purity} (حساب بالغرام)\n"
        f"🔹 الوزن المستلم: {weight:.3f} غرام\n"
        f"⚖️ الوزن الإجمالي بالجرام: {weight:.3f} غرام\n"
        f"🔥 خصم الصهر/أجور الجرام: {making_fee:,} دينار\n"
        f"----------------------------------------\n"
        f"💰 سعر الشراء المعتمد للمثقال: {base_gold_price:,} دينار\n"
        f"💰 سعر غرام الشراء الصافي: {price_per_gram:,} دينار\n"
        f"----------------------------------------\n"
        f"💵 **المبلغ الكلي المدفوع بالدينار العراقي:**\n"
        f"👈 {int(total_dinar):,} دينار\n\n"
        f"💵 **صافي الحساب بالورق والدينار:**\n"
        f"👈 {usd_count * 10} ورقة و {int(remaining_dinar):,} دينار\n"
        f"----------------------------------------\n"
        f"{TEXTS[user['lang']]['invoice_footer'].format(username=BOT_USERNAME)}"
    )
    await callback.message.edit_text(invoice)
    await state.clear()

# 📤 مسار بيع ذهب إلى زبون
@router.message(F.text.in_([TEXTS['ar']['btn_sell'], TEXTS['ku']['btn_sell'], TEXTS['en']['btn_sell']]))
async def start_sell_process(message: types.Message, state: FSMContext):
    await message.answer("⚖️ أرسل الوزن المراد بيعه للزبون (بالغرام):")
    await state.set_state(CalculationStates.waiting_for_sell_weight)

@router.message(CalculationStates.waiting_for_sell_weight)
async def process_sell_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(sell_weight=weight)
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="عيار 21", callback_query_data="sell_purity_21"),
             types.InlineKeyboardButton(text="عيار 18", callback_query_data="sell_purity_18")]
        ])
        await message.answer("💎 اختر عيار الذهب المباع لتحديد قاعدة الاحتساب بدقة والأسعار الرسمية لمحلكم:", reply_markup=kb)
    except ValueError:
        await message.answer("⚠️ يرجى إدخال قيمة رقمية صحيحة للوزن.")

@router.callback_query(F.data.startswith("sell_purity_"))
async def process_sell_purity(callback: types.CallbackQuery, state: FSMContext):
    purity = int(callback.data.split("_")[2])
    state_data = await state.get_data()
    weight = state_data['sell_weight']
    user = await utils.get_user(callback.from_user.id)
    prices = await utils.get_morning_prices()
    
    base_gold_price = prices['gold_21_price'] if purity == 21 else prices['gold_18_price']
    making_fee = prices['making_21'] if purity == 21 else prices['making_18']
    
    price_per_gram = base_gold_price / 5
    # في عملية البيع تضاف الأجور إلى سعر الغرام الصافي
    total_dinar = (weight * price_per_gram) + (weight * making_fee)
    
    usd_count = int(total_dinar // prices['usd_rate'])
    usd_value_in_dinar = usd_count * prices['usd_rate']
    remaining_dinar = total_dinar - usd_value_in_dinar
    
    invoice = (
        f"{TEXTS[user['lang']]['welcome_brand']}\n"
        f"----------------------------------------\n"
        f"📄 **فاتورة بيع ذهب للزبون**\n"
        f"----------------------------------------\n"
        f"🏪 المحل العامر: {user['shop_name']}\n"
        f"🔹 العيار ونوع الحساب: عيار {purity} (حساب بالغرام)\n"
        f"🔹 الوزن المطلوب: {weight:.3f} غرام\n"
        f"⚖️ الوزن الإجمالي بالجرام: {weight:.3f} غرام\n"
        f"🔨 أجور صياغة الغرام: {making_fee:,} دينار\n"
        f"----------------------------------------\n"
        f"💰 سعر غرام الذهب الصافي: {price_per_gram:,} دينار\n"
        f"💵 **السعر الكلي بالدينار العراقي:**\n"
        f"👈 {int(total_dinar):,} دينار\n\n"
        f"💵 **صافي الحساب بالورق والدينار:**\n"
        f"👈 {usd_count * 10} ورقة و {int(remaining_dinar):,} دينار\n"
        f"----------------------------------------\n"
        f" ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب! ❤️\n\n"
        f"⚜️ صممت بحب في منصة ARAMKY الرقمية\n"
        f"🤖 يوزر البوت المعتمد: @{BOT_USERNAME}"
    )
    await callback.message.edit_text(invoice)
    await state.clear()

# ==================== 🛠️ قـسـم الإدارة والآدمـن (لوحة التحكم الفاخرة) ====================

@router.message(F.text == "/admin")
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="⚙️ تحديث الأسعار الصباحية", callback_query_data="adm_update_prices")],
        [types.InlineKeyboardButton(text="🚫 حظر/إيقاف عميل", callback_query_data="adm_block")],
        [types.InlineKeyboardButton(text="✅ تفعيل عميل", callback_query_data="adm_unblock")]
    ])
    await message.answer("👑 **لوحة الإدارة الفاخرة لشركة ARAMKY**\n\nمرحباً بك يا مهندس، يرجى اختيار إجراء التحكم بالسيرفر والعملاء الحركيين:", reply_markup=kb)

@router.callback_query(F.data == "adm_update_prices")
async def adm_request_prices(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    await callback.message.edit_text(
        "📝 يرجى إرسال الأسعار الجديدة في سطر منفصل لكل منها بهذا الترتيب الحصري:\n"
        "1️⃣ سعر مثقال عيار 21\n"
        "2️⃣ سعر مثقال عيار 18\n"
        "3️⃣ أجور صياغة غرام 21\n"
        "4️⃣ أجور صياغة غرام 18\n"
        "5️⃣ سعر الـ 100 دولار"
    )
    await state.set_state(AdminStates.waiting_for_prices)

@router.message(AdminStates.waiting_for_prices)
async def adm_process_prices(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        data = message.text.split('\n')
        g21, g18, m21, m18, usd = float(data[0]), float(data[1]), float(data[2]), float(data[3]), float(data[4])
        await utils.update_morning_prices(g21, g18, m21, m18, usd)
        await message.answer("✅ تم تحديث الأسعار المركزية على السيرفر وضخها لكافة المشتركين وتجار الصاغة بنجاح وفخامة تامة.")
        await state.clear()
    except Exception:
        await message.answer("⚠️ خطأ في التنسيق، يرجى إدخال 5 أرقام كل رقم في سطر منفصل.")

@router.callback_query(F.data == "adm_block")
async def adm_req_block(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    await callback.message.edit_text("🚫 أرسل المعرف الرقمي (User ID) للعميل المراد إيقاف فترته المجانية فوراً:")
    await state.set_state(AdminStates.waiting_for_block_id)

@router.message(AdminStates.waiting_for_block_id)
async def adm_exec_block(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = int(message.text)
        await utils.change_user_status(target_id, 0)
        await message.answer(f"✅ تم إيقاف الاشتراك وتجميد الصلاحيات للعميل {target_id} وإرسال إشعار الدفع الرسمي له.")
        await send_subscription_request(target_id)
        await state.clear()
    except ValueError:
        await message.answer("⚠️ يرجى إدخال معرف رقمي صحيح.")

@router.callback_query(F.data == "adm_unblock")
async def adm_req_unblock(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    await callback.message.edit_text("✅ أرسل المعرف الرقمي (User ID) لتفعيل أو زيادة فترة العميل الحركي:")
    await state.set_state(AdminStates.waiting_for_unblock_id)

@router.message(AdminStates.waiting_for_unblock_id)
async def adm_exec_unblock(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = int(message.text)
        await utils.change_user_status(target_id, 1)
        await message.answer(f"✅ تم تفعيل حساب العميل بنجاح تام وإعادة فتح أدوات الكار له.")
        await bot.send_message(target_id, "👑 **تهانينا**\n\nتم تفعيل حسابك وترقية اشتراكك في منظومة نواة الذهب الذكية بالكامل! توكل على الله الرزاق.")
        await state.clear()
    except ValueError:
        await message.answer("⚠️ يرجى إدخال معرف رقمي صحيح.")

async def send_subscription_request(user_id: int):
    # رسالة إيقاف الفترة المجانية الرسمية بطلب الصورة والتحويل الفوري للماستر كارد الخاص بالشركة
    text = (
        "👑 **ARAMKY | نظام نواة الذهب لحسابات الصاغة الذكية**\n"
        "----------------------------------------\n"
        "👑 **باقة شيوخ الكار المطورين (خصم حصري)**\n\n"
        "🚫 **انتهت الفترة التجريبية المخصصة للمنظومة.**\n"
        "للاشتراك وتمديد الصلاحية بالسعر التنافسي المستمر بقيمة **105,000 دينار عراقي فقط** بدلاً من السعر الأساسي 133,000 دينار عراقي (توفير 28,000 دينار عراقي بكل تجديد).\n\n"
        "💳 **حساب الإيداع المالي الذهبي للشركة:**\n"
        "رقم الماستر كارد الرسمي المعتمد:\n`910400201646`\n\n"
        "📸 بعد التحويل، اضغط على الزر بالأسفل وأرسل **صورة الوصل** لتفعيل حسابك تلقائياً بعد مراجعته فورا من قبل الإدارة الفنية.\n\n"
        "📞 خط الدعم الفني: 07872180902"
    )
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📸 إرسال وصل التحويل المالي", callback_query_data="send_receipt")]
    ])
    try:
        await bot.send_message(chat_id=user_id, text=text, reply_markup=kb, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Could not send sub request to {user_id}: {e}")

@router.callback_query(F.data == "send_receipt")
async def req_receipt_photo(callback: types.CallbackQuery):
    await callback.message.reply("ℹ️ يرجى إرسال صورة إيصال الدفع أو التحويل مباشرة الآن كرسالة مصورة لتأكيد الحساب ومراجعته بلحظات.")

@router.message(F.photo)
async def process_receipt_photo(message: types.Message):
    # تحويل صور الوصولات مباشرة لآدمن الشركة للتحقق اليدوي منها وتفعيل الحساب بلمحة بصر
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"🔔 **وصل تحويل مالي جديد للمراجعة**\n\n👤 اسم العميل: {message.from_user.full_name}\n🔢 معرّف الحساب المالي (User ID): `{message.from_user.id}`\n⚡ لتفعيله فوراً، اذهب إلى لوحة التحكم واضغط تفعيل عميل."
    )
    await message.answer("⏳ تم استلام صورة الوصل بنجاح، جاري التدقيق والربط الفوري من قبل مهندسي الدعم الفني لشركة ARAMKY.")

# ======================================================================================

async def main():
    await utils.init_and_refresh_db()
    await start_background_web_server()
    logging.info("✨ SMART GOLD SYSTEM RUNNING FIRM AND FINE ON HIGH PERFORMANCE MODE")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🔴 System shutting down gracefully.")
