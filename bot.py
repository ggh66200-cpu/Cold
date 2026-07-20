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
MASTER_SUPPORT = os.getenv("MASTER_NUMBER", "077XXXXXXXX") # رقم الترند والماستر المعتمد

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# فئات الحالات المنسقة لسهولة العمل وإلغاء العمليات
class RegistrationFlow(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()

class UnifiedMorningStates(StatesGroup):
    waiting_for_all_configs = State()

class SellOperationStates(StatesGroup):
    waiting_for_weight = State()

class BuyOperationStates(StatesGroup):
    waiting_for_buy_data = State()

class InvoiceFlowStates(StatesGroup):
    waiting_for_client_name = State()

class AdminPanelStates(StatesGroup):
    waiting_for_target_user = State()
    waiting_for_broadcast_msg = State()
    waiting_for_global_trial = State()

# كيبورد إلغاء العمليات الموحد
def get_cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ إلغاء العملية العودة للملف")]],
        resize_keyboard=True
    )

# الكيبورد الرئيسي الذكي والمبسط
def get_dashboard_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 ضبط أسعار الصباح الموحدة")],
            [KeyboardButton(text="💰 عملية بيع لزبون محلك"), KeyboardButton(text="⚖️ عملية شراء ذهب من زبون")],
            [KeyboardButton(text="🌐 اللغات / Ziman"), KeyboardButton(text="👑 لوحة تحكم الماستر")]
        ],
        resize_keyboard=True
    )

# 1. بداية التشغيل واختيار اللغات الجميل المبدع
@dp.message(Command("start"))
async def start_nexus_system(message: Message):
    await utils.add_or_update_user(message.from_user.id, message.from_user.username)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="العربية 🇮🇶", callback_data="lang_ar"),
         InlineKeyboardButton(text="Kurdî ☀️", callback_data="lang_ku"),
         InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")]
    ])
    
    await message.answer(
        "✨ *ARAMKY DIGITAL SOLUTIONS • GOLD NUCLEUS BRANCH* ✨\n"
        "═══════════════════════════════\n"
        "🤝 أهلاً بك في المنظومة الحسابية الأقوى والأفخم في أسواق الصاغة العراقية.\n"
        "يرجى اختيار لغة الواجهة الذكية لبدء التهيئة الفورية:\n"
        "Please select your system language to launch setup:",
        parse_mode="Markdown",
        reply_markup=kb
    )

# 2. إطلاق رسالة الشركة المثبتة وبدء استمارة التسجيل
@dp.callback_query(F.data.startswith("lang_"))
async def on_lang_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    
    trial_str = await utils.admin_get_global_trial_string()
    
    welcome_corporate = (
        "🏛️ *منظومة SMART GOLD SYSTEM لإدارة محلات الصياغة* 🏛️\n"
        f"قادمة إليكم من *شركة آرامكي للحلول الرقمية - فرع نواة الذهب*.\n"
        "═══════════════════════════════\n"
        "🛡️ *رسالة وتعهد المنظومة الملكية:*\n"
        "نحن هنا لنحرس أموالك، نؤتمت حساباتك بقانون المثقال العراقي الصارم الصافي، ونمنح تجارتك الميدانية هيبة رقمية أمام زبائنك، متخطين بالكامل مشاكل ضعف الإنترنت في العراق.\n\n"
        f"📞 *خط الطوارئ والدعم الماستر الفوري للشركة:* `{MASTER_SUPPORT}`\n"
        f"🎁 *هدية الانضمام:* لقد تم منح حسابكم فترة تجريبية مجانية مدتها *({trial_str})* بكامل الصلاحيات الفاخرة!\n"
        "═══════════════════════════════\n"
        "📋 *استمارة الانتساب الرقمية لمحلك العامر:*\n"
        "ابدأ الآن بكتابة *[اسم مكتب الصياغة أو المحل الخاص بك]* ليتم اعتماده رسمياً برأس الفاتورة الفاخرة:"
    )
    
    await callback.message.answer(welcome_corporate, parse_mode="Markdown")
    await state.set_state(RegistrationFlow.waiting_for_name)

@dp.message(RegistrationFlow.waiting_for_name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(shop_name=message.text.strip())
    await message.answer("📍 *عاش دستك.. هسة أرسل عنوان المحل بالتفصيل والوصف المميز* (مثال: بغداد - الكاظمية - سوق الذهب داخل القيصرية):")
    await state.set_state(RegistrationFlow.waiting_for_address)

@dp.message(RegistrationFlow.waiting_for_address)
async def reg_address(message: Message, state: FSMContext):
    await state.update_data(shop_address=message.text.strip())
    await message.answer("📞 *أحسنت، خطوتك الأخيرة بالاستمارة:* يرجى إرسال رقم الهاتف المعتمد للمحل لتواصل الزبائن:")
    await state.set_state(RegistrationFlow.waiting_for_phone)

@dp.message(RegistrationFlow.waiting_for_phone)
async def reg_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    await utils.update_shop_profile(message.from_user.id, data['shop_name'], message.text.strip(), data['shop_address'])
    
    # رسالة معسلة بعد ملء البيانات تفتح النفس وتظهر بعدها الأزرار
    success_msg = (
        f"🎉 *يا فتاح يا عليم يا رزاق يا كريم* 🎉\n"
        f"مبارك انضمام محلك العامر *({data['shop_name']})* إلى منصة الصاغة الكبرى.\n"
        f"تم تأمين بروفايلك الرقمي وربطه بخوادم السحابة بنجاح تام.\n\n"
        f"⬇️ هسة انفتحت إلك لوحة التحكم الذهبية الكاملة بالأسفل. توكل على الرزاق وابدأ العمل ومنافسة السوق!"
    )
    await message.answer(success_msg, parse_mode="Markdown", reply_markup=get_dashboard_kb())
    await state.clear()

# ميزة إلغاء العمليات للعودة للملف
@dp.message(F.text == "❌ إلغاء العملية العودة للملف")
async def cancel_any_operation(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🛎️ تم إلغاء العملية الجارية فوراً وإعادتك للملف الرئيسي للمنظومة. محلك جاهز لأي أمر جديد ✨", reply_markup=get_dashboard_kb())

# 3. إعدادات الصباح الموحدة - تتعدل مرة واحدة وبصيغة منسقة وبسيطة جداً
@dp.message(F.text == "📊 ضبط أسعار الصباح الموحدة")
async def unified_morning_prompt(message: Message, state: FSMContext):
    user_info = await utils.get_user_data(message.from_user.id)
    prompt_text = (
        "📊 *غرفة إدارة أسعار الصباح الموحدة لمشغلك* 📊\n"
        "═══════════════════════════════\n"
        "يرجى إدخال أسعار البورصة وأجور الصياغة المعتمدة في محلك لمرة واحدة هذا الصباح، بالترتيب التالي مفصلةً بـ (فراغ أو مسافة) وبسطر واحد حصراً:\n\n"
        "`[سعر مثقال 21] [سعر مثقال 18] [أجور صياغة 21] [أجور صياغة 18] [سعر الورقة 100$]`\n\n"
        "💡 *مثال توضيحي دقيق للإدخال:* \n"
        "`480000 410000 10000 8000 153500`\n"
        "═══════════════════════════════\n"
        "📋 *القيم الحالية المحفوظة بنظامك:* \n"
        f"• سعر مثقال 21: {int(user_info['m21_price']):,} د.ع\n"
        f"• سعر مثقال 18: {int(user_info['m18_price']):,} د.ع\n"
        f"• أجور الغرام 21: {int(user_info['w21_charge']):,} د.ع\n"
        f"• أجور الغرام 18: {int(user_info['w18_charge']):,} د.ع\n"
        f"• سعر الصرف للورقة: {int(user_info['usd_rate']):,} د.ع"
    )
    await message.answer(prompt_text, parse_mode="Markdown", reply_markup=get_cancel_kb())
    await state.set_state(UnifiedMorningStates.waiting_for_all_configs)

@dp.message(UnifiedMorningStates.waiting_for_all_configs)
async def process_unified_morning(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء العملية العودة للملف": return
    try:
        parts = message.text.split()
        if len(parts) < 5: raise ValueError
        m21, m18, w21, w18, usd = map(float, parts)
        
        await utils.update_morning_config(message.from_user.id, m21, m18, w21, w18, usd)
        await message.answer("✅ *تم تثبيت بورصة الصباح الموحدة الخاصة بمحلك بنجاح!* حسابات البيع والشراء أصبحت متطابقة مع موازينك الآن كلياً وبأعلى دقة.", reply_markup=get_dashboard_kb())
        await state.clear()
    except Exception:
        await message.answer("❌ عذراً، التنسيق الذي أدخلته غير صحيح. يرجى كتابة الـ 5 أرقام مفصولة بفراغات فقط كالمثال التوضيحي بالرسالة السابقة:")

# 4. خيار بيع للزبون مع حركة التحميل الفنية والترند الماستر
@dp.message(F.text == "💰 عملية بيع لزبون محلك")
async def start_sell_op(message: Message, state: FSMContext):
    has_sub = await utils.check_subscription(message.from_user.id)
    if not has_sub:
        await send_subscription_expired_msg(message)
        return
    await message.answer("⚖️ *بدء عملية البيع الحالية:* \nيرجى إدخال *الوزن الصافي الإجمالي* للذهب المراد بيعه بالجرام (مثال: 4.987):", reply_markup=get_cancel_kb())
    await state.set_state(SellOperationStates.waiting_for_weight)

@dp.message(SellOperationStates.waiting_for_weight)
async def process_sell_weight(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء العملية العودة للملف": return
    try:
        weight = float(message.text)
        user_info = await utils.get_user_data(message.from_user.id)
        
        # حسم اختيار العيار تلقائياً أو اعتماد عيار 21 كمعيار أساسي ذكي، لنسأله بلمسة زر سريعة:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 الذهب المباع عيار 21", callback_data=f"docalc_21_{weight}"),
             InlineKeyboardButton(text="💎 الذهب المباع عيار 18", callback_data=f"docalc_18_{weight}")]
        ])
        await message.answer("✨ اختر عيار الصنف المباع للزبون لتطبيق عملياته الحسابية المعتمدة فوراً:", reply_markup=kb)
    except ValueError:
        await message.answer("❌ يرجى إدخال رقم الوزن بشكل صحيح (مثال: 5.420):")

@dp.callback_query(F.data.startswith("docalc_"))
async def execute_sell_calculation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split("_")
    karat = int(parts[1])
    weight = float(parts[2])
    
    user_info = await utils.get_user_data(callback.from_user.id)
    mithqal_price = user_info['m21_price'] if karat == 21 else user_info['m18_price']
    workmanship = user_info['w21_charge'] if karat == 21 else user_info['w18_charge']
    usd_rate = user_info['usd_rate']
    
    # جلب رقم الترند الماستر الذي يزيد مع كل عملية كاستعراض لقوة المنظومة
    trend_num = await utils.get_trend_number()
    
    # حركة التحميل الفنية الإبداعية لمدة 5 ثوانٍ ليعرف العميل صعوبة ودقة الحسبة
    loading = await callback.message.answer("⏳ *جاري الاتصال السحابي بخوادم آرامكي المركزية...*")
    await asyncio.sleep(1.2)
    await loading.edit_text(f"⚖️ *جاري تطبيق قانون المثقال العراقي وعزل أجور الصياغة الموازية...*\n⚙️ الحركة بالترند: `#{trend_num}`")
    await asyncio.sleep(1.2)
    await loading.edit_text(f"💵 *جاري تصفية أوراق النقد النقدية وفرز كسر الدينار العراقي...*\n⚙️ الحركة بالترند: `#{trend_num+2}`")
    await asyncio.sleep(1.3)
    await loading.edit_text("✨ *اللمسات الأخيرة لتنسيق فواتير محلك المعتمدة...*")
    await asyncio.sleep(1.3)
    await loading.delete()
    
    # العملية الحسابية الدقيقة المطلوبة: تقسيم المثقال على 5 + الأجور مضروبة بالوزن مع دقة الفواصل
    gram_base, total_iqd, waraqa, remain_iqd = utils.calculate_gold(weight, workmanship, mithqal_price, usd_rate)
    
    # خزن النواتج مؤقتاً في FSM لتفادي مشكلة تعليق الفاتورة
    await state.update_data(
        res_w=weight, res_k=karat, res_gb=gram_base, res_wm=workmanship,
        res_iqd=total_iqd, res_war=waraqa, res_rem=remain_iqd
    )
    
    result_ui = (
        f"👑 *النتيجة الحسابية الرسمية للبيع* 👑\n"
        f"═══════════════════════════\n"
        f"📋 الصنف: *ذهب عيار {karat}*\n"
        f"⚖️ الوزن الموزون بدقة: *{weight:.3f} غرام*\n"
        f"📐 غرام الصافي (المثقال ÷ 5): *{int(gram_base):,} د.ع*\n"
        f"🛠️ أجور الصياغة المعتمدة للجرام: *{int(workmanship):,} د.ع*\n"
        f"═══════════════════════════\n\n"
        f"💰 *إجمالي الصافي بالدينار العراقي:* \n» *{int(total_iqd):,} د.ع*\n\n"
        f"💵 *حسبة النقد والكسور بأسواق العراق:* \n» *{waraqa} ورقة فئة 100$* 💵 \n» المتبقي كسر بالدينار: *{int(remain_iqd):,} د.ع* 🇮🇶\n"
        f"═══════════════════════════\n"
        f"💎 نظام آرامكي الذكي فرض دقة أموالك ميدانياً."
    )
    
    kb_invoice = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧾 تنظيم وثيقة البيع والفاتورة الفاخرة للزبون", callback_data="make_premium_invoice")]
    ])
    
    await callback.message.answer(result_ui, parse_mode="Markdown", reply_markup=get_dashboard_kb())
    await callback.message.answer("💡 *الزبون يطلب وصلاً؟* اضغط على الزر أدناه لإصدار الفاتورة المطبوعة بهوية محلك العامر:", reply_markup=kb_invoice)

# 5. خيار شراء من الزبون - رسالة موحدة منسقة تدمج البورصة والأجور والوزن
@dp.message(F.text == "⚖️ عملية شراء ذهب من زبون")
async def start_buy_op(message: Message, state: FSMContext):
    has_sub = await utils.check_subscription(message.from_user.id)
    if not has_sub:
        await send_subscription_expired_msg(message)
        return
    
    user_info = await utils.get_user_data(message.from_user.id)
    buy_prompt = (
        "⚖️ *غرفة الشراء المباشر والكسر من الزبائن* ⚖️\n"
        "═══════════════════════════════\n"
        "يرجى إرسال بيانات الشراء الحالية بسطر واحد مفصولة بفراغ كالتالي:\n"
        "`[الوزن الصافي] [عيار الذهب 21 أو 18] [أجور التصفية/التصهير للغرام]`\n\n"
        "💡 *مثال توضيحي للإدخال المباشر:* \n"
        "`12.450 21 3000`\n"
        "═══════════════════════════════\n"
        f"💡 بورصتك المخزنة حالياً للشراء: \n"
        f"• مثقال 21: {int(user_info['m21_price']):,} د.ع | • مثقال 18: {int(user_info['m18_price']):,} د.ع"
    )
    await message.answer(buy_prompt, parse_mode="Markdown", reply_markup=get_cancel_kb())
    await state.set_state(BuyOperationStates.waiting_for_buy_data)

@dp.message(BuyOperationStates.waiting_for_buy_data)
async def process_buy_calculation(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء العملية العودة للملف": return
    try:
        parts = message.text.split()
        weight = float(parts[0])
        karat = int(parts[1])
        melt_charge = float(parts[2])
        
        user_info = await utils.get_user_data(message.from_user.id)
        mithqal_price = user_info['m21_price'] if karat == 21 else user_info['m18_price']
        usd_rate = user_info['usd_rate']
        
        # حسبة الشراء: سعر الغرام يطرح منه أجور التصفية والتصهير
        gram_base = mithqal_price / 5.0
        final_gram_buy = gram_base - melt_charge
        total_iqd = final_gram_buy * weight
        
        usd_single = usd_rate / 100.0
        total_usd = total_iqd / usd_single
        waraqa = int(total_usd // 100)
        remain_iqd = (total_usd % 100) * usd_single
        
        # حفظ البيانات للفاتورة
        await state.update_data(
            res_w=weight, res_k=karat, res_gb=gram_base, res_wm=(-melt_charge),
            res_iqd=total_iqd, res_war=waraqa, res_rem=remain_iqd
        )
        
        result_ui = (
            f"⚖️ *النتيجة الحسابية المعتمدة لـ (شراء الكسر)* ⚖️\n"
            f"═══════════════════════════\n"
            f"📋 الصنف المشتري: *ذهب عيار {karat} كسر*\n"
            f"⚖️ الوزن الصافي: *{weight:.3f} غرام*\n"
            f"📐 سعر الغرام الخام للبورصة: *{int(gram_base):,} د.ع*\n"
            f"🔥 أجور التصفية والتصهير المخصومة: *{int(melt_charge):,} د.ع*\n"
            f"═══════════════════════════\n\n"
            f"💰 *المبلغ المستحق كاش للزبون بالدينار:* \n» *{int(total_iqd):,} د.ع*\n\n"
            f"💵 *التسوية بنظام الورق والموازي:* \n» *{waraqa} ورقة دولار* 💵 + *{int(remain_iqd):,} د.ع كسر عراقي* 🇮🇶\n"
            f"═══════════════════════════\n"
            f"💎 تمت الحسبة بأمان مطلق تحت رعاية منظومة آرامكي الذكية."
        )
        
        kb_invoice = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧾 تنظيم وإصدار وثيقة الفاتورة للمحل", callback_data="make_premium_invoice")]
        ])
        
        await message.answer(result_ui, parse_mode="Markdown", reply_markup=get_dashboard_kb())
        await message.answer("💡 خيار إضافي: يمكنك توثيق العملية الحسابية بفاتورة رسمية فوراً بالضغط أدناه:", reply_markup=kb_invoice)
        
    except Exception:
        await message.answer("❌ خطأ في إدخال البيانات، يرجى كتابتها تماماً مثل المثال: الوزن ثم العيار ثم الأجور مفصولة بفراغات:")

# 6. تنظيم الفاتورة الفاخرة باللهجة العراقية المحببة والكلام المعسل
@dp.callback_query(F.data == "make_premium_invoice")
async def ask_client_name_invoice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("✍️ *يا الله.. يرجى إدخال اسم الزبون الكريم* الذي تريد إصدار الفاتورة الفاخرة باسمه:")
    await state.set_state(InvoiceFlowStates.waiting_for_client_name)

@dp.message(InvoiceFlowStates.waiting_for_client_name)
async def output_premium_invoice(message: Message, state: FSMContext):
    customer_name = message.text.strip()
    data = await state.get_data()
    shop = await utils.get_user_data(message.from_user.id)
    
    op_title = "وصل شراء كسر وثيقة معتمدة" if data['res_wm'] < 0 else "فاتورة بيع رقمية فاخرة"
    charge_title = "أجور التصفية المخصومة" if data['res_wm'] < 0 else "أجور الصياغة للغرام"
    display_charge = abs(data['res_wm'])
    
    invoice_ui = (
        f"📜 *{op_title}* 📜\n"
        f"🏛️ *المصدر العامر:* {shop['shop_name']}\n"
        f"📍 *عنوان المحل:* {shop['shop_address']}\n"
        f"📞 *رقم هاتف المحل رسميّاً:* {shop['shop_phone']}\n"
        f"═══════════════════════════════\n\n"
        f"👤 *إلى السيد/ة المحترم/ة:* {customer_name}\n"
        f"⚖️ الوزن الصافي الإجمالي للذهب: *{data['res_w']:.3f} غرام*\n"
        f"📋 العيار التجاري المعتمد: ذهب عيار {data['res_k']}\n"
        f"🛠️ {charge_title}: *{int(display_charge):,} دينار عراقي*\n"
        f"═══════════════════════════════\n\n"
        f"💰 *المجموع النهائي بالدينار العراقي:* \n» *{int(data['res_iqd']):,} د.ع*\n\n"
        f"💵 *المجموع المسوى بنظام بورصة السوق:* \n» *{data['res_war']} ورقة دولار* 💵 + *{int(data['res_rem']):,} دينار عراقي* 🇮🇶\n"
        f"═══════════════════════════════\n\n"
        f"✨ *تتهنون برزقكم يا رب، ونشكر ثقتكم الغالية بمحلاتنا العامرة* ✨\n\n"
        f"👑 *صيغت وتمت مراجعتها عبر النظام الذكي للأتمتة الحسابية*\n"
        f"🚀 معرف المنظومة الرسمي بالمملكة الرقمية لشركة آرامكي: @GoldenCalc_Bot"
    )
    
    await message.answer(invoice_ui, parse_mode="Markdown", reply_markup=get_dashboard_kb())
    await state.clear()

# 7. الرسالة الرسمية المعسلة مع الخصم عند انتهاء الاشتراك
async def send_subscription_expired_msg(message: Message):
    expired_text = (
        "👑 *مجموعة آرامكي للحلول الرقمية - فرع نواة الذهب* 👑\n"
        "═══════════════════════════════\n"
        "شريكنا وصائغنا العزيز.. نود إعلامكم بأن الفترة المتاحة لحسابكم قد انتهت صلاحيتها السحابية حالياً.\n"
        "حرصاً على سلامة حسابات محلك اليومية وتجنب القفل المفاجئ للموازين أمام زبائنك ميدانياً، يرجى تجديد قيد اشتراكك.\n\n"
        "💳 *عروض وخصومات آرامكي لفترة محدودة جداً:* \n"
        "💰 اشترك الآن بسعر الخصم الذهبي: *105,000 دينار عراقي شهرياً فقط!* بدلاً من السعر الأساسي البالغ 133,000 د.ع.\n\n"
        "⚡ *طرق الدفع السريعة المتاحة للتفعيل التلقائي:* \n"
        "🔒 ندعم الدفع الآمن الفوري عبر بطاقات **الماستركارد (Mastercard)** الإلكترونية لضمان استقرار العمل بدون تأثر بضعف الإنترنت.\n\n"
        f"📞 *لإرسال طلب التفعيل أو الاستفسار الطارئ، تواصل مع الرقم الماستر للإدارة:* `{MASTER_SUPPORT}`\n"
        "═══════════════════════════════\n"
        "✨ نظام آرامكي.. أمان دائم لفخامة تجارتك وعملك الصاعد."
    )
    await message.answer(expired_text, parse_mode="Markdown")

# 8. لوحة الماستر الفخمة والتحكم الكامل للأدمن
@dp.message(F.text == "👑 لوحة تحكم الماستر")
async def open_admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 جرد وكشف حسابات الصاغة", callback_data="adm_view_users")],
        [InlineKeyboardButton(text="⏱️ تعديل وقت التجربة الافتراضي", callback_data="adm_global_trial")],
        [InlineKeyboardButton(text="📢 بث رسالة تنبيه للكل", callback_data="adm_broadcast")]
    ])
    await message.answer("👑 *لوحة السيطرة الاستراتيجية والتحكم الفوقي الماستر:* \nأنت هسة تدير قاعدة البيانات السحابية المركزية لنواة الذهب.", reply_markup=kb)

@dp.callback_query(F.data == "adm_view_users")
async def adm_view_users_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    users = await utils.admin_get_all_users()
    report = "👥 *جرد الحسابات والأرقام الحقيقية المفعّلة بالنظام:* \n\n"
    for u in users:
        report += (f"🆔 `{u[0]}` | 🏢 *{u[2] or 'غير مسجل'}* \n"
                   f"👤 @{u[1] or 'لايوجد'} | Status: {u[3]}\n"
                   f"⏱️ ينتهي التجريبي: `{u[4]}`\n"
                   f"📅 ينتهي المدفوع: `{u[5]}`\n"
                   f"⚙️ للإجراء الفوري اضغط:\n"
                   f"• تفعيل شهر: `/addsub {u[0]}`\n"
                   f"• تقليص وقت: `/reduce {u[0]}`\n"
                   f"• حظر فوري: `/block {u[0]}`\n"
                   f"═══════════════════\n")
    
    # تجزئة الرسالة في حال تخطي حدود النصوص بالتليجرام لتفادي التعليق
    if len(report) > 4000:
        for x in range(0, len(report), 4000):
            await callback.message.answer(report[x:x+4000], parse_mode="Markdown")
    else:
        await callback.message.answer(report, parse_mode="Markdown")
    await callback.answer()

@dp.message(F.text.startswith("/addsub "))
async def cmd_addsub(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    uid = int(message.text.split()[1])
    await utils.admin_modify_user_time(uid, "add_sub", 30)
    await message.answer(f"✅ تم تفعيل باقة الاشتراك الفاخرة المعتمدة للصائغ صاحب المعرف `{uid}` لمدة 30 يوماً كاملة.")

@dp.message(F.text.startswith("/reduce "))
async def cmd_reduce(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    uid = int(message.text.split()[1])
    await utils.admin_modify_user_time(uid, "reduce_trial", 0)
    await message.answer(f"✅ تم تقليص وقت الاشتراك التجريبي فوراً وبنجاح للمعرف `{uid}` ليبقى ساعة واحدة فقط.")

@dp.message(F.text.startswith("/block "))
async def cmd_block(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    uid = int(message.text.split()[1])
    await utils.admin_modify_user_time(uid, "block", 0)
    await message.answer(f"🛑 تم تطبيق الحظر السحابي الفوري وإنهاء جلسة العمل للمعرف `{uid}` بنجاح.")

@dp.callback_query(F.data == "adm_global_trial")
async def adm_global_trial_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer("⏱️ *تعديل الوقت المجاني الافتراضي للعملاء الجدد:* \nيرجى إدخال عدد الساعات الجديدة فوراً (مثال: أرسل `24` لجعله يوم واحد، أو `168` لجعله 7 أيام):")
    await state.set_state(AdminPanelStates.waiting_for_global_trial)
    await callback.answer()

@dp.message(AdminPanelStates.waiting_for_global_trial)
async def save_global_trial(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    if message.text.isdigit():
        hours = int(message.text)
        await utils.admin_set_global_trial(hours)
        await message.answer("✅ *تم بنجاح!* تم تعديل قيمة الوقت المجاني الافتراضي، وستتغير تلقائياً في واجهات الترحيب لجميع العملاء الجدد القادمين للنظام.")
        await state.clear()
    else:
        await message.answer("❌ يرجى إرسال رقم صحيح يمثل الساعات:")

@dp.callback_query(F.data == "adm_broadcast")
async def adm_broadcast_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer("📢 اكتب الآن رسالة التنبيه أو التحذير التي تود بثها فوراً لجميع العملاء المسجلين بقاعدة البيانات:")
    await state.set_state(AdminPanelStates.waiting_for_broadcast_msg)
    await callback.answer()

@dp.message(AdminPanelStates.waiting_for_broadcast_msg)
async def send_broadcast_to_all(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    users = await utils.admin_get_all_users()
    count = 0
    for u in users:
        try:
            await bot.send_message(chat_id=u[0], text=f"📢 *إشعار رسمي هام من إدارة آرامكي لـ نواة الذهب:*\n\n{message.text}", parse_mode="Markdown")
            count += 1
        except Exception: pass
    await message.answer(f"✅ تم بنجاح بث وبث إشعارك الإداري ووصل بنجاح إلى ({count}) صائغ مشترك بالخوادم.")
    await state.clear()

async def main():
    await utils.init_and_refresh_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
