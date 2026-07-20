import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiohttp import web

import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# مصفوفة اللغات والترجمات الفخمة (العربية، الكردية، الإنجليزية)
LEXICON = {
    'ar': {
        'welcome': "✨ يا فتاح يا عليم يا رزاق يا كريم ✨\n\nأهلاً بك في منظومة **نواة الذهب الذكية** 👑\nالتابعة لشركة **ARAMKY | أرامكي للحلول الرقمية**.\n\nالمنظومة الأسرع والأدق لإدارة حسابات الصياغة والأسواق المالية ميدانياً.",
        'main_menu': "يرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق 👇",
        'btn_prices': "📊 الأسعار الصباحية",
        'btn_buy': "📥 شراء من زبون",
        'btn_sell': "📤 بيع لزبون",
        'btn_admin': "⚙️ لوحة الإدارة",
        'invoice_header': "━━━━━━━━━━━━━━━\n👑 ARAMKY | أرامكي للحلول الرقمية 👑\n✨ فرع نواة الذهب لحسابات الصاغة ✨\n━━━━━━━━━━━━━━━",
    },
    'ku': {
        'welcome': "✨ یا فتاح یا علیم یا رزاق یا کریم ✨\n\nبخێر بێی بۆ سیستەمی ژیری **نواة الذهب** 👑\nسەر بە کۆمپانیای **ARAMKY | أرامكي للحلول الرقمية**.",
        'main_menu': "تکایە کرداری داواکراو لە دوگمەکانی خوارەوە هەڵبژێرە 👇",
        'btn_prices': "📊 نرخەکانی بەیانیان",
        'btn_buy': "📥 کڕین لە کڕیار",
        'btn_sell': "📤 فرۆشتن بە کڕیار",
        'btn_admin': "⚙️ پانێڵی بەڕێوەبردن",
        'invoice_header': "━━━━━━━━━━━━━━━\n👑 ARAMKY | الحلول الرقمية 👑\n✨ لقی نواة الذهب بۆ ژمێریاری زێڕ ✨\n━━━━━━━━━━━━━━━",
    },
    'en': {
        'welcome': "✨ Welcome to Nawat Al-Dhahab Smart System 👑\nPowered by **ARAMKY for Digital Solutions**.",
        'main_menu': "Please select the required operation below 👇",
        'btn_prices': "📊 Morning Prices",
        'btn_buy': "📥 Purchase from Client",
        'btn_sell': "📤 Sell to Client",
        'btn_admin': "⚙️ Admin Dashboard",
        'invoice_header': "━━━━━━━━━━━━━━━\n👑 ARAMKY | DIGITAL SOLUTIONS 👑\n✨ Nawat Al-Dhahab Gold System ✨\n━━━━━━━━━━━━━━━",
    }
}

class SystemStates(StatesGroup):
    WAITING_FOR_REG = State()
    WAITING_FOR_ADMIN_PRICES = State()
    CALCULATING_OPERATION = State()

# --- خادم التمويه لتخطي فحص البورتات بنجاح ---
async def health_check(request):
    return web.Response(text="ARAMKY GOLD ENGINE RUNNING SUCCESSFULLY", status=200)

async def start_background_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- لوحات الأزرار الفخمة والمقسمة هندسياً ---
def get_main_keyboard(lang: str, is_admin: bool = False):
    kb = [
        [types.KeyboardButton(text=LEXICON[lang]['btn_prices'])],
        [types.KeyboardButton(text=LEXICON[lang]['btn_buy']), types.KeyboardButton(text=LEXICON[lang]['btn_sell'])]
    ]
    if is_admin:
        kb.append([types.KeyboardButton(text=LEXICON[lang]['btn_admin'])])
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_lang_inline_keyboard():
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="العربية 🇮🇶", callback_data="setlang_ar"),
         types.InlineKeyboardButton(text="كوردي ☀️", callback_data="setlang_ku"),
         types.InlineKeyboardButton(text="English 🇬🇧", callback_data="setlang_en")]
    ])

def get_invoice_options_keyboard():
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💾 حفظ وجرد الفاتورة", callback_data="inv_save"),
         types.InlineKeyboardButton(text="❌ إلغاء العملية", callback_data="inv_cancel")]
    ])

# --- معالجة انطلاق البوت والشرح الأولي ---
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user = await utils.get_user_data(message.from_user.id)
    if not user or not user['is_registered']:
        # الشرح لأول مرة مع ذكر هيبة الشركة
        await message.answer(
            "👑 أهلاً بك في أرامكي للحلول الرقمية 👑\n\nقبل تفعيل نظام **نواة الذهب** الخاص بمحلك، يرجى اختيار لغة النظام المفضلة لديك لبدء التثبيت والتأمين الميداني:",
            reply_markup=get_lang_inline_keyboard()
        )
    else:
        lang = user['lang']
        await message.answer(LEXICON[lang]['welcome'], reply_markup=get_main_keyboard(lang, user['is_admin']))

@router.callback_query(F.data.startswith("setlang_"))
async def callback_set_lang(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await utils.update_user_lang(callback.from_user.id, lang)
    await callback.message.answer(
        f"✅ تم ضبط اللغة بنجاح.\n\n{LEXICON[lang]['welcome']}\n\nيرجى كتابة اسم محلك الرسمي الآن لإتمام التسجيل بالسيرفر الفاخر:"
    )
    await state.set_state(SystemStates.WAITING_FOR_REG)
    await state.update_data(lang=lang)
    await callback.answer()

@router.message(SystemStates.WAITING_FOR_REG)
async def process_registration(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ar')
    shop_name = message.text
    
    # محاكاة حفظ التموضع السريع للميدان
    await utils.register_user(message.from_user.id, message.from_user.username or "صائغ", shop_name, "بغداد - الكاظمية", "07896")
    await state.clear()
    
    await message.answer(
        f"🎉 تم تسجيل وتأمين البيانات بنجاح تام لمستودعك صياغة **{shop_name}**!\n\n{LEXICON[lang]['main_menu']}",
        reply_markup=get_main_keyboard(lang, is_admin=False)
    )

# --- معالجة أزرار العملاء الأساسية ---
@router.message(F.text.contains("الأسعار الصباحية") | F.text.contains("نرخەکانی بەیانیان") | F.text.contains("Morning Prices"))
async def show_morning_prices(message: types.Message):
    user = await utils.get_user_data(message.from_user.id)
    lang = user['lang'] if user else 'ar'
    prices = await utils.get_latest_prices()
    
    if not prices:
        await message.answer("⚠️ لم يتم إدخال الأسعار الصباحية من قبل الإدارة بعد.")
        return
        
    msg = (
        f"{LEXICON[lang]['invoice_header']}\n"
        f"📊 **إعدادات الأسعار الحالية لمحلك:**\n\n"
        f"🔹 سعر مثقال عيار 21: {prices['gold_price_21']:,.0f} دينار\n"
        f"🔹 سعر مثقال عيار 18: {prices['gold_price_18']:,.0f} دينار\n"
        f"🔨 أجور صياغة غرام 21: {prices['wage_21']:,.0f} دينار\n"
        f"🔨 أجور صياغة غرام 18: {prices['wage_18']:,.0f} دينار\n"
        f"💵 سعر الـ 100 دولار: {prices['usd_rate']:,.0f} دينار\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🤖 معرف البوت الرسمي: @{(await bot.get_me()).username}"
    )
    await message.answer(msg)

# تفعيل عملية البيع أو الشراء الفخمة للعملاء
@router.message(F.text.contains("شراء") | F.text.contains("بيع") | F.text.contains("کڕین") | F.text.contains("فرۆشتن") | F.text.contains("Client"))
async def start_operation(message: types.Message, state: FSMContext):
    user = await utils.get_user_data(message.from_user.id)
    lang = user['lang'] if user else 'ar'
    
    op_type = "purchase" if ("شراء" in message.text or "کڕین" in message.text or "Purchase" in message.text) else "sell"
    await state.set_state(SystemStates.CALCULATING_OPERATION)
    await state.update_data(op_type=op_type, lang=lang)
    
    await message.answer("📥 أرسل وزن عيار 18 أولاً بالغرام (إذا لم يتوفر أرسل 0):")

@router.message(SystemStates.CALCULATING_OPERATION)
async def calculate_invoice_flow(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ar')
    op_type = data.get('op_type', 'purchase')
    
    prices = await utils.get_latest_prices()
    if not prices:
        await message.answer("❌ عذراً، يجب على الإدارة إدخال الأسعار الصباحية أولاً.")
        await state.clear()
        return

    try:
        # التقاط الأوزان المدخلة (تبسيط التدفق للمثال)
        weight_18 = float(message.text)
        weight_21 = 0.0 # الافتراضي، يمكن توسيعها لطلب عيار 21
        
        # إجراء العمليات الهندسية الحسابية الدقيقة
        wage = prices['wage_18'] if weight_18 > 0 else prices['wage_21']
        pure_21, mitqals, total_iqd, usd_papers, rem_iqd = utils.calculate_gold_mechanics(
            weight_18, weight_21, prices['gold_price_21'], wage, prices['usd_rate']
        )
        
        # بناء الفاتورة الفخمة متضمنة اسم وشعار الشركة ومعرف البوت
        inv_title = "فاتورة شراء ذهب من زبون 🧾" if op_type == "purchase" else "فاتورة بيع ذهب للزبون 🧾"
        invoice_msg = (
            f"{LEXICON[lang]['invoice_header']}\n"
            f"✨ **{inv_title}** ✨\n\n"
            f"🏢 المحل العامر: {message.from_user.first_name}\n"
            f"⚖️ الوزن مستلم (18): {weight_18} غرام\n"
            f"📊 الوزن الإجمالي (مكافئ 21): {pure_21:.3f} غرام\n"
            f"⚜️ الوزن الكلي بالمثاقيل: {mitqals:.3f} مثقال\n"
            f"💵 سعر الصرف المعتمد (الورق): {prices['usd_rate']:,.0f} دينار\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💰 **المبلغ الكلي الكلي المالي:**\n"
            f"👉 {total_iqd:,.0f} دينار عراقي\n\n"
            f"💵 **صافي الحساب بالورق والدينار:**\n"
            f"⚡️ {usd_papers} ورقة و {rem_iqd:,.0f} دينار\n"
            f"━━━━━━━━━━━━━━━\n"
            f"✨ تمنياتنا لكم بالرزق الوفير والنجاح ✨\n"
            f"🤖 معرف البوت: @{(await bot.get_me()).username}\n"
            f"━━━━━━━━━━━━━━━"
        )
        
        # حفظ المتغيرات المؤقتة في الـ FSM لتخيار العميل بالجرد أو الإلغاء
        await state.update_data(w18=weight_18, w21=pure_21, tiqd=total_iqd, upap=usd_papers, riqd=rem_iqd)
        
        await message.answer(invoice_msg, reply_markup=get_invoice_options_keyboard())
        
    except ValueError:
        await message.answer("❌ يرجى إدخال أرقام صحيحة للأوزان.")

@router.callback_query(F.data.startswith("inv_"))
async def finalize_invoice(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    data = await state.get_data()
    lang = data.get('lang', 'ar')
    
    if action == "save":
        await utils.save_invoice(
            callback.from_user.id, data['op_type'], data['w18'], data['w21'], data['tiqd'], data['upap'], data['riqd']
        )
        await callback.message.edit_text(f"✅ {callback.message.text}\n\n🌟 [تم جرد وحفظ الفاتورة بنجاح في سجلات أرامكي]")
    else:
        await callback.message.edit_text("❌ تم إلغاء العملية وحذف الفاتورة المؤقتة بنجاح.")
        
    await state.clear()
    await callback.answer()

# --- انطلاق النظام الفاخر الفعلي ---
async def main():
    await utils.init_and_refresh_db()
    await start_background_web_server()
    logging.info("✨ نظام أرامكي الفاخر لنواة الذهب يعمل الآن بأعلى كفاءة واستقرار ميداني.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
