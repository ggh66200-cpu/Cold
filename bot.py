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
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
MASTER_SUPPORT_NUMBER = os.getenv("MASTER_NUMBER", "077XXXXXXXX") # رقم الترند والماستر المعتمد للشركة

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# الحالات المبرمجة بدقة متناهية وسهلة جداً
class SetupStates(StatesGroup):
    waiting_for_m21 = State()
    waiting_for_m18 = State()
    waiting_for_usd = State()

class ProfileStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_addr = State()

class CalcStates(StatesGroup):
    waiting_for_weight = State()
    waiting_for_workmanship = State()

class InvoiceStates(StatesGroup):
    waiting_for_customer_name = State()

def get_welcome_text():
    return (
        "👑 *مرحباً بك في منظومة SMART GOLD SYSTEM الذكية* 👑\n"
        "المنصة الحسابية والترويجية الرقمية الأولى المصممة خصيصاً لأسواق الذهب العريقة في العراق 🇮🇶\n\n"
        "✨ *منظومة آرامكي تمنحك السيادة المطلقة:* ✨\n"
        "🔹 *أتمتة قانون المثقال العراقي الصارم* وعزل الأجور كلياً بدقة متناهية.\n"
        "🔹 *تطابق فوري مع السوق الموازي* (حسبة الورق والدينار الكسر بلحظات).\n"
        "🔹 *الفواتير الترويجية الفاخرة* التي تحمل اسم وشعار محلك لتعزيز هيبتك التسويقية.\n\n"
        "═══════════════════════════\n"
        "🎁 *عروض آرامكي لفترة محدودة:* \n"
        "استمتع بالباقة الذهبية المتكاملة بسعر خصم حصري: *105,000 د.ع شهرياً فقط* بدلاً من السعر الأساسي البالغ 133,000 د.ع!\n"
        "🔥 حسابكم مفعّل حالياً بـ *الفترة التجريبية المجانية (7 أيام)* لاكتساح السوق ميدانياً.\n"
        "═══════════════════════════\n"
        "👇 اختر وجهتك الحسابية وتوكل على الرزاق الحكيم:"
    )

def get_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚖️ احتساب ذهب عيار 21"), KeyboardButton(text="⚖️ احتساب ذهب عيار 18")],
            [KeyboardButton(text="📊 تعديل أسعار الصباح للمحلات"), KeyboardButton(text="🏢 تهيئة بروفايل المحل")],
            [KeyboardButton(text="🌐 تغيير اللغة / Ziman"), KeyboardButton(text="☎️ الخط الماستر لآرامكي")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await utils.add_or_update_user(message.from_user.id, message.from_user.username)
    # شاشة اختيار اللغة الفخمة للمنظومة المترابطة
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="العربية 🇮🇶", callback_data="setlang_ar"),
         InlineKeyboardButton(text="Kurdî ☀️", callback_data="setlang_ku"),
         InlineKeyboardButton(text="English 🇬🇧", callback_data="setlang_en")]
    ])
    await message.answer("👑 *WELCOME TO ARAMKY DIGITAL SOLUTIONS*\n\nيرجى اختيار لغة المنظومة المعتمدة لتخصيص واجهتكم الذكية:", parse_mode="Markdown", reply_markup=kb)

@dp.callback_query(F.data.startswith("setlang_"))
async def select_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    await utils.update_user_lang(callback.from_user.id, lang)
    await callback.message.delete()
    await callback.message.answer(get_welcome_text(), parse_mode="Markdown", reply_markup=get_main_kb())
    await callback.answer()

@dp.message(F.text == "☎️ الخط الماستر لآرامكي")
async def cmd_master_line(message: Message):
    await message.answer(
        f"🏛️ *مجموعة آرامكي للحلول الرقمية - فرع نواة الذهب* 🏛️\n\n"
        f"شركاؤنا الأفاضل، لطلب التفعيل السنوي أو الصيانة الطارئة المباشرة لخوادمكم، خط الترند الماستر متاح لخدمتكم فوراً:\n\n"
        f"📞 *الرقم الماستر المعتمد للإدارة:* `{MASTER_SUPPORT_NUMBER}`\n\n"
        f"✨ نحن نحرس أرقامكم ونصنع هيبة تجارتكم الرقمية.", parse_mode="Markdown"
    )

# معالج أسعار الصباح - خطوة بخطوة بكل سهولة وبدون تعقيد
@dp.message(F.text == "📊 تعديل أسعار الصباح للمحلات")
async def edit_morning_prices_wizard(message: Message, state: FSMContext):
    await message.answer("🏆 *إعدادات البورصة الخاصة بمحلك* 🏆\n\nيرجى إدخال سعر مثقال الذهب *عيار 21* المعتمد في سوقكم اليوم (بالدينار العراقي):")
    await state.set_state(SetupStates.waiting_for_m21)

@dp.message(SetupStates.waiting_for_m21)
async def process_m21(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ يرجى إدخال أرقام فقط بدون فواصل:")
        return
    await state.update_data(m21=float(message.text))
    await message.answer("📐 ممتاز، الآن يرجى إدخال سعر مثقال الذهب *عيار 18* المعتمد اليوم:")
    await state.set_state(SetupStates.waiting_for_m18)

@dp.message(SetupStates.waiting_for_m18)
async def process_m18(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ يرجى إدخال أرقام فقط:")
        return
    await state.update_data(m18=float(message.text))
    await message.answer("💵 أخيرًا، يرجى إدخال سعر صرف الورقة ($100) الحالي في السوق الموازي (مثال: 153500):")
    await state.set_state(SetupStates.waiting_for_usd)

@dp.message(SetupStates.waiting_for_usd)
async def process_usd(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ يرجى إدخال أرقام فقط:")
        return
    data = await state.get_data()
    await utils.update_morning_prices(message.from_user.id, data['m21'], data['m18'], float(message.text))
    await message.answer("✅ *تم تأمين وحفظ أسعار الصباح الخاصة بمحلك بنجاح!* المنظومة الحسابية متطابقة الآن مع تحديثك الشخصي بالكامل.", reply_markup=get_main_kb())
    await state.clear()

# تهيئة بروفايل المحل
@dp.message(F.text == "🏢 تهيئة بروفايل المحل")
async def profile_shop_wizard(message: Message, state: FSMContext):
    await message.answer("🏛️ *إعداد الهوية التجارية للمحل* 🏛️\n\nيرجى إدخال *اسم المحل أو الصائغ* الجاهز للطباعة بالفاتورة:")
    await state.set_state(ProfileStates.waiting_for_name)

@dp.message(ProfileStates.waiting_for_name)
async def prof_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("📞 يرجى إدخال رقم هاتف المحل الرسمي:")
    await state.set_state(ProfileStates.waiting_for_phone)

@dp.message(ProfileStates.waiting_for_phone)
async def prof_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await message.answer("📍 يرجى إدخال عنوان المحل الرسمي بالتفصيل (مثال: بغداد - سوق الكاظمية - قيصرية المعموري):")
    await state.set_state(ProfileStates.waiting_for_addr)

@dp.message(ProfileStates.waiting_for_addr)
async def prof_addr(message: Message, state: FSMContext):
    data = await state.get_data()
    await utils.update_shop_profile(message.from_user.id, data['name'], data['phone'], message.text.strip())
    await message.answer("✅ *تم بنجاح تثبيت هويتك التجارية السحابية!* فواتيرك الرقمية ستصدر بطابع ملكي يعكس فخامة اسمك بالسوق.", reply_markup=get_main_kb())
    await state.clear()

# آلية الاحتساب الذكي مع الـ 5 ثواني الفاخرة للعمليات المعقدة
@dp.message(F.text.in_(["⚖️ احتساب ذهب عيار 21", "⚖️ احتساب ذهب عيار 18"]))
async def start_gold_calculation(message: Message, state: FSMContext):
    has_sub = await utils.check_subscription(message.from_user.id)
    if not has_sub:
        await message.answer("⚠️ زميلنا المحترم، عذراً، يجب تفعيل الاشتراك السنوي أو تنشيط الفترة التجريبية عبر الخط الماستر للاستمرار.")
        return
    
    karat = 21 if "21" in message.text else 18
    await state.update_data(karat=karat)
    await message.answer(f"⚖️ يرجى إدخال الوزن الإجمالي للذهب بالجرام (عيار {karat}):")
    await state.set_state(CalcStates.waiting_for_weight)

@dp.message(CalcStates.waiting_for_weight)
async def calc_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)
        await message.answer("🛠️ يرجى إدخال أجور الصياغة المعتمدة للغرام الواحد (بالدينار العراقي):")
        await state.set_state(CalcStates.waiting_for_workmanship)
    except ValueError:
        await message.answer("❌ يرجى إدخال الوزن بشكل رقمي صحيح:")

@dp.message(CalcStates.waiting_for_workmanship)
async def calc_workmanship(message: Message, state: FSMContext):
    try:
        workmanship = float(message.text)
        data = await state.get_data()
        
        # تأثير حركة التحميل العملاقة لمدة 5 ثوانٍ لإبراز قوة وضخامة العملية الحسابية
        loading = await message.answer("⏳ جاري ربط الخادم الآمن وتطبيق قانون المثقال العراقي...")
        await asyncio.sleep(1.2)
        await loading.edit_text("⚖️ جاري تصفية الغرامات وعزل أجور الصياغة الفنية...")
        await asyncio.sleep(1.2)
        await loading.edit_text("💵 جاري احتساب أسعار الصرف وتحويل الكسور للموازين المحلية...")
        await asyncio.sleep(1.3)
        await loading.edit_text("✨ اللمسات الأخيرة للفاتورة الرقمية الفاخرة...")
        await asyncio.sleep(1.3)
        await loading.delete()
        
        user_info = await utils.get_user_data(message.from_user.id)
        mithqal_price = user_info['m21_price'] if data['karat'] == 21 else user_info['m18_price']
        usd_rate = user_info['usd_rate']
        
        gram_base, total_iqd, waraqa, remain_iqd = utils.calculate_gold(
            data['weight'], workmanship, mithqal_price, usd_rate
        )
        
        # خزن النواتج داخل الـ FSM لتلافي خطأ تخطي حدود التليجرام بالأزرار
        await state.update_data(
            res_w=data['weight'], res_k=data['karat'], res_gb=gram_base,
            res_wm=workmanship, res_iqd=total_iqd, res_war=waraqa, res_rem=remain_iqd
        )
        
        result_ui = (
            f"👑 *النتيجة الحسابية الرسمية المعتمدة* 👑\n\n"
            f"📋 العيار الاحترافي: *ذهب عيار {data['karat']}*\n"
            f"⚖️ الوزن الصافي الإجمالي: *{data['weight']} غرام*\n"
            f"📐 سعر الغرام الصافي (المثقال ÷ 5): *{int(gram_base):,} د.ع*\n"
            f"🛠️ أجور الصياغة الفنية للجرام: *{int(workmanship):,} د.ع*\n"
            f"═══════════════════════════\n\n"
            f"💰 *إجمالي الحساب بالدينار العراقي:* \n» *{int(total_iqd):,} د.ع*\n\n"
            f"💵 *حسبة السوق الموازي (الدولار والكسور):* \n» *{waraqa} ورقة* 💵 + *{int(remain_iqd):,} دينار عراقي* 🇮🇶\n"
            f"═══════════════════════════\n"
            f"💎 خوادم آرامكي - دقة وأمان وسرعة مطلقة."
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧾 تنظيم وإصدار فاتورة المحل الفاخرة", callback_data="trigger_invoice")]
        ])
        
        await message.answer(result_text=result_ui, parse_mode="Markdown", reply_markup=get_main_kb())
        await message.answer("💡 خيار إضافي متاح: يمكنك إرسال وثيقة بيع رسمية مطبوعة باسم زبونك بالضغط أدناه:", reply_markup=kb)
        
    except ValueError:
        await message.answer("❌ يرجى إدخال الأجور بشكل رقمي صحيح:")

# إطلاق الفاتورة المؤمنة بنجاح 100% وبدون أي تعليق
@dp.callback_query(F.data == "trigger_invoice")
async def start_invoice_generation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("✍️ يرجى إدخال *اسم الزبون الكريم* لإصدار وطباعة الفاتورة الرسمية باسمه:")
    await state.set_state(InvoiceStates.waiting_for_customer_name)

@dp.message(InvoiceStates.waiting_for_customer_name)
async def print_luxury_invoice(message: Message, state: FSMContext):
    customer_name = message.text.strip()
    data = await state.get_data()
    shop = await utils.get_user_data(message.from_user.id)
    
    invoice_template = (
        f"📜 *فاتورة رقمية رسمية فاخرة* 📜\n"
        f"🏛️ *المصدر العامر:* {shop['shop_name']}\n"
        f"📞 *رقم الهاتف:* {shop['shop_phone']}\n"
        f"📍 *العنوان:* {shop['shop_address']}\n"
        f"═══════════════════════════\n\n"
        f"👤 *إلى السيد/ة الكريم/ة:* {customer_name}\n"
        f"📋 الصنف: ذهب عيار {data['res_k']}\n"
        f"⚖️ الوزن الإجمالي: *{data['res_w']} غرام*\n"
        f"🛠️ أجور صياغة الجرام الواحد: *{int(data['res_wm']):,} د.ع*\n"
        f"═══════════════════════════\n\n"
        f"💰 *المجموع النهائي بالدينار:* {int(data['res_iqd']):,} د.ع\n"
        f"💵 *المجموع بنظام السوق العراقي:* {data['res_war']} ورقة + {int(data['res_rem']):,} دينار\n"
        f"═══════════════════════════\n\n"
        f"✨ مبارك لكم رزقكم الزاهر ونشكر ثقتكم بنا ✨\n\n"
        f"👑 *صيغت وتمت مراجعتها عبر منظومة SMART GOLD SYSTEM*\n"
        f"🚀 نظام أتمتة الصاغة المعتمد بالمملكة الرقمية لآرامكي: @GoldenCalc_Bot"
    )
    
    await message.answer(invoice_template, parse_mode="Markdown", reply_markup=get_main_kb())
    await state.clear()

# لوحة تحكم الإدارة (الماستر الكبيرة لشركة آرامكي)
@dp.message(Command("admin"))
async def cmd_admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 كشف وجرد الصاغة المسجلين بالنظام", callback_data="adm_users_list")]
    ])
    await message.answer("👑 *لوحة السيطرة والتحكم الاستراتيجي لشركة آرامكي:*", reply_markup=kb)

@dp.callback_query(F.data == "adm_users_list")
async def adm_list_users(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    users = await utils.db_get_all_users()
    report = "👥 *قاعدة بيانات الصاغة المسجلين بالتفصيل:* \n\n"
    for u in users:
        report += f"🆔 `{u[0]}` | 👤 @{u[1] or 'لا يوجد'} | 🛡️ {u[2]} | 📅 {u[3]}\n"
    await callback.message.answer(report, parse_mode="Markdown")
    await callback.answer()

async def main():
    await utils.init_and_refresh_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
