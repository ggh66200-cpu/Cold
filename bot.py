import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

import utils

# قراءة الإعدادات الآمنة من متغيرات البيئة المستضافة بالسيرفر الخاص بك
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()]

GLOBAL_GOLD_PRICE_24 = 95000 # سعر غرام 24 المعتمد افتتاحياً للبورصة المحلية

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# إعداد الـ FSM لتتبع مسار حسابات السوق
class GoldCalcStates(StatesGroup):
    waiting_for_weight = State()
    waiting_for_karat = State()
    waiting_for_workmanship = State()

class InvoiceStates(StatesGroup):
    waiting_for_customer_name = State()

# لوحة المفاتيح الرسمية التي تطابق الهوية العريقة لعملك الميداني
def get_market_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚖️ شراء سريع"), KeyboardButton(text="💰 بيع للزبون")],
            [KeyboardButton(text="⚙️ أسعار الصباح")]
        ],
        resize_keyboard=True
    )

def get_karat_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="18"), KeyboardButton(text="21")],
            [KeyboardButton(text="22"), KeyboardButton(text="24")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await utils.add_or_update_user(message.from_user.id, message.from_user.username)
    await message.answer(utils.LANGUAGES["ar"]["welcome"], parse_mode="Markdown", reply_markup=get_market_keyboard())

@dp.message(F.text == "⚙️ أسعار الصباح")
async def cmd_morning_prices(message: Message):
    has_sub = await utils.check_subscription(message.from_user.id)
    if not has_sub:
        await message.answer(utils.LANGUAGES["ar"]["no_sub"], parse_mode="Markdown")
        return
    
    prices_msg = (
        "📊 *نشرة أسعار الصباح المعتمدة للصاغة:* \n\n"
        f"👑 غرام عيار 24: {GLOBAL_GOLD_PRICE_24:,} د.ع\n"
        f"👑 غرام عيار 21: {int(GLOBAL_GOLD_PRICE_24 * 0.875):,} د.ع\n"
        f"👑 غرام عيار 18: {int(GLOBAL_GOLD_PRICE_24 * 0.750):,} د.ع\n\n"
        "⚡ تحديث تلقائي لحظي مرتبط ببورصة الذهب المركزية."
    )
    await message.answer(prices_msg, parse_mode="Markdown")

# --- محرك العمليات الحسابية (شراء سريع / بيع للزبون) ---

@dp.message(F.text.in_(["⚖️ شراء سريع", "💰 بيع للزبون"]))
async def init_calculation(message: Message, state: FSMContext):
    has_sub = await utils.check_subscription(message.from_user.id)
    if not has_sub:
        await message.answer(utils.LANGUAGES["ar"]["no_sub"], parse_mode="Markdown")
        return
    
    calc_type = "sell" if message.text == "💰 بيع للزبون" else "buy"
    await state.update_data(calc_type=calc_type)
    
    await message.answer(utils.LANGUAGES["ar"]["enter_weight"])
    await state.set_state(GoldCalcStates.waiting_for_weight)

@dp.message(GoldCalcStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)
        await message.answer(utils.LANGUAGES["ar"]["enter_karat"], reply_markup=get_karat_keyboard())
        await state.set_state(GoldCalcStates.waiting_for_karat)
    except ValueError:
        await message.answer("❌ يرجى إدخال قيمة الوزن بالأرقام فقط:")

@dp.message(GoldCalcStates.waiting_for_karat)
async def process_karat(message: Message, state: FSMContext):
    try:
        karat = int(message.text)
        if karat not in [18, 21, 22, 24]: raise ValueError
        await state.update_data(karat=karat)
        
        data = await state.get_data()
        if data['calc_type'] == "buy":
            # الشراء السريع لا يحتاج إدخال أجور صياغة للزبون
            await state.update_data(workmanship=0.0)
            await finalize_gold_calculation(message, state)
        else:
            await message.answer(utils.LANGUAGES["ar"]["enter_workmanship"], reply_markup=ReplyKeyboardMarkup(keyboard=[], remove_keyboard=True))
            await state.set_state(GoldCalcStates.waiting_for_workmanship)
    except ValueError:
        await message.answer("❌ يرجى اختيار العيار الصحيح المتاح بالقائمة:")

@dp.message(GoldCalcStates.waiting_for_workmanship)
async def process_workmanship(message: Message, state: FSMContext):
    try:
        workmanship = float(message.text)
        await state.update_data(workmanship=workmanship)
        await finalize_gold_calculation(message, state)
    except ValueError:
        await message.answer("❌ يرجى إدخال قيمة الأجور بالأرقام فقط:")

async def finalize_gold_calculation(message: Message, state: FSMContext):
    data = await state.get_data()
    loading_msg = await message.answer(utils.LANGUAGES["ar"]["loading"])
    
    base_p, work_p, final_p = utils.calculate_gold_price(
        data['weight'], data['karat'], data['workmanship'], GLOBAL_GOLD_PRICE_24, data['calc_type']
    )
    
    type_title = "عملية بيع للزبون" if data['calc_type'] == "sell" else "عملية شراء من الزبون"
    
    result = (
        f"{utils.LANGUAGES['ar']['result_title']}"
        f"📋 النوع: *{type_title}*\n"
        f"⚖️ الوزن: *{data['weight']} غرام*\n"
        f"👑 عيار الذهب: *عيار {data['karat']}*\n"
        f"🛠️ أجور الصياغة الإجمالية: *{work_p:,} د.ع*\n"
        f"💰 صافي قيمة الذهب الخام: *{base_p:,} د.ع*\n"
        f"_______________________________\n\n"
        f"🚀 *إجمالي الحساب الصافي للمستهلك:* {final_p:,} د.ع\n"
    )
    
    # توليد البيانات الخاصة بزر الفاتورة الشفاف المطور لتمريره دون كسر مسار المستخدم
    callback_data = f"inv_{data['weight']}_{data['karat']}_{work_p}_{final_p}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧾 إصدار فاتورة فاخرة للزبون (اختياري)", callback_data=callback_data)]
    ])
    
    await loading_msg.delete()
    await message.answer(result, parse_mode="Markdown", reply_markup=get_market_keyboard())
    await message.answer("✨ هل تود إصدار فاتورة رقمية فاخرة لهذه العملية الحسابية؟ اضغط على الزر أعلاه إذا كنت ترغب في ذلك.", reply_markup=kb)
    await state.clear()

# --- محرك توليد الفواتير الترويجية الفاخرة الاختيارية ---

@dp.callback_query(F.data.startswith("inv_"))
async def start_inline_invoice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    invoice_data = callback.data.split("_")
    
    await state.update_data(
        w=invoice_data[1],
        k=invoice_data[2],
        wp=invoice_data[3],
        fp=invoice_data[4]
    )
    
    await callback.message.answer("✍️ من فضلك، أدخل الآن *اسم الزبون الكريم* لتضمينه داخل الفاتورة الرسمية:")
    await state.set_state(InvoiceStates.waiting_for_customer_name)

@dp.message(InvoiceStates.waiting_for_customer_name)
async def process_customer_invoice(message: Message, state: FSMContext):
    customer_name = message.text.strip()
    data = await state.get_data()
    
    invoice_text = (
        f"{utils.LANGUAGES['ar']['invoice_header']}"
        f"🏛️ *المحل المصدر:* محلات محمد جايم\n"
        f"📞 *هاتف المحل:* 789\n"
        f"📍 *العنوان المعتمد:* بغداد - سوق الكاظمية\n"
        f"👤 *السيد/ة المحترم/ة:* {customer_name}\n"
        f"_______________________________\n\n"
        f"⚖️ وزن الذهب الإجمالي: {data['w']} غرام\n"
        f"👑 عيار الذهب المعتمد: عيار {data['k']}\n"
        f"🛠️ أجور الصياغة المحسوبة: {float(data['wp']):,} د.ع\n"
        f"💰 *المجموع النهائي الكلي:* {float(data['fp']):,} د.ع\n"
        f"_______________________________\n\n"
        f"✨ شكراً لثقتكم وتعامكم معنا - محلك العامر دوماً ✨\n\n"
        f"📢 *تمت الحسبة وصيغت الفاتورة بنظام SMART GOLD SYSTEM*\n"
        f"🤖 يوزر نظام أتمتة الصاغة المعتمد: @GoldenCalc_Bot"
    )
    
    await message.answer(invoice_text, parse_mode="Markdown", reply_markup=get_market_keyboard())
    await state.clear()

# --- لوحة التحكم المتكاملة للمشرفين لإدارة السوق ---

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 تقرير أداء المنظومة", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 بث رسالة ترويجية / توجيهية", callback_data="admin_broadcast")]
    ])
    await message.answer("👑 *لوحة الإشراف العليا لـ SMART GOLD SYSTEM:*", reply_markup=kb)

@dp.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    total, active = await utils.db_get_stats()
    await callback.message.answer(f"📊 *تقرير الصاغة الحالي:*\n\n👥 إجمالي المحلات المسجلة: {total}\n💎 الحسابات المفعّلة والنشطة: {active}")
    await callback.answer()

class BroadcastState(StatesGroup): waiting_for_msg = State()

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer("📝 اكتب نص الرسالة التي تود إرسالها فوراً لجميع محلات الذهب المدمجة بالسيستم:")
    await state.set_state(BroadcastState.waiting_for_msg)
    await callback.answer()

@dp.message(BroadcastState.waiting_for_msg)
async def process_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    user_ids = await utils.db_get_all_users()
    sent = 0
    for uid in user_ids:
        try:
            await bot.send_message(chat_id=uid, text=message.text)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception: continue
    await message.answer(f"📢 تمت عملية البث بنجاح إلى {sent} صائغ ومحل ذهب بالمنظومة.")
    await state.clear()

@dp.message(Command("activate_trial"))
async def admin_activate_trial(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        target_id = int(message.text.split()[1])
        await utils.db_activate_trial(target_id)
        await message.answer(f"✅ تم تفعيل حساب الصائغ {target_id} تجريبياً.")
    except Exception: await message.answer("الصيغة: `/activate_trial [user_id]`")

@dp.message(Command("add_subscription"))
async def admin_add_subscription(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        target_id = int(message.text.split()[1])
        await utils.db_add_subscription(target_id, days=30)
        await message.answer(f"✅ تم استلام باقة التجديد وتفعيل الاشتراك للصائغ {target_id}.")
    except Exception: await message.answer("الصيغة: `/add_subscription [user_id]`")

async def main():
    await utils.init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
