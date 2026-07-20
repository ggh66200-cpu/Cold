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
MASTER_SUPPORT = os.getenv("MASTER_NUMBER", "077XXXXXXXX") 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# قاموس الترجمة الذكي للغات الثلاث
LANG_TEXTS = {
    "ar": {
        "cancel": "❌ إلغاء العملية والانتقال للملف",
        "btn_morning": "☀️ إعدادات الصباح الموحدة",
        "btn_sell": "💵 بيع للزبون",
        "btn_buy": "⚖️ شراء كسر من زبون",
        "btn_lang": "🌐 Ziman / Languages",
        "btn_admin": "👑 لوحة السيطرة والتحكم",
        "reg_start": "📋 *استمارة تسجيل المحل الرقمية:*\nيرجى كتابة *[اسم مكتب الصاغة أو المحل]* الخاص بك حالياً:",
        "reg_address": "📍 ممتاز.. هسة اكتب *[العنوان بالتفصيل مع الوصف]* لكي يظهر بالفاتورة للزبائن:",
        "reg_phone": "📞 خطوة أخيرة.. اكتب *[رقم هاتف المحل]* المعتمد:",
        "reg_success": "🎉 *يا فتاح يا عليم يا رزاق يا كريم*\nتم حفظ بيانات محلك بنجاح وتفعيل لوحتك الحسابية المعتمدة.",
        "sell_start": "⚖️ *بدء حسبة بيع جديدة:*\nيرجى كتابة *[الوزن الإجمالي بالجرام]* حالياً (مثال: `5.450`):",
        "buy_prompt": "⚖️ *غرفة شراء الذهب والكسر من الزبائن* ⚖️\nيرجى إرسال بيانات الشراء سطر تحت سطر (رقم جوه رقم):\n\n`الوزن بالجرام`\n`العيار 21 أو 18`\n`أجور التصفية للجرام`\n\n💡 *مثال للنسخ والتعديل:*\n`10.500`\n`21`\n`3000`",
        "err_format": "❌ عذراً، التنسيق غير صحيح. يرجى إدخال الأرقام سطر تحت سطر رقم جوه رقم:",
        "invoice_btn": "🧾 تنظيم وإصدار وثيقة الفاتورة للزبون",
        "invoice_ask_name": "✍️ *على بركة الله..* يرجى إدخال اسم الزبون الكريم لإتمام صياغة السند:"
    },
    "ku": {
        "cancel": "❌ هەڵوەشاندنەوەی کردارەکە",
        "btn_morning": "☀️ ڕێکخستنی بەیانیان",
        "btn_sell": "💵 فرۆشتن بە کڕیار",
        "btn_buy": "⚖️ کڕینەوەی زێڕی شکاواو",
        "btn_lang": "🌐 Ziman / Languages",
        "btn_admin": "👑 پانێڵی سەرپەرشتیار",
        "reg_start": "📋 *فۆرمی تۆمارکردنی دوکان:*\nتکایە *[ناوی دوکان یان نوسینگەی زێڕینگەری]* بنووسە:",
        "reg_address": "📍 زۆر باشە.. ئێستا *[ناونیشانی تەواو]* بنووسە بۆ سەر پسوولەکە:",
        "reg_phone": "📞 هەنگاوی کۆتایی.. *[ژمارەی تەلەفۆنی دوکان]* بنووسە:",
        "reg_success": "🎉 بە سەرکەوتوویی زانیارییەکانی دوکانەکەت تۆمارکرا و سیستەمەکە چالاک بوو.",
        "sell_start": "⚖️ *دەستپێکردنی ژمێریاری فرۆشتن:*\nتکایە *[کێشی گشتی بە گرام]* بنووسە (نموونە: `5.450`):",
        "buy_prompt": "⚖️ *کڕینەوەی زێڕ و شکاوی کڕیاران* ⚖️\nتکایە زانیارییەکان دێڕ بە دێڕ بنووسە (ژمارە لەژێر ژمارە):\n\n`کێش بە گرام`\n`عیار 21 یان 18`\n`کرێی پاڵاوتن بۆ هەر گرامێک`\n\n💡 *نموونە بۆ کۆپیکردن:*\n`10.500`\n`21`\n`3000`",
        "err_format": "❌ ببورە، شێوازی نووسینەکە هەڵەیە. ژمارەکان دێڕ بە دێڕ بنووسە:",
        "invoice_btn": "🧾 ڕێکخستن و دەرکردنی پسوولە بۆ کڕیار",
        "invoice_ask_name": "✍️ تکایە ناوی کڕیار بنووسە بۆ تەواوکردنی پسوولەکە:"
    },
    "en": {
        "cancel": "❌ Cancel Operation",
        "btn_morning": "☀️ Unified Morning Settings",
        "btn_sell": "💵 Sell to Customer",
        "btn_buy": "⚖️ Buy Scrap Gold",
        "btn_lang": "🌐 Ziman / Languages",
        "btn_admin": "👑 Control Panel / Admin",
        "reg_start": "📋 *Shop Registration Form:*\nPlease enter your *[Shop or Gold Office Name]*:",
        "reg_address": "📍 Excellent.. Now enter your *[Full Address/Description]* for the invoice:",
        "reg_phone": "📞 Last step.. Enter your authorized *[Shop Phone Number]*:",
        "reg_success": "🎉 Your shop profile has been successfully saved and activated.",
        "sell_start": "⚖️ *Start New Sell Calculation:*\nPlease enter the *[Total Weight in Grams]* (e.g., `5.450`):",
        "buy_prompt": "⚖️ *Gold Buying Room (Scrap)* ⚖️\nPlease send the data line by line (Number under Number):\n\n`Weight in Grams`\n`Karat 21 or 18`\n`Refinery Charge per Gram`\n\n💡 *Example to copy and edit:*\n`10.500`\n`21`\n`3000`",
        "err_format": "❌ Sorry, invalid format. Please enter numbers line by line (number under number):",
        "invoice_btn": "🧾 Organize & Issue Customer Invoice",
        "invoice_ask_name": "✍️ Please enter the customer's name to generate the document:"
    }
}

class RegistrationFlow(StatesGroup):
    waiting_for_name = State()
    waiting_for_address = State()
    waiting_for_phone = State()

class UnifiedMorningStates(StatesGroup):
    waiting_for_all_configs = State()

class SellOperationStates(StatesGroup):
    waiting_for_weight = State()

class BuyOperationStates(StatesGroup):
    waiting_for_buy_data = State()

class InvoiceFlowStates(StatesGroup):
    waiting_for_client_name = State()

class AdminPanelStates(StatesGroup):
    waiting_for_global_trial = State()

def get_dashboard_kb(lang="ar"):
    t = LANG_TEXTS.get(lang, LANG_TEXTS["ar"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_morning"])],
            [KeyboardButton(text=t["btn_sell"]), KeyboardButton(text=t["btn_buy"])],
            [KeyboardButton(text=t["btn_lang"]), KeyboardButton(text=t["btn_admin"])]
        ],
        resize_keyboard=True
    )

def get_cancel_kb(lang="ar"):
    t = LANG_TEXTS.get(lang, LANG_TEXTS["ar"])
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t["cancel"])]], resize_keyboard=True)

@dp.message(Command("start"))
async def start_nexus_system(message: Message):
    await utils.add_or_update_user(message.from_user.id, message.from_user.username)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="العربية 🇮🇶", callback_data="lang_ar"),
         InlineKeyboardButton(text="Kurdî ☀️", callback_data="lang_ku"),
         InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")]
    ])
    
    welcome_pinned = (
        "✨ *ARAMKY | أرامكي للحلول الرقمية* ✨\n"
        "✨ *فرع نواة الذهب المعتمد* ✨\n"
        "═══════════════════════════\n"
        "💎 *بيان ونظام الشركة المثبت رسمياً:*\n"
        "منظومة الأتمتة الحسابية الذكية الأولى المخصصة لأسواق الذهب العراقية، مصممة لتعمل بأقصى سرعة وتتجاوز ضعف الإنترنت حمايةً لأرباح صاغتنا الغوالي.\n\n"
        f"📞 *الدعم الفوري والـطوارئ:* `{MASTER_SUPPORT}`\n"
        "═══════════════════════════\n"
        "يرجى تحديد لغة الواجهة التفاعلية للبدء فوراً:"
    )
    await message.answer(welcome_pinned, parse_mode="Markdown", reply_markup=kb)

@dp.message(F.text.in_(["🌐 Ziman / Languages", "🌐 Ziman / Languages"]))
async def change_lang_menu(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="العربية 🇮🇶", callback_data="lang_ar"),
         InlineKeyboardButton(text="Kurdî ☀️", callback_data="lang_ku"),
         InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")]
    ])
    await message.answer("🌐 Select Language / لغات المنظومة:", reply_markup=kb)

@dp.callback_query(F.data.startswith("lang_"))
async def on_lang_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    selected_lang = callback.data.split("_")[1]
    await utils.update_user_lang(callback.from_user.id, selected_lang)
    await callback.message.delete()
    
    t = LANG_TEXTS[selected_lang]
    trial_str = await utils.admin_get_global_trial_string()
    
    await callback.message.answer(
        f"🎁 Period Activated: {trial_str}\n"
        "═══════════════════════════\n"
        f"{t['reg_start']}"
    )
    await state.update_data(lang=selected_lang)
    await state.set_state(RegistrationFlow.waiting_for_name)

@dp.message(RegistrationFlow.waiting_for_name)
async def reg_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ar")
    t = LANG_TEXTS[lang]
    
    await state.update_data(shop_name=message.text.strip())
    await message.answer(t["reg_address"])
    await state.set_state(RegistrationFlow.waiting_for_address)

@dp.message(RegistrationFlow.waiting_for_address)
async def reg_address(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ar")
    t = LANG_TEXTS[lang]
    
    await state.update_data(shop_address=message.text.strip())
    await message.answer(t["reg_phone"])
    await state.set_state(RegistrationFlow.waiting_for_phone)

@dp.message(RegistrationFlow.waiting_for_phone)
async def reg_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ar")
    t = LANG_TEXTS[lang]
    
    await utils.update_shop_profile(message.from_user.id, data['shop_name'], message.text.strip(), data['shop_address'])
    await message.answer(t["reg_success"], parse_mode="Markdown", reply_markup=get_dashboard_kb(lang))
    await state.clear()

@dp.message(F.text.in_(["❌ إلغاء العملية والانتقال للملف", "❌ هەڵوەشاندنەوەی کردارەکە", "❌ Cancel Operation"]))
async def cancel_op(message: Message, state: FSMContext):
    user_info = await utils.get_user_data(message.from_user.id)
    lang = user_info['lang'] if user_info else "ar"
    await state.clear()
    msg = "🛎️ تم إلغاء العملية." if lang == "ar" else "🛎️ کردارەکە هەڵوەشایەوە." if lang == "ku" else "🛎️ Operation cancelled."
    await message.answer(msg, reply_markup=get_dashboard_kb(lang))

# إعدادات الصباح بنمط رقم جوه رقم للغات الثلاث
@dp.message(F.text.in_(["☀️ إعدادات الصباح الموحدة", "☀️ ڕێکخستنی بەیانیان", "☀️ Unified Morning Settings"]))
async def morning_prompt(message: Message, state: FSMContext):
    user_info = await utils.get_user_data(message.from_user.id)
    lang = user_info['lang']
    
    if lang == "ku":
        prompt_text = "📊 *ڕێکخستنی نرخەکانی بەیانیان البورصة* 📊\nقالبەکە کۆپی بکە و ژمارەکان دێڕ بە دێڕ بنووسە بەبێ هیچ خاڵێک:\n\n`نرخی مثقال ٢١`\n`نرخی مثقال ١٨`\n`کرێی دەستی ٢١`\n`کرێی دەستی ١٨`\n`نرخی دۆلار`\n\n📋 *نرخەکانی ئێستا:* \n"
    elif lang == "en":
        prompt_text = "📊 *Morning Exchange Settings* 📊\nCopy the template and send numbers line under line without commas:\n\n`Mithqal 21 Price`\n`Mithqal 18 Price`\n`Workmanship 21`\n`Workmanship 18`\n`USD Rate`\n\n📋 *Current Values:* \n"
    else:
        prompt_text = "📊 *تحديث أسعار البورصة للصباح* 📊\nانسخ القالب، واكتب الأرقام سطر تحت سطر (رقم جوه رقم) بدون أي نقاط أو فواصل:\n\n`سعر مثقال 21`\n`سعر مثقال 18`\n`اجور صياغة 21`\n`اجور صياغة 18`\n`سعر صرف الدولار للورقة`\n\n📋 *القيم الحالية المخزنة بنظامك:* \n"
        
    prompt_text += f"{int(user_info['m21_price'])}\n{int(user_info['m18_price'])}\n{int(user_info['w21_charge'])}\n{int(user_info['w18_charge'])}\n{int(user_info['usd_rate'])}"
    
    await message.answer(prompt_text, parse_mode="Markdown", reply_markup=get_cancel_kb(lang))
    await state.set_state(UnifiedMorningStates.waiting_for_all_configs)

@dp.message(UnifiedMorningStates.waiting_for_all_configs)
async def process_morning(message: Message, state: FSMContext):
    user_info = await utils.get_user_data(message.from_user.id)
    lang = user_info['lang']
    t = LANG_TEXTS[lang]
    
    if message.text in ["❌ إلغاء العملية والانتقال للملف", "❌ هەڵوەشاندنەوەی کردارەکە", "❌ Cancel Operation"]: return
    try:
        lines = message.text.strip().split('\n')
        if len(lines) < 5:
            lines = message.text.strip().split()
            if len(lines) < 5: raise ValueError
            
        m21, m18, w21, w18, usd = map(float, [l.strip() for l in lines[:5]])
        await utils.update_morning_config(message.from_user.id, m21, m18, w21, w18, usd)
        
        suc = "✅ تم تثبيت الأسعار بنجاح!" if lang == "ar" else "✅ نرخەکان بە سەرکەوتوویی جێگیرکران!" if lang == "ku" else "✅ Prices updated successfully!"
        await message.answer(suc, reply_markup=get_dashboard_kb(lang))
        await state.clear()
    except Exception:
        await message.answer(t["err_format"])

# عملية البيع
@dp.message(F.text.in_(["💵 بيع للزبون", "💵 فرۆشتن بە کڕیار", "💵 Sell to Customer"]))
async def start_sell(message: Message, state: FSMContext):
    user_info = await utils.get_user_data(message.from_user.id)
    lang = user_info['lang']
    if not await utils.check_subscription(message.from_user.id):
        await send_expired_notice(message)
        return
    await message.answer(LANG_TEXTS[lang]["sell_start"], parse_mode="Markdown", reply_markup=get_cancel_kb(lang))
    await state.set_state(SellOperationStates.waiting_for_weight)

@dp.message(SellOperationStates.waiting_for_weight)
async def process_sell_weight(message: Message, state: FSMContext):
    if message.text in ["❌ إلغاء العملية والانتقال للملف", "❌ هەڵوەشاندنەوەی کردارەکە", "❌ Cancel Operation"]: return
    try:
        weight = float(message.text)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 عيار 21 / Karat 21", callback_data=f"calc_21_{weight}"),
             InlineKeyboardButton(text="💎 عيار 18 / Karat 18", callback_data=f"calc_18_{weight}")]
        ])
        await message.answer("✨ Select Karat / اختر عيار الصنف:", reply_markup=kb)
    except ValueError:
        await message.answer("❌ Enter valid number:")

@dp.callback_query(F.data.startswith("calc_"))
async def execute_sell(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split("_")
    karat, weight = int(parts[1]), float(parts[2])
    
    user_info = await utils.get_user_data(callback.from_user.id)
    lang = user_info['lang']
    mithqal_price = user_info['m21_price'] if karat == 21 else user_info['m18_price']
    workmanship = user_info['w21_charge'] if karat == 21 else user_info['w18_charge']
    usd_rate = user_info['usd_rate']
    
    trend = await utils.get_trend_number()
    
    load = await callback.message.answer("⏳ ...")
    await asyncio.sleep(1.0)
    await load.delete()
    
    gram_base, total_iqd, waraqa, remain_iqd = utils.calculate_gold(weight, workmanship, mithqal_price, usd_rate)
    await state.update_data(res_w=weight, res_k=karat, res_gb=gram_base, res_wm=workmanship, res_iqd=total_iqd, res_war=waraqa, res_rem=remain_iqd)
    
    # ناتج رقم تحت رقم حسب لغة المستخدم لمنع الجفاف المالي
    if lang == "ku":
        result_text = f"👑 *ئەنجامی فەرمی فرۆشتن* 👑\n═════════════\nکێشی زێڕ:\n{weight:.3f} گرام\n\nنرخی گرام بە خاوی:\n{int(gram_base)} دینار\n\nکرێی دەست بۆ هەر گرامێک:\n{int(workmanship)} دینار\n\n💰 *کۆی گشتی بە دینار:*\n*{int(total_iqd)} دینار*\n\n💵 *دابەشکاری نقد و وەرەقە:*\n*{waraqa} وەرەقە فەی ١٠٠$*\nماوە بە دینار:\n*{int(remain_iqd)} دینار*\n═════════════"
    elif lang == "en":
        result_text = f"👑 *Official Sell Result* 👑\n═════════════\nGold Weight:\n{weight:.3f} grams\n\nBase Gram Price:\n{int(gram_base)} IQD\n\nWorkmanship per Gram:\n{int(workmanship)} IQD\n\n💰 *Total in IQD:*\n*{int(total_iqd)} IQD*\n\n💵 *Cash Breakdown:*\n*{waraqa} Bills of 100$*\nRemaining in IQD:\n*{int(remain_iqd)} IQD*\n═════════════"
    else:
        result_text = f"👑 *النتيجة الحسابية المعتمدة للبيع* 👑\n═════════════\nوزن الذهب:\n{weight:.3f} غرام\n\nسعر الغرام الصافي:\n{int(gram_base)} دينار\n\nأجور الصياغة للجرام:\n{int(workmanship)} دينار\n\n💰 *المجموع الكلي بالدينار العراقي:*\n*{int(total_iqd)} دينار*\n\n💵 *حسبة النقد بالورق والكسر:*\n*{waraqa} ورقة فئة 100$*\nالمتبقي بالدينار العراقي:\n*{int(remain_iqd)} دينار*\n═════════════"
        
    kb_invoice = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG_TEXTS[lang]["invoice_btn"], callback_data="invoice_generate")]])
    await callback.message.answer(result_text, parse_mode="Markdown", reply_markup=get_dashboard_kb(lang))
    await callback.message.answer("✨ Option / خيارات السند:", reply_markup=kb_invoice)

# شراء كسر
@dp.message(F.text.in_(["⚖️ شراء كسر من زبون", "⚖️ کڕینەوەی زێڕی شکاواو", "⚖️ Buy Scrap Gold"]))
async def start_buy(message: Message, state: FSMContext):
    user_info = await utils.get_user_data(message.from_user.id)
    lang = user_info['lang']
    if not await utils.check_subscription(message.from_user.id):
        await send_expired_notice(message)
        return
    await message.answer(LANG_TEXTS[lang]["buy_prompt"], parse_mode="Markdown", reply_markup=get_cancel_kb(lang))
    await state.set_state(BuyOperationStates.waiting_for_buy_data)

@dp.message(BuyOperationStates.waiting_for_buy_data)
async def process_buy(message: Message, state: FSMContext):
    user_info = await utils.get_user_data(message.from_user.id)
    lang = user_info['lang']
    t = LANG_TEXTS[lang]
    
    if message.text in ["❌ إلغاء العملية والانتقال للملف", "❌ هەڵوەشاندنەوەی کردارەکە", "❌ Cancel Operation"]: return
    try:
        lines = message.text.strip().split('\n')
        if len(lines) < 3:
            lines = message.text.strip().split()
            if len(lines) < 3: raise ValueError
            
        weight = float(lines[0].strip())
        karat = int(lines[1].strip())
        melt_charge = float(lines[2].strip())
        
        mithqal_price = user_info['m21_price'] if karat == 21 else user_info['m18_price']
        usd_rate = user_info['usd_rate']
        
        gram_base = mithqal_price / 5.0
        final_gram_buy = gram_base - melt_charge
        total_iqd = final_gram_buy * weight
        
        usd_single = usd_rate / 100.0
        total_usd = total_iqd / usd_single
        waraqa = int(total_usd // 100)
        remain_iqd = (total_usd % 100) * usd_single
        
        await state.update_data(res_w=weight, res_k=karat, res_gb=gram_base, res_wm=(-melt_charge), res_iqd=total_iqd, res_war=waraqa, res_rem=remain_iqd)
        
        if lang == "ku":
            result_text = f"⚖️ *ئەنجامی کڕینەوەی زێڕی شکاواو* ⚖️\n═════════════\nکێش وزن:\n{weight:.3f} گرام\n\nنرخی بورصەی گرام:\n{int(gram_base)} دينار\n\nداشکاندنی کرێی تاواندنەوە:\n{int(melt_charge)} دينار\n\n💰 *کاش الواجب دفعه کڕیار:*\n*{int(total_iqd)} دينار*\n\n💵 *پارەی وەرەقە و کسر:*\n*{waraqa} وەرەقە فەی 100$*\nمابووەوە بە دینار:\n*{int(remain_iqd)} دينار*\n═════════════"
        elif lang == "en":
            result_text = f"⚖️ *Scrap Gold Buy Result* ⚖️\n═════════════\nReceived Weight:\n{weight:.3f} grams\n\nMarket Gram Price:\n{int(gram_base)} IQD\n\nMelt Discount per Gram:\n{int(melt_charge)} IQD\n\n💰 *Net Cash Payout to Customer:*\n*{int(total_iqd)} IQD*\n\n💵 *USD/IQD Liquidity Division:*\n*{waraqa} Bills of 100$*\nRemaining in IQD:\n*{int(remain_iqd)} IQD*\n═════════════"
        else:
            result_text = f"⚖️ *النتيجة الحسابية المعتمدة لـ (شراء الكسر)* ⚖️\n═════════════\nالوزن المستلم:\n{weight:.3f} غرام\n\nسعر غرام البورصة الخام:\n{int(gram_base)} دينار\n\nأجور التصفية المخصومة:\n{int(melt_charge)} دينار\n\n💰 *صافي المبلغ الكاش الواجب دفعه للزبون:*\n*{int(total_iqd)} دينار عراقي*\n\n💵 *تقسيمات السيولة النقدية الموازية:*\n*{waraqa} ورقة دولار فئة 100$*\nالمتبقي بالكسر العراقي:\n*{int(remain_iqd)} دينار*\n═════════════"
            
        kb_invoice = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t["invoice_btn"], callback_data="invoice_generate")]])
        await message.answer(result_text, parse_mode="Markdown", reply_markup=get_dashboard_kb(lang))
        await message.answer("✨ Option / خيارات السند:", reply_markup=kb_invoice)
    except Exception:
        await message.answer(t["err_format"])

# الفاتورة التفاعلية الفاخرة المترجمة
@dp.callback_query(F.data == "invoice_generate")
async def invoice_client_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_info = await utils.get_user_data(callback.from_user.id)
    lang = user_info['lang']
    await callback.message.answer(LANG_TEXTS[lang]["invoice_ask_name"])
    await state.set_state(InvoiceFlowStates.waiting_for_client_name)

@dp.message(InvoiceFlowStates.waiting_for_client_name)
async def output_invoice(message: Message, state: FSMContext):
    customer_name = message.text.strip()
    data = await state.get_data()
    shop = await utils.get_user_data(message.from_user.id)
    lang = shop['lang']
    
    if lang == "ku":
        op_name = "پسوولەی زێڕی فەرمی و דיגיטלי"
        lbl = "کێشی زێڕ:\n" + f"{data['res_w']:.3f} گرام\n\n" + "کۆی گشتی بە دینار:\n" + f"*{int(data['res_iqd'])} دینار*"
        footer = "✨ پیرۆز بێت و سوپاس بۆ متمانەکەتان ✨"
    elif lang == "en":
        op_name = "OFFICIAL DIGITAL GOLD INVOICE"
        lbl = "Total Weight:\n" + f"{data['res_w']:.3f} grams\n\n" + "Grand Total in IQD:\n" + f"*{int(data['res_iqd'])} IQD*"
        footer = "✨ Thank you for your business & trust ✨"
    else:
        op_name = "وثيقة فاتورة الذهب الرقمية الفاخرة"
        lbl = "الوزن الإجمالي الحقيقي:\n" + f"{data['res_w']:.3f} غرام\n\n" + "المجموع الإجمالي النهائي بالدينار:\n" + f"*{int(data['res_iqd'])} دينار عراقي*"
        footer = "✨ تتهنون برزقكم يا رب، ونشكر ثقتكم الغالية بمحلاتنا ✨"
        
    invoice_template = (
        f"📜 *{op_name}* 📜\n"
        f"🏛️ {shop['shop_name']}\n"
        f"📍 {shop['shop_address']}\n"
        f"📞 {shop['shop_phone']}\n"
        "═══════════════════════════\n\n"
        f"👤 To: {customer_name}\n\n"
        f"{lbl}\n\n"
        f"💵 Cash USD:\n*{data['res_war']} x 100$*\n"
        f"Remaining IQD:\n*{int(data['res_rem'])} IQD*\n"
        "═══════════════════════════\n\n"
        f"{footer}\n\n"
        "👑 Nawat Al-Dhahab Automation System by Aramky"
    )
    await message.answer(invoice_template, parse_mode="Markdown", reply_markup=get_dashboard_kb(lang))
    await state.clear()

async def send_expired_notice(message: Message):
    expired_ui = (
        "👑 *شركة آرامكي للحلول الرقمية - فرع نواة الذهب* 👑\n"
        "═══════════════════════════\n"
        "شريكنا العزيز.. انتهت الفترة المتاحة للاستخدام مجاناً لحسابكم.\n"
        "🎁 *سعر الخصم الحصري:* 105,000 دينار عراقي شهرياً فقط!\n"
        "💳 التفعيل فوري وآمن بالكامل عن طريق بطاقات **الماستركارد (Mastercard)** الإلكترونية المعتمدة لضمان السرعة المطلقة واستقرار السيرفر ضد ضعف الإنترنت.\n\n"
        f"📞 تواصل مع الدعم الفوري لتنشيط قفل المنظومة: `{MASTER_SUPPORT}`"
    )
    await message.answer(expired_ui, parse_mode="Markdown")

# لوحة السيطرة الكاملة المخصصة للآدمن
@dp.message(F.text.in_(["👑 لوحة السيطرة والتحكم", "👑 پانێڵی سەرپەرشتیار", "👑 Control Panel / Admin"]))
async def open_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 جرد العملاء والأرقام الحقيقية", callback_data="adm_users")],
        [InlineKeyboardButton(text="⏱️ تعديل الوقت المجاني للكل", callback_data="adm_trial")],
        [InlineKeyboardButton(text="📢 بث رسالة تنبيه لجميع الصاغة", callback_data="adm_alert")]
    ])
    await message.answer("👑 *لوحة السيطرة والتحكم الفوقي الماستر لنواة الذهب:*\nصلاحيات الإشراف الكاملة بين يديك الآن.", reply_markup=kb)

@dp.callback_query(F.data == "adm_users")
async def adm_users_list(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    users = await utils.admin_get_all_users()
    report = "👥 *جرد حسابات المشتركين الحقيقيين بالنظام:* \n\n"
    for u in users:
        report += (f"🆔 `{u[0]}` | المحل: *{u[2] or 'لم يكمل'}* \n"
                   f"يوزر: @{u[1] or 'لايوجد'} | حالة الباقة: {u[3]}\n"
                   f"⚙️ إجراءات تحكم فوري عميق:\n"
                   f"• تفعيل شهر: `/addsub {u[0]}`\n"
                   f"• تقليص وقت مجاني: `/reduce {u[0]}`\n"
                   f"• حظر العميل: `/block {u[0]}`\n"
                   f"═══════════════════\n")
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
    await message.answer(f"✅ تم تفعيل باقة الـ 30 يوماً بنجاح للمعرف `{uid}`.")

@dp.message(F.text.startswith("/reduce "))
async def cmd_reduce(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    uid = int(message.text.split()[1])
    await utils.admin_modify_user_time(uid, "reduce_trial", 0)
    await message.answer(f"⚠️ تم تقليص الوقت المجاني المتبقي للمعرف `{uid}` إلى 15 دقيقة فقط بنجاح.")

@dp.message(F.text.startswith("/block "))
async def cmd_block(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    uid = int(message.text.split()[1])
    await utils.admin_modify_user_time(uid, "block", 0)
    await message.answer(f"🛑 تم تطبيق الحظر السحابي الفوري وقطع الخدمة عن المعرف `{uid}`.")

@dp.callback_query(F.data == "adm_trial")
async def adm_trial_cfg(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer("⏱️ أرسل عدد ساعات الوقت المجاني الافتراضية للعملاء الجدد (مثال: `168` لـ 7 أيام):")
    await state.set_state(AdminPanelStates.waiting_for_global_trial)
    await callback.answer()

@dp.message(AdminPanelStates.waiting_for_global_trial)
async def save_trial(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    if message.text.isdigit():
        await utils.admin_set_global_trial(int(message.text))
        await message.answer("✅ تم تحديث الوقت المجاني الافتراضي لجميع المسجلين الجدد وتعديل رسائل الترحيب تلقائيّاً.")
        await state.clear()
    else:
        await message.answer("❌ يرجى إرسال رقم يمثل الساعات فقط:")

@dp.callback_query(F.data == "adm_alert")
async def adm_alert_cfg(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer("📢 اكتب نص رسالة التنبيه التي سيتم بثها فوراً لهواتف جميع العملاء المشتركين بالخادم:")
    await state.set_state(InvoiceFlowStates.waiting_for_client_name) 
    await callback.answer()

@dp.message(InvoiceFlowStates.waiting_for_client_name)
async def send_global_alert(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    users = await utils.admin_get_all_users()
    count = 0
    for u in users:
        try:
            await bot.send_message(chat_id=u[0], text=f"📢 *إشعار رسمي هام من إدارة آرامكي:*\n\n{message.text}", parse_mode="Markdown")
            count += 1
        except Exception: pass
    await message.answer(f"📢 تم بث رسالة التنبيه بنجاح، ووصلت إلى ({count}) صائغ حاليّاً.")
    await state.clear()

async def main():
    await utils.init_and_refresh_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
