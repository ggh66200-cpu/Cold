import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

# استيراد إعدادات الدوال المساعدة
import utils

# قراءة التوكن والآي دي تلقائياً من متغيرات البيئة المضافة في سيرفر Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")

# تحويل المعرفات إلى أرقام
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()]
GLOBAL_GOLD_PRICE_24 = 95000  # السعر الافتراضي لغرام الذهب عيار 24 بالدينار العراقي كمثال تنفيذي

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# الحالات الخاصة بالعمليات الحسابية المتتابعة (FSM) لمنع تداخل المدخلات
class GoldCalcStates(StatesGroup):
    waiting_for_weight = State()
    waiting_for_karat = State()
    waiting_for_workmanship = State()

class InvoiceStates(StatesGroup):
    waiting_for_details = State()

# الكيبوردات التفاعلية الأساسية
def get_main_keyboard(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=utils.LANGUAGES[lang]["calc_gold"]), KeyboardButton(text=utils.LANGUAGES[lang]["make_invoice"])],
            [KeyboardButton(text=utils.LANGUAGES[lang]["subscribe_status"]), KeyboardButton(text="🌐 Change Language / زمان")]
        ],
        resize_keyboard=True
    )

def get_lang_inline_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="العربية 🇮🇶", callback_data="set_lang_ar")],
        [InlineKeyboardButton(text="Kurdî ☀️", callback_data="set_lang_ku")],
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="set_lang_en")]
    ])

def get_karat_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="18"), KeyboardButton(text="21")],
            [KeyboardButton(text="22"), KeyboardButton(text="24")]
        ],
        resize_keyboard=True
    )

# --- معالجات الأوامر العامة للمستخدمين ---

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await utils.add_or_update_user(message.from_user.id, message.from_user.username)
    lang = await utils.get_user_lang(message.from_user.id)
    await message.answer(utils.LANGUAGES[lang]["select_lang"], reply_markup=get_lang_inline_keyboard())

@dp.callback_query(F.data.startswith("set_lang_"))
async def callback_set_lang(callback: CallbackQuery):
    selected_lang = callback.data.split("_")[2]
    await utils.set_user_lang(callback.from_user.id, selected_lang)
    await callback.answer()
    await callback.message.answer(utils.LANGUAGES[selected_lang]["welcome"], reply_markup=get_main_keyboard(selected_lang))

@dp.message(F.text == "🌐 Change Language / زمان")
async def cmd_change_lang(message: Message):
    lang = await utils.get_user_lang(message.from_user.id)
    await message.answer(utils.LANGUAGES[lang]["select_lang"], reply_markup=get_lang_inline_keyboard())

@dp.message(F.text.in_([utils.LANGUAGES["ar"]["subscribe_status"], utils.LANGUAGES["ku"]["subscribe_status"], utils.LANGUAGES["en"]["subscribe_status"]]))
async def cmd_sub_status(message: Message):
    lang = await utils.get_user_lang(message.from_user.id)
    status, end_date = await utils.get_subscription_details(message.from_user.id)
    msg = f"💳 *الحالة:* {status}\n📅 *ينتهي في:* {end_date}\n\n"
    if status != 'active':
        msg += utils.LANGUAGES[lang]["trial_msg"]
    await message.answer(msg, parse_mode="Markdown")

# --- محرك حساب الذهب الآمن (حسابات فورية بدون تعليق) ---

@dp.message(F.text.in_([utils.LANGUAGES["ar"]["calc_gold"], utils.LANGUAGES["ku"]["calc_gold"], utils.LANGUAGES["en"]["calc_gold"]]))
async def start_calc(message: Message, state: FSMContext):
    has_sub = await utils.check_subscription(message.from_user.id)
    lang = await utils.get_user_lang(message.from_user.id)
    if not has_sub:
        await message.answer(utils.LANGUAGES[lang]["no_sub"])
        return
    await message.answer(utils.LANGUAGES[lang]["enter_weight"])
    await state.set_state(GoldCalcStates.waiting_for_weight)

@dp.message(GoldCalcStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    lang = await utils.get_user_lang(message.from_user.id)
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)
        await message.answer(utils.LANGUAGES[lang]["enter_karat"], reply_markup=get_karat_keyboard())
        await state.set_state(GoldCalcStates.waiting_for_karat)
    except ValueError:
        await message.answer("❌ يرجى إدخال رقم صحيح للوزن:")

@dp.message(GoldCalcStates.waiting_for_karat)
async def process_karat(message: Message, state: FSMContext):
    lang = await utils.get_user_lang(message.from_user.id)
    try:
        karat = int(message.text)
        if karat not in [18, 21, 22, 24]:
            raise ValueError
        await state.update_data(karat=karat)
        await message.answer(utils.LANGUAGES[lang]["enter_workmanship"], reply_markup=ReplyKeyboardMarkup(keyboard=[], remove_keyboard=True))
        await state.set_state(GoldCalcStates.waiting_for_workmanship)
    except ValueError:
        await message.answer("❌ يرجى اختيار عيار صحيح من الخيارات المتاحة:")

@dp.message(GoldCalcStates.waiting_for_workmanship)
async def process_workmanship(message: Message, state: FSMContext):
    lang = await utils.get_user_lang(message.from_user.id)
    try:
        workmanship = float(message.text)
        data = await state.get_data()
        
        # تفعيل إشارة التحميل الفورية لمنع شعور المستخدم بتأخر البوت لقفل الشاشة
        loading_msg = await message.answer(utils.LANGUAGES[lang]["loading"])
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        
        base_p, work_p, final_p = utils.calculate_gold_price(
            data['weight'], data['karat'], workmanship, GLOBAL_GOLD_PRICE_24
        )
        
        result = (
            f"{utils.LANGUAGES[lang]['result_title']}"
            f"⚖️ الوزن: {data['weight']} جرام\n"
            f"👑 عيار الذهب: {data['karat']}\n"
            f"🛠 أجور الصياغة المعتمدة: {work_p:,} د.ع\n"
            f"💰 السعر الصافي التقريبي للذهب: {base_p:,} د.ع\n"
            f"---------------------------\n"
            f"🚀 إجمالي السعر النهائي للمستهلك: {final_p:,} د.ع\n\n"
            f"شركة آرامكي - الحل الذكي لصياغة الذهب 👑"
        )
        
        await loading_msg.delete()
        await message.answer(result, reply_markup=get_main_keyboard(lang))
        await state.clear()
    except ValueError:
        await message.answer("❌ يرجى إدخال قيمة صحيحة لأجور الصياغة:")

# --- نظام الفواتير الفاخرة المدمج ---

@dp.message(F.text.in_([utils.LANGUAGES["ar"]["make_invoice"], utils.LANGUAGES["ku"]["make_invoice"], utils.LANGUAGES["en"]["make_invoice"]]))
async def start_invoice(message: Message, state: FSMContext):
    has_sub = await utils.check_subscription(message.from_user.id)
    lang = await utils.get_user_lang(message.from_user.id)
    if not has_sub:
        await message.answer(utils.LANGUAGES[lang]["no_sub"])
        return
    await message.answer("✍️ يرجى إدخال تفاصيل الفاتورة بالشكل التالي حصراً لنظام الأتمتة:\n\n[اسم الزبون] - [الوزن] - [العيار] - [الصياغة]")
    await state.set_state(InvoiceStates.waiting_for_details)

@dp.message(InvoiceStates.waiting_for_details)
async def process_invoice_details(message: Message, state: FSMContext):
    lang = await utils.get_user_lang(message.from_user.id)
    try:
        parts = message.text.split("-")
        if len(parts) < 4:
            raise ValueError
        customer_name = parts[0].strip()
        weight = float(parts[1].strip())
        karat = int(parts[2].strip())
        workmanship = float(parts[3].strip())
        
        loading_msg = await message.answer(utils.LANGUAGES[lang]["loading"])
        
        _, _, final_p = utils.calculate_gold_price(weight, karat, workmanship, GLOBAL_GOLD_PRICE_24)
        
        invoice_text = (
            f"{utils.LANGUAGES[lang]['invoice_header']}\n"
            f"👤 العميل المحترم: {customer_name}\n"
            f"⚖️ وزن القطعة المشتراة: {weight} غرام\n"
            f"👑 العيار الرسمي: {karat}\n"
            f"💵 إجمالي قيمة الفاتورة المعتمدة: {final_p:,} د.ع\n"
            f"✨ شكراً لتعاملكم معنا - محلات سوق الكاظمية التجاري ✨\n"
            f"----------------------------------------\n"
            f"⚡ رقمية مدعومة من نظام ARAMKY Gold Nucleus"
        )
        
        await loading_msg.delete()
        await message.answer(invoice_text, reply_markup=get_main_keyboard(lang))
        await state.clear()
    except Exception:
        await message.answer("❌ صيغة الإدخال غير صحيحة، يرجى المحاولة مرة أخرى والالتزام بالترتيب المطلق:\nاسم الزبون - الوزن - العيار - الصياغة")

# --- لوحة التحكم الخاصة بالمشرفين (Control Panel) ---

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 إحصائيات النظام", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 بث رسالة جماعية", callback_data="admin_broadcast")]
    ])
    await message.answer("👑 مرحباً بك في لوحة تحكم مشرف نظام آرامكي الموحد:", reply_markup=kb)

@dp.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    total, active = await utils.db_get_stats()
    await callback.message.answer(f"📊 *إحصائيات البوت الحالية:*\n\n👥 عدد المستخدمين الكلي: {total}\n💎 المشتركين الفعالين: {active}", parse_mode="Markdown")
    await callback.answer()

class BroadcastState(StatesGroup):
    waiting_for_msg = State()

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.answer("📝 أرسل الآن نص الرسالة الإعلانية أو التوجيهية التي تود بثها لجميع محلات الذهب المسجلة بالسيستم:")
    await state.set_state(BroadcastState.waiting_for_msg)
    await callback.answer()

@dp.message(BroadcastState.waiting_for_msg)
async def process_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    user_ids = await utils.db_get_all_users()
    sent_count = 0
    for uid in user_ids:
        try:
            await bot.send_message(chat_id=uid, text=message.text)
            sent_count += 1
            await asyncio.sleep(0.05)  # تأخير لحماية البوت من الحظر من تيليجرام أثناء الإرسال المكثف
        except Exception:
            continue
    await message.answer(f"📢 تمت عملية البث بنجاح! تم تسليم الرسالة إلى {sent_count} مستخدم بنجاح.")
    await state.clear()

# الأوامر المباشرة للمشرف للتحكم اليدوي السريع في الاشتراكات
@dp.message(Command("activate_trial"))
async def admin_activate_trial(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        target_id = int(message.text.split()[1])
        await utils.db_activate_trial(target_id)
        await message.answer(f"✅ تم تفعيل الفترة التجريبية للمستخدم الرقمي: {target_id}")
    except Exception:
        await message.answer("⚠️ الصيغة خاطئة، استخدم: `/activate_trial [user_id]`")

@dp.message(Command("add_subscription"))
async def admin_add_subscription(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        target_id = int(message.text.split()[1])
        await utils.db_add_subscription(target_id, days=30)
        await message.answer(f"✅ تم تفعيل الاشتراك المالي المدفوع بنجاح للمستخدم: {target_id}")
    except Exception:
        await message.answer("⚠️ الصيغة خاطئة، استخدم: `/add_subscription [user_id]`")

# --- تشغيل البوت المباشر ودورة حياة النظام ---

async def main():
    await utils.init_db()  # بناء قاعدة البيانات بشكل فوري عند أول إقلاع
    print("🔥 البوت يعمل الآن بكفاءة وبدون أي مشاكل تعليق أو قفل للنظام...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
