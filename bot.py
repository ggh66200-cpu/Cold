import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

import utils

logging.basicConfig(level=logging.INFO)

# توكن البوت والآدمن من السيرفر
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 123456789)) # ضع الآي دي الخاص بك كمدير للشركة

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

class RegistrationState(StatesGroup):
    waiting_for_data = State()

class AdminState(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_days = State()

# --- خادم التمويه لتخطي فحص البورت لـ Render ---
async def health_check(request):
    return web.Response(text="ARAMKY GOLD SYSTEM ACTIVE", status=200)

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- كيبورد اختيار اللغة الفخم ---
def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇸🇾 العربية", callback_data="setlang_ar")],
        [InlineKeyboardButton(text="☀️ Kurdî", callback_data="setlang_ku")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en")]
    ])

# --- كيبورد العملاء الـ 3 المعتمد الفاخر ---
def get_client_keyboard(lang):
    if lang == 'ku':
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📊 نرخەکانی بەیانی"), KeyboardButton(text="📥 کڕین لە کڕیار")],
            [KeyboardButton(text="📤 فرۆشتن بە کڕیار")]
        ], resize_keyboard=True)
    elif lang == 'en':
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📊 Morning Prices"), KeyboardButton(text="📥 Buy from Client")],
            [KeyboardButton(text="📤 Sell to Client")]
        ], resize_keyboard=True)
    else:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📊 الأسعار الصباحية"), KeyboardButton(text="📥 شراء من زبون")],
            [KeyboardButton(text="📤 بيع للزبون")]
        ], resize_keyboard=True)

# --- كيبورد التحكم الخاص بالآدمن (إدارة الشقة) ---
def get_admin_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛑 إيقاف الفترة المجانية"), KeyboardButton(text="➕ زيادة الفترة المجانية")],
        [KeyboardButton(text="📊 إحصائيات المنظومة")]
    ], resize_keyboard=True)

# --- بداية الدخول والنظام ---
@router.message(Command("start"))
async def start_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("⚙️ أهلاً بك يا باشمهندس في لوحة إدارة شركة ARAMKY للحلول الرقمية.", reply_markup=get_admin_keyboard())
        return
        
    user = await utils.get_user(message.from_user.id)
    if not user:
        await message.answer("💎 مرحبا بك في منظومة نواة الذهب الذكية من ARAMKY.\nيرجى اختيار اللغة المفضلة لبدء التأسيس الرسمي الفاخر:", reply_markup=get_lang_keyboard())
    else:
        is_valid, status = await utils.check_trial(message.from_user.id)
        if is_valid:
            await message.answer(utils.INTRO_TEXTS[user['lang']], reply_markup=get_client_keyboard(user['lang']))
        else:
            await handle_expired_status(message, status)

async def handle_expired_status(message: types.Message, status):
    if status in ["expired", "suspended"]:
        text = (
            "⚠️ **إشعار رسمي من شركة أرامكي للحلول الرقمية** ⚠️\n\n"
            "عزيزي صاحب الكار المحترم، لقد انتهت الفترة التجريبية المخصصة للمنظومة الذكية الخاصة بمحلك.\n"
            "للاستمرار بالتمتع بباقة شيوخ الكار المطورة وتمديد الصلاحية بالسعر التنافسي (105,000 دينار عراقي فقط بدلاً من 133,000 دينار).\n\n"
            "💳 **رقم الماستر كارد الرسمي المعتمد للشركة:**\n`910400201646`\n\n"
            "📸 بعد التحويل، يرجى إرسال صورة الوصل هنا فوراً ليتم تدقيقها وتفعيل حسابك تلقائياً من الإدارة الفنية."
        )
        await message.answer(text, parse_mode="Markdown")

@router.callback_query(F.data.startswith("setlang_"))
async def set_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    await callback.message.answer(
        "📝 خطوة تفعيل المحل وتأمين البيانات رسميّاً:\n"
        "الرجاء إرسال معلومات محلك العامر بالترتيب التالي وفي رسالة واحدة:\n"
        "1- اسم المحل الرسمي\n"
        "2- المحافظة والمنطقة\n"
        "3- رقم هاتف المحل المعتمد"
    )
    await state.set_state(RegistrationState.waiting_for_data)
    await callback.answer()

@router.message(RegistrationState.waiting_for_data)
async def process_registration(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ar')
    lines = message.text.split('\n')
    
    shop_name = lines[0] if len(lines) > 0 else "محلك العامر"
    location = lines[1] if len(lines) > 1 else "العراق"
    phone = lines[2] if len(lines) > 2 else message.from_user.id
    
    await utils.register_user(message.from_user.id, shop_name, location, phone, lang)
    await state.clear()
    
    await message.answer("✨ تم تسجيل محلك بنجاح وتأمين خط الاتصال بالسيرفر الفاخر!", reply_markup=get_client_keyboard(lang))
    await message.answer(utils.INTRO_TEXTS[lang], reply_markup=get_client_keyboard(lang))

# --- معالجة طلبات الأزرار الفخمة للعملاء (شراء/بيع/أسعار) ---
@router.message(F.text.in_(["📊 الأسعار الصباحية", "📊 نرخەکانی بەیانی", "📊 Morning Prices"]))
async def morning_prices_flow(message: types.Message):
    user = await utils.get_user(message.from_user.id)
    # فخامة استدعاء الأسعار الاختيارية للعميل
    await message.answer(
        f"💎 **ARAMKY | فرع نواة الذهب لأجود الحسابات**\n\n"
        f"🏪 المحل العامر: {user['shop_name']}\n"
        f"📍 الموقع الإداري الميداني: {user['location']}\n\n"
        f"📊 إعدادات الأسعار الحالية لمحلك:\n"
        f"🔹 سعر مثقال عيار 21: 900,000 دينار\n"
        f"🔹 سعر مثقال عيار 18: 450,000 دينار (محسوب بأقل من عيار 21)\n"
        f"🔸 أجور صياغة غرام 21: 10,000 دينار\n"
        f"🔸 أجور صياغة غرام 18: 1,000 دينار\n"
        f"💵 سعر الـ 100 دولار المعتمد: 155,000 دينار\n\n"
        f"💡 لتحديث أسعارك الصباحية الاختيارية بأي وقت، أرسل الأسعار الجديدة فوراً.",
        parse_mode="Markdown"
    )

@router.message(F.text.in_(["📥 شراء من زبون", "📥 کڕین لە کڕیار", "📥 Buy from Client"]))
async def buy_gold_flow(message: types.Message):
    user = await utils.get_user(message.from_user.id)
    # الفاتورة المنتسقة والفخمة التي تعكس اسم الشركة والبوت للزبون
    invoice_template = (
        "💎 **ARAMKY | أرامكي للحلول الرقمية**\n"
        "⚜️ **نواة الذهب لأنظمة الصاغة والأسواق المالية**\n"
        "🤖 يوزر البوت المعتمد: @SmartGoldSystem_Bot\n"
        "----------------------------------------\n"
        f"📄 **فاتورة شراء ذهب من زبون**\n\n"
        f"🏪 المحل العامر: {user['shop_name']}\n"
        f"⚖️ العيار وطريقة الشراء: عيار 18 (حساب بالغرام)\n"
        f"⚖️ الوزن المستلم: 478.963 غرام\n"
        f"⚖️ الوزن الإجمالي بالجرام: 478.963 غرام\n"
        f"🔥 خصم الصهر/أجور الجرام: 35,000 دينار\n"
        "----------------------------------------\n"
        f"💰 سعر الشراء المعتمد للمثقال: 900,000 دينار\n"
        f"💰 سعر غرام الشراء الصافي: 145,000 دينار\n"
        "----------------------------------------\n"
        f"💵 **المبلغ الكلي المدفوع بالدينار العراقي:**\n"
        f"👉 69,449,635 دينار عراقياً\n\n"
        f"💵 **صافي الحساب بالورق والدينار:**\n"
        f"👉 446 ورقة فئة (100$) و 96,635 دينار\n"
        "----------------------------------------\n"
        "🌸 تمت عملية الشراء بنجاح وشفافية مطلقة من خلال منظومتنا الذكية! ربي يعوضكم بالخير والرزق الوفير! ✨"
    )
    await message.answer(invoice_template, parse_mode="Markdown")

@router.message(F.text.in_(["📤 بيع للزبون", "📤 فرۆشتن بە کڕیار", "📤 Sell to Client"]))
async def sell_gold_flow(message: types.Message):
    user = await utils.get_user(message.from_user.id)
    invoice_template = (
        "💎 **ARAMKY | أرامكي للحلول الرقمية**\n"
        "⚜️ **نواة الذهب لأنظمة الصاغة والأسواق المالية**\n"
        "🤖 يوزر البوت المعتمد: @SmartGoldSystem_Bot\n"
        "----------------------------------------\n"
        f"📄 **فاتورة بيع ذهب للزبون**\n\n"
        f"🏪 المحل العامر: {user['shop_name']}\n"
        f"⚖️ العيار ونوع الحساب: عيار 18 (حساب بالغرام)\n"
        f"⚖️ الوزن المطلوب: 4.963 غرام\n"
        f"⚖️ الوزن الإجمالي بالجرام: 4.963 غرام\n"
        f"🪚 أجور صياغة الغرام: 1,000 دينار\n"
        "----------------------------------------\n"
        f"💰 سعر غرام الذهب الصافي: 90,000 دينار\n"
        f"💵 **السعر الكلي بالدينار العراقي:**\n"
        f"👉 451,633 دينار\n\n"
        f"💵 **صافي الحساب بالورق والدينار:**\n"
        f"👉 2 ورقة فئة (100$) و 141,633 دينار\n"
        "----------------------------------------\n"
        "🌸 ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب! ✨"
    )
    await message.answer(invoice_template, parse_mode="Markdown")

# --- إدارة الآدمن (إيقاف وتمديد الحسابات للشركة مع معالجة الصورة المرفوعة) ---
@router.message(F.text == "🛑 إيقاف الفترة المجانية", F.from_user.id == ADMIN_ID)
async def admin_suspend_trigger(message: types.Message, state: FSMContext):
    await message.answer("👤 أرسل رقم (User ID) الخاص بالعميل المراد إيقاف خدمته فوراً:")
    await state.set_state(AdminState.waiting_for_user_id)

@router.message(AdminState.waiting_for_user_id)
async def admin_process_suspend(message: types.Message, state: FSMContext):
    try:
        target_uid = int(message.text)
        async with aiosqlite.connect(utils.DB_NAME) as db:
            await db.execute("UPDATE users SET is_active = 0 WHERE user_id = ?", (target_uid,))
            await db.commit()
        await message.answer(f"🔒 تم إيقاف الخدمة بنجاح عن العميل ذو المعرف {target_uid}. سيُطلب منه الاشتراك رسمياً عند المحاولة.")
        await state.clear()
    except:
        await message.answer("⚠️ عذراً، يرجى إدخال معرف رقمي صحيح.")

@router.message(F.photo)
async def handle_incoming_receipt(message: types.Message):
    # استقبال صورة الوصل الميداني من الصاغة لإرسالها للآدمن فوراً للتدقيق والتفعيل
    await message.answer("🔄 تم استلام صورة الوصل بنجاح، يرجى الانتظار لحين تأكيد التحويل المالي من قسم الحسابات الفنية لشركة أرامكي.")
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"🔔 **وصل تحويل جديد للمراجعة الميدانية:**\n\n👤 المرسل (ID): `{message.from_user.id}`\n🏪 الاسم: {message.from_user.full_name}",
        parse_mode="Markdown"
    )

async def main():
    await utils.init_and_refresh_db()
    await start_web_server()
    logging.info("✨ نظام نواة الذهب بأزرار الفخامة وجرد الملفات الثلاثية شغال الآن.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
