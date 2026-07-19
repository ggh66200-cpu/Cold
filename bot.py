import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

import utils

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# مسارات الآلة الإدارية والحسابية
class GoldCalcStates(StatesGroup):
    waiting_for_weight = State()
    waiting_for_workmanship = State()

class AdminSettingsStates(StatesGroup):
    waiting_for_prices = State()
    waiting_for_user_control = State()

class ShopSetupStates(StatesGroup):
    waiting_for_details = State()

# الواجهة الرئيسية المطابقة لهوية الكار والسوق
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚖️ شراء سريع"), KeyboardButton(text="💰 بيع للزبون")],
            [KeyboardButton(text="⚙️ أسعار الصباح"), KeyboardButton(text="🏢 تهيئة بيانات المحل")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await utils.add_or_update_user(message.from_user.id, message.from_user.username)
    await message.answer(utils.WELCOME_MESSAGE, parse_mode="Markdown", reply_markup=get_main_keyboard())

@dp.message(F.text == "⚙️ أسعار الصباح")
async def cmd_morning_prices(message: Message):
    has_sub = await utils.check_subscription(message.from_user.id)
    if not has_sub:
        # رسالة التجديد الملكية الفاخرة المعتمدة
        await message.answer(
            "👑 *منظومة آرامكي للحلول الرقمية - فرع نواة الذهب* 👑\n\n"
            "زميلنا الصائغ المحترم.. نود إعلامكم بأن الفترة التجريبية المخصصة لحسابكم قد انتهت صلاحيتها الميدانية.\n"
            "حرصاً على استمرار دقة حساباتكم اليومية وتفادي أي تأخير في تنظيم فواتير محلك العامر، يرجى تجديد الاشتراك السنوي/الشهري.\n\n"
            "💳 *الباقة الذهبية المعتمدة حالياً:* \n"
            "💰 *105,000 دينار عراقي شهرياً فقط* (بدلاً من السعر الأساسي المقدر بـ 133,000 د.ع).\n\n"
            "📞 للتفعيل الفوري وتلقي كود التجديد المعتمد، يرجى التواصل مباشرة مع الإدارة الفنية لنواة الذهب.",
            parse_mode="Markdown"
        )
        return
    
    config = await utils.get_system_config()
    msg = (
        "👑 *نشرة أسعار الصباح المعتمدة لأسواق العراق:* \n\n"
        f"🏆 سعر مثقال الذهب المعتمد اليوم: *{int(config['mithqal_price']):,} د.ع*\n"
        f"💵 سعر صرف الورقة (100 دولار): *{int(config['usd_rate']):,} د.ع*\n"
        f"📐 سعر الغرام الصافي بقانون المثقال: *{int(config['mithqal_price']/5):,} د.ع*\n\n"
        "⚡ الحسابات مبرمجة ومحدثة مركزياً لضمان التطابق المطلق مع البورصة."
    )
    await message.answer(msg, parse_mode="Markdown")

@dp.message(F.text == "🏢 تهيئة بيانات المحل")
async def setup_shop(message: Message, state: FSMContext):
    await message.answer("📝 يرجى إدخال بيانات محلك العامر لتظهر بشكل رسمي وتلقائي بالفواتير، بالصيغة التالية حصراً:\n\n[اسم المحل] - [رقم الهاتف] - [العنوان الجاهز]")
    await state.set_state(ShopSetupStates.waiting_for_details)

@dp.message(ShopSetupStates.waiting_for_details)
async def save_shop_details(message: Message, state: FSMContext):
    try:
        parts = message.text.split("-")
        if len(parts) < 3: raise ValueError
        await utils.update_shop_details(message.from_user.id, parts[0].strip(), parts[1].strip(), parts[2].strip())
        await message.answer("✅ تم حفظ وتأمين بيانات المحل بنجاح! ستظهر هسة بجميع الفواتير الرقمية الصادرة عنك.", reply_markup=get_main_keyboard())
        await state.clear()
    except ValueError:
        await message.answer("❌ خطأ في الصيغة. يرجى الإدخال بالشكل التالي: اسم المحل - رقم الهاتف - العنوان")

# --- محرك العمليات الحسابية الخارق (معالجة فورية بثوانٍ) ---

@dp.message(F.text.in_(["⚖️ شراء سريع", "💰 بيع للزبون"]))
async def start_calc(message: Message, state: FSMContext):
    has_sub = await utils.check_subscription(message.from_user.id)
    if not has_sub:
        await message.answer("⚠️ عذراً، يجب تفعيل الاشتراك أو الفترة التجريبية للاستمرار في استخدام المنظومة الحسابية.")
        return
    
    calc_type = "sell" if message.text == "💰 بيع للزبون" else "buy"
    await state.update_data(calc_type=calc_type)
    await message.answer(f"⚖️ ابدأ بإدخال وزن الذهب الحالي *بالجرام*:")
    await state.set_state(GoldCalcStates.waiting_for_weight)

@dp.message(GoldCalcStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)
        
        data = await state.get_data()
        if data['calc_type'] == "buy":
            await state.update_data(workmanship=0.0)
            await execute_iraqi_calculation(message, state)
        else:
            await message.answer("🛠️ أدخل الآن أجور الصياغة المعتمدة للجرام الواحد (بالدينار العراقي):")
            await state.set_state(GoldCalcStates.waiting_for_workmanship)
    except ValueError:
        await message.answer("❌ يرجى إدخال رقم صحيح للوزن:")

@dp.message(GoldCalcStates.waiting_for_workmanship)
async def process_workmanship(message: Message, state: FSMContext):
    try:
        workmanship = float(message.text)
        await state.update_data(workmanship=workmanship)
        await execute_iraqi_calculation(message, state)
    except ValueError:
        await message.answer("❌ يرجى إدخال رقم صحيح للأجور:")

async def execute_iraqi_calculation(message: Message, state: FSMContext):
    data = await state.get_data()
    
    # محاكاة تأثير المعالجة بكسر من الثانية لجمالية الواجهة دون أي Lag حقيقي
    loading_msg = await message.answer("⏳ جاري الاحتساب وتطبيق قانون المثقال العراقي الصارم...")
    await asyncio.sleep(0.4)
    
    config = await utils.get_system_config()
    
    # استدعاء القانون الرياضي المعتمد بالسوق العراقي
    gram_base, total_iqd, waraqa, remain_iqd = utils.calculate_iraqi_gold(
        data['weight'], data['workmanship'], config['mithqal_price'], config['usd_rate']
    )
    
    op_name = "بيع للزبون" if data['calc_type'] == "sell" else "شراء سريع من الزبون"
    
    result_text = (
        f"👑 *النتيجة الحسابية الرسمية المعتمدة* 👑\n\n"
        f"📋 النوع: *{op_name}*\n"
        f"⚖️ الوزن الإجمالي: *{data['weight']} غرام*\n"
        f"📏 سعر الغرام الصافي (المثقال ÷ 5): *{int(gram_base):,} د.ع*\n"
        f"🛠️ أجور الصياغة المعتمدة للجرام: *{int(data['workmanship']):,} د.ع*\n"
        f"_______________________________\n\n"
        f"💰 *إجمالي الحساب بالدينار العراقي:* \n» *{int(total_iqd):,} د.ع*\n\n"
        f"💵 *حسبة السوق (الدولار والعراقي):* \n» *{waraqa} ورقة* 💵 + *{int(remain_iqd):,} دينار عراقي* 🇮🇶\n"
        f"_______________________________\n"
        f"💎 نظام SMART GOLD SYSTEM - سرعة وأمان مطلق."
    )
    
    await loading_msg.delete()
    
    # زر توليد الفاتورة المخير والذكي
    cb_data = f"makeinv_{data['weight']}_{int(data['workmanship'])}_{int(total_iqd)}_{waraqa}_{int(remain_iqd)}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧾 تنظيم وإصدار فاتورة المحل الفاخرة", callback_data=cb_data)]
    ])
    
    await message.answer(result_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    await message.answer("💡 خيار إضافي: يمكنك إرسال فاتورة منسقة ومطبوعة للزبون بالضغط على الزر أدناه:", reply_markup=kb)
    await state.clear()

# --- محرك الفواتير الفاخرة ذات العائد الإعلاني والتررويجي ---

@dp.callback_query(F.data.startswith("makeinv_"))
async def init_inline_invoice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    inv_parts = callback.data.split("_")
    await state.update_data(w=inv_parts[1], wm=inv_parts[2], iqd=inv_parts[3], war=inv_parts[4], rem=inv_parts[5])
    await callback.message.answer("✍️ يرجى إدخال *اسم الزبون الكريم* لإصدار وطباعة الفاتورة الرسمية:")
    await state.set_state(AdminSettingsStates.waiting_for_user_control) # استغلال حالة مؤقتة لاستقبال الاسم

@dp.message(AdminSettingsStates.waiting_for_user_control)
async def print_luxury_invoice(message: Message, state: FSMContext):
    customer_name = message.text.strip()
    data = await state.get_data()
    shop = await utils.get_shop_details(message.from_user.id)
    
    s_name = shop[0] if shop else "محلات الصائغ المعتمد"
    s_phone = shop[1] if shop else "077XXXXXXXX"
    s_addr = shop[2] if shop else "بغداد - سوق الكاظمية"
    
    invoice_template = (
        f"📜 *فاتورة رقمية رسمية فاخرة* 📜\n"
        f"🏛️ *المصدر العامر:* {s_name}\n"
        f"📞 *رقم الهاتف:* {s_phone}\n"
        f"📍 *العنوان:* {s_addr}\n"
        f"_______________________________\n\n"
        f"👤 *إلى السيد/ة الكريم/ة:* {customer_name}\n"
        f"⚖️ الوزن الصافي المشتراة: *{data['w']} غرام*\n"
        f"🛠️ احتساب صياغة الجرام: *{int(data['wm']):,} د.ع*\n"
        f"_______________________________\n\n"
        f"💰 *المجموع النهائي بالدينار:* {int(data['iqd']):,} د.ع\n"
        f"💵 *المجموع بنظام السوق العراقي:* {data['war']} ورقة + {int(data['rem']):,} دينار\n"
        f"_______________________________\n\n"
        f"✨ شكراً لثقتكم ومبارك لكم رزقكم الزاهر ✨\n\n"
        f"👑 *صيغت وتمت مراجعتها عبر منظومة SMART GOLD SYSTEM*\n"
        f"🚀 نظام أتمتة الصاغة المعتمد بالمملكة الرقمية: @GoldenCalc_Bot"
    )
    
    await message.answer(invoice_template, parse_mode="Markdown", reply_markup=get_main_keyboard())
    await state.clear()

# --- أدوات تحكم المشرف والسيطرة المطلقة العالية الجودة (Admin Control) ---

@dp.message(Command("admin"))
async def cmd_admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 تحديث أسعار الصباح والدولار", callback_data="adm_prices")],
        [InlineKeyboardButton(text="👥 كشف وجرد حسابات الصاغة", callback_data="adm_users")],
        [InlineKeyboardButton(text="🛠️ التحكم والسيطرة بحساب معين", callback_data="adm_control_user")]
    ])
    await message.answer("👑 *لوحة السيطرة والتحكم المطلق لمنظومة آرامكي:*", reply_markup=kb)

@dp.callback_query(F.data == "adm_prices")
async def adm_prices_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer("📊 أرسل الأسعار الجديدة بالترتيب التالي حصراً لتحديث المنظومة:\n\n[سعر المثقال] - [سعر صرف الورقة 100$]")
    await state.set_state(AdminSettingsStates.waiting_for_prices)
    await callback.answer()

@dp.message(AdminSettingsStates.waiting_for_prices)
async def save_morning_prices(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        parts = message.text.split("-")
        mithqal = float(parts[0].strip())
        usd = float(parts[1].strip())
        await utils.update_system_config(mithqal, usd)
        await message.answer("✅ تم تحديث أسعار الصباح وصرف الدولار مركزياً بالمنظومة بنجاح!")
        await state.clear()
    except Exception:
        await message.answer("❌ خطأ في الإدخال. يرجى الالتزام بالصيغة: سعر المثقال - سعر الورقة")

@dp.callback_query(F.data == "adm_users")
async def adm_users_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    users = await utils.db_get_all_users_full()
    report = "👥 *جرد الصاغة المسجلين بالنظام:* \n\n"
    for u in users:
        report += f"🆔 `{u[0]}` | 👤 @{u[1] or 'لا يوجد'} | 🛡️ {u[2]} | 📅 {u[3]}\n"
    await callback.message.answer(report, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "adm_control_user")
async def adm_control_user_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer(
        "🛠️ للسيطرة الفورية على أي حساب، استخدم الأوامر المباشرة التالية بسطر الأوامر:\n\n"
        "1️⃣ لتفعيل باقة صائغ مدفوعة:\n`/activate_user [user_id]`\n\n"
        "2️⃣ لإنهاء وإيقاف اشتراك صائغ فوراً:\n`/block_user [user_id]`"
    )
    await callback.answer()

@dp.message(Command("activate_user"))
async def admin_activate_action(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        uid = int(message.text.split()[1])
        await utils.db_manage_user_status(uid, "active", days=30)
        await message.answer(f"✅ تم منح الصائغ صاحب المعرف `{uid}` اشتراكاً مدفوعاً فعالاً لمدة 30 يوماً بنجاح.", parse_mode="Markdown")
    except Exception: await message.answer("الاستخدام: `/activate_user [user_id]`")

@dp.message(Command("block_user"))
async def admin_block_action(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        uid = int(message.text.split()[1])
        await utils.db_manage_user_status(uid, "expired", days=-1)
        await message.answer(f"🛑 تم إيقاف وإلغاء تنشيط قيد الصائغ `{uid}` فوراً من خوادم آرامكي.", parse_mode="Markdown")
    except Exception: await message.answer("الاستخدام: `/block_user [user_id]`")

async def main():
    # استدعاء دالة التهيئة والتصفير الشامل المكتوبة بـ utils.py عند إقلاع السيرفر
    await utils.init_and_refresh_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
