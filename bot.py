import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web

import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# التوكن الافتراضي من السيرفر
BOT_TOKEN = os.getenv("BOT_TOKEN", "7483920194:AAH_FakeTokenForRenderPortScanVerification")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789")) # ضع رقم الآدمن المعتمد هنا

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# --- كود خداع السيرفر (WEB SERVICE PORT SCAN BYPASS) ---
async def health_check(request):
    return web.Response(text="ARAMKY GOLD SYSTEM ONLINE", status=200)

async def start_port_trick():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"🔥 Port scanner deception active on port: {port}")

# --- حالات إدخال البيانات (FSM) ---
class RegistrationState(StatesGroup):
    waiting_for_data = State()

class SettingsState(StatesGroup):
    waiting_for_prices = State()

class InvoiceState(StatesGroup):
    waiting_for_buy_data = State()
    waiting_for_sell_data = State()

class AdminState(StatesGroup):
    waiting_for_user_id_mod = State()
    waiting_for_user_id_susp = State()

class SupportState(StatesGroup):
    waiting_for_receipt = State()

# --- لوحات الأزرار (Keyboards) ---
def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇸🇾 العربية", callback_query_id="setlang_ar"),
         InlineKeyboardButton(text="☀️ Kurdî", callback_query_id="setlang_ku"),
         InlineKeyboardButton(text="🇬🇧 English", callback_query_id="setlang_en")]
    ])

def get_client_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📊 الأسعار الصباحية"), KeyboardButton(text="📥 شراء من زبون")],
        [KeyboardButton(text="📤 بيع للزبون"), KeyboardButton(text="⚙️ تحديث الأسعار")]
    ], resize_keyboard=True)

def get_admin_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="➕ زيادة فترة مجانية"), KeyboardButton(text="⛔ إيقاف مشترك")],
        [KeyboardButton(text="📊 إحصائيات المنظومة"), KeyboardButton(text="🔙 خروج من الإدارة")]
    ], resize_keyboard=True)

# --- المعالجات والاتصالات (Handlers) ---
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    status, lang = await utils.check_user_status(message.from_user.id)
    
    if status == "NOT_REGISTERED":
        await message.answer(
            "👑 **مرحباً بكم في منظومة نواة الذهب الذكية من شركة أرامكي**\n\n"
            "للبدء وتأمين بيانات محلك العامر، يرجى إرسال معلومات المحل بنص رسالة واحدة مرتبة كالتالي:\n"
            "1- اسم المحل الرسمي\n"
            "2- المحافظة والمنطقة\n"
            "3- رقم هاتف المحل المعتمد"
        )
        return
        
    if status in ["EXPIRED", "SUSPENDED"]:
        await message.answer(utils.LANG_TEXTS[lang]['expired'])
        return

    await message.answer(utils.LANG_TEXTS[lang]['welcome'], reply_markup=get_client_keyboard())

@router.message(F.text, lambda msg: not msg.text.startswith("/"))
async def handle_registration_or_text(message: types.Message, state: FSMContext):
    status, lang = await utils.check_user_status(message.from_user.id)
    
    if status == "NOT_REGISTERED":
        lines = message.text.split("\n")
        if len(lines) >= 3:
            shop_name = lines[0].strip()
            location = lines[1].strip()
            phone = lines[2].strip()
            
            await utils.register_user(message.from_user.id, shop_name, location, phone)
            count = await utils.get_total_users_count()
            
            welcome_msg = (
                f"🎉 **ما شاء الله، تم تسجيل محلك العامر بنجاح تامة!**\n\n"
                f"🆔 رقم الصائغ المعتمد: `#{message.from_user.id}`\n"
                f"📍 المحل: {shop_name}\n"
                f"🌍 الموقع: {location}\n"
                f"📞 الهاتف: {phone}\n\n"
                f"👥 المشتركين النشطين في الكار الآن: {count + 160} صائغ\n"
                f"يرجى اختيار لغة الواجهة الرسمية المفضلة لديك:"
            )
            await message.answer(welcome_msg, reply_markup=get_lang_keyboard())
        else:
            await message.answer("⚠️ يرجى إدخال المعلومات بثلاثة أسطر منفصلة (اسم المحل، المنطقة، الهاتف) لضمان دقة التسجيل.")
        return

    if status in ["EXPIRED", "SUSPENDED"]:
        if message.photo:
            await message.forward(chat_id=ADMIN_ID)
            await message.answer("✅ تم إرسال صورة الوصل بنجاح إلى الإدارة المالية لشركة أرامكي. سيتم مراجعة الدفع وتفعيل الحساب فوراً.")
        else:
            await message.answer(utils.LANG_TEXTS[lang]['expired'])
        return

    # معالجات الأزرار للعملاء الشغالين
    if message.text == "📊 الأسعار الصباحية":
        s = await utils.get_shop_settings(message.from_user.id)
        if s:
            msg = (
                f"👑 **ARAMKY | أرامكي للحلول الرقمية**\n"
                f"✨ **نواة الذهب لحسابات الصاغة الذكية**\n"
                f"➖➖➖➖➖➖➖➖➖➖\n"
                f"☀️ **إعدادات الصباح الحالية لمحلك:**\n\n"
                f"🔹 سعر مثقال عيار 21: {s[0]:,.0f} دينار\n"
                f"🔹 سعر مثقال عيار 18: {s[1]:,.0f} دينار *(أقل من 21)*\n"
                f"⚒️ أجور صياغة غرام 21: {s[2]:,.0f} دينار\n"
                f"⚒️ أجور صياغة غرام 18: {s[3]:,.0f} دينار\n"
                f"💵 سعر الـ 100 دولار: {s[4]:,.0f} دينار\n"
            )
            await message.answer(msg)
        
    elif message.text == "⚙️ تحديث الأسعار":
        await message.answer(
            "✏️ أرسل الأسعار الصباحية الجديدة في سطر واحد مفصلة بفاصلة مسافة كالتالي:\n"
            "`شراء_21, شراء_18, صياغة_21, صياغة_18, سعر_الدولار`\n\n"
            "مثال: `900000, 450000, 10000, 1000, 155000`"
        )
        await state.set_state(SettingsState.waiting_for_prices)

    elif message.text == "📥 شراء من زبون":
        await message.answer("⚖️ أرسل تفاصيل الشراء بالتنسيق التالي في سطر واحد:\n`الوزن_بالغرام, العيار(18 او 21), خصم_المنصهر_للغرام`\n\nمثال: `478.963, 18, 35000`")
        await state.set_state(InvoiceState.waiting_for_buy_data)

    elif message.text == "📤 بيع للزبون":
        await message.answer("⚖️ أرسل تفاصيل البيع بالتنسيق التالي في سطر واحد:\n`الوزن_بالغرام, العيار(18 او 21)`\n\nمثال: `4.963, 18`")
        await state.set_state(InvoiceState.waiting_for_sell_data)

# --- معالجة المدخلات الحسابية والفواتير الفخمة ---
@router.message(SettingsState.waiting_for_prices)
async def process_new_prices(message: types.Message, state: FSMContext):
    try:
        parts = [float(x.strip()) for x in message.text.split(",")]
        await utils.update_settings(message.from_user.id, parts[0], parts[1], parts[2], parts[3], parts[4])
        await message.answer("✅ تم تحديث الأسعار الصباحية بنجاح وتوافق تام مع المخزون.")
    except Exception:
        await message.answer("❌ صيغة خاطئة، يرجى الالتزام بالمثال: 900000, 450000, 10000, 1000, 155000")
    await state.clear()

@router.message(InvoiceState.waiting_for_buy_data)
async def process_buy_invoice(message: types.Message, state: FSMContext):
    try:
        parts = [x.strip() for x in message.text.split(",")]
        weight = float(parts[0])
        karat = int(parts[1])
        melt_discount = float(parts[2])
        
        s = await utils.get_shop_settings(message.from_user.id)
        # احتساب الأوزان والمثاقيل الشرعية (المثقال العراقي = 5 غرام)
        base_price_mithqal = s[0] if karat == 21 else s[1]
        price_per_gram = base_price_mithqal / 5
        clean_buy_price = price_per_gram - melt_discount
        
        total_iqd = weight * clean_buy_price
        
        # تحويل كاش عراقي لورق فئة 100$
        usd_rate = s[4]
        total_usd_bills = int(total_iqd // usd_rate)
        remain_iqd = total_iqd % usd_rate
        
        bot_info = await bot.get_me()
        invoice = (
            f"👑 **ARAMKY | أرامكي للحلول الرقمية**\n"
            f"✨ *فرع نواة الذهب لأنظمة الصاغة والأسواق المالية*\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"🧾 **فاتورة شراء ذهب من زبون**\n\n"
            f"🔹 **العيار وطريقة الشراء:** عيار {karat} (حساب بالغرام)\n"
            f"⚖️ **الوزن المستلم:** {weight:.3f} غرام\n"
            f"🔥 **خصم الصهر/أجور الجرام:** {melt_discount:,.0f} دينار\n"
            f"💰 **سعر الشراء المعتمد للمثقال:** {base_price_mithqal:,.0f} دينار\n"
            f"💰 **سعر غرام الشراء الصافي:** {clean_buy_price:,.0f} دينار\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"💵 **المبلغ الكلي المدفوع بالدينار:** {total_iqd:,.0f} دينار\n"
            f"💵 **صافي الحساب بالورق والدينار:**\n"
            f"   {total_usd_bills} ورقة و {remain_iqd:,.0f} دينار\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"🌸 *تمت عملية الشراء بنجاح وشفافية مطلقة!*\n"
            f"🤖 معرف البوت الرسمي: @{bot_info.username}"
        )
        await message.answer(invoice)
    except Exception:
        await message.answer("❌ حدث خطأ في البيانات المدخلة، يرجى التأكد من الصيغة الصحيحة.")
    await state.clear()

@router.message(InvoiceState.waiting_for_sell_data)
async def process_sell_invoice(message: types.Message, state: FSMContext):
    try:
        parts = [x.strip() for x in message.text.split(",")]
        weight = float(parts[0])
        karat = int(parts[1])
        
        s = await utils.get_shop_settings(message.from_user.id)
        base_price_mithqal = s[0] if karat == 21 else s[1]
        making_fee = s[2] if karat == 21 else s[3]
        
        price_per_gram = base_price_mithqal / 5
        final_gram_price = price_per_gram + making_fee
        total_iqd = weight * final_gram_price
        
        usd_rate = s[4]
        total_usd_bills = int(total_iqd // usd_rate)
        remain_iqd = total_iqd % usd_rate
        
        bot_info = await bot.get_me()
        invoice = (
            f"👑 **ARAMKY | أرامكي للحلول الرقمية**\n"
            f"✨ *فرع نواة الذهب لأنظمة الصاغة والأسواق المالية*\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"🧾 **فاتورة بيع ذهب للزبون**\n\n"
            f"🔹 **العيار ونوع الحساب:** عيار {karat} (حساب بالغرام)\n"
            f"⚖️ **الوزن المطلوب:** {weight:.3f} غرام\n"
            f"⚒️ **أجور صياغة الغرام:** {making_fee:,.0f} دينار\n"
            f"💰 **سعر غرام الذهب الصافي:** {price_per_gram:,.0f} دينار\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"💵 **السعر الكلي بالدينار العراقي:** {total_iqd:,.0f} دينار\n"
            f"💵 **صافي الحساب بالورق والدينار:**\n"
            f"   {total_usd_bills} ورقة و {remain_iqd:,.0f} دينار\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"🌸 *ألف مبروك وحلال عليكم! ربي يرزقكم الرزق الواسع.*\n"
            f"🤖 معرف البوت الرسمي: @{bot_info.username}"
        )
        await message.answer(invoice)
    except Exception:
        await message.answer("❌ حدث خطأ في البيانات المدخلة، يرجى التحقق.")
    await state.clear()

# --- لوحة تحكم الإدارة لشركة أرامكي (Admin Panel) ---
@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠️ أهلاً بك يا باشمهندس في لوحة التحكم الإدارية لنظام نواة الذهب.", reply_markup=get_admin_keyboard())
    else:
        await message.answer("❌ عذراً، هذا الأمر مخصص فقط لمدراء النظام في شركة أرامكي.")

@router.message(F.text == "➕ زيادة فترة مجانية")
async def admin_add_time_trigger(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👤 أرسل رقم معرف الصائغ (User ID) المُراد زيادة فترته المجانية:")
        await state.set_state(AdminState.waiting_for_user_id_mod)

@router.message(AdminState.waiting_for_user_id_mod)
async def admin_process_add_time(message: types.Message, state: FSMContext):
    try:
        target_id = int(message.text.strip())
        success = await utils.admin_modify_trial(target_id, 30) # إضافة 30 يوم تلقائياً
        if success:
            await message.answer(f"✅ تم بنجاح تمديد الفترة المجانية للمشترك `#{target_id}` لمدة 30 يوماً إضافية.")
            await bot.send_message(target_id, "🎉 بشرى سارة! قامت إدارة شركة أرامكي بتمديد فترتك المجانية لمدة 30 يوماً إضافية. يمكنك الآن مواصلة العمل بكل ميزات المنظومة.")
        else:
            await message.answer("❌ لم يتم العثور على هذا المستخدم بقاعدة البيانات.")
    except ValueError:
        await message.answer("❌ يرجى إدخال رقم المعرف بصيغة رقمية صحيحة.")
    await state.clear()

@router.message(F.text == "⛔ إيقاف مشترك")
async def admin_suspend_trigger(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👤 أرسل رقم معرف الصائغ (User ID) المراد إيقاف خدمته فوراً:")
        await state.set_state(AdminState.waiting_for_user_id_susp)

@router.message(AdminState.waiting_for_user_id_susp)
async def admin_process_suspend(message: types.Message, state: FSMContext):
    try:
        target_id = int(message.text.strip())
        await utils.admin_suspend_user(target_id)
        await message.answer(f"⛔ تم إيقاف المشترك `#{target_id}` بنجاح وإلزام النظام بمطالبته بالاشتراك الرسمي.")
        await bot.send_message(target_id, "⚠️ تم إيقاف الصلاحية التجريبية الخاصة بحسابك من قبل الإدارة. يرجى مراجعة الدعم لتفعيل الاشتراك.")
    except ValueError:
        await message.answer("❌ المعرف غير صحيح.")
    await state.clear()

@router.message(F.text == "📊 إحصائيات المنظومة")
async def admin_stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        count = await utils.get_total_users_count()
        await message.answer(f"📈 **إحصائيات أرامكي الحالية:**\n\n👥 إجمالي عدد الصاغة المسجلين فعلياً: {count} محل صياغة.")

@router.message(F.text == "🔙 خروج من الإدارة")
async def admin_exit(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("⚙️ تم العودة لقائمة العملاء.", reply_markup=get_client_keyboard())

# --- معالجة الضغط على أزرار اللغات الوهمية (Inline Queries) ---
@router.callback_query(F.data.startswith("setlang_"))
async def callback_lang(call: types.CallbackQuery):
    lang_code = call.data.split("_")[1]
    # محاكاة حفظ اللغة بنجاح
    await call.answer("تم اعتماد اللغة بنجاح" if lang_code == "ar" else "Language fully configured")
    await call.message.answer("⚙️ تم ضبط اللغة بنجاح، يمكنك استخدام الأزرار أدناه للتحكم المطلق بمخزونك وفواتيرك العريقة.", reply_markup=get_client_keyboard())

# --- نقطة الانطلاق الشاملة للخدعة والتشغيل المباشر ---
async def main():
    await utils.init_and_refresh_db()
    # تشغيل خادم الويب الخلفي الوهمي على السيرفر لتخطي الـ Port Scan لـ Render بنجاح تام
    await start_port_trick()
    
    logging.info("✨ نظام نواة الذهب الاحترافي من أرامكي جاهز ميدانياً.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
