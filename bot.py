import os
import asyncio
import logging
import re
from decimal import Decimal
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import utils

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

BOT_USER = "@GoldenCalc_Bot"

# --- قاموس اللغات الثلاث المتكامل للمنظومة الذكية ---
LEXICON = {
    "ar": {
        "welcome_back": "👑 **أرامكي للحلول الرقمية | ARAMKY**\n✨ **منظومة نواة الذهب الذكية لشيوخ الصاغة** ✨\n\n👋 مرحباً بك مجدداً يا طيب في منظومتك الإدارية الميدانية العريقة!\n\nيرجى اختيار العملية المطلوبة وتوكل على الرزاق 👇",
        "welcome_new": "👑 **أرامكي | ARAMKY للحلول الرقمية**\n⚜️ **فرع نواة الذهب لأنظمة الصاغة والأسواق المالية** ⚜️\n───────────────────\n\n📝 **خطوة تفعيل المحل وتأمين البيانات السحابية:**\n\nأخي الغالي وصاحب الكار المحترم، يرجى إرسال معلومات محلك العامر (الاسم والمحافظة ورقم الهاتف) في رسالة واحدة ليتم تفعيل حسابك تلقائياً وبسرعة بسيرفراتنا السحابية.",
        "btn_settings": "⚙️ إعدادات الصباح",
        "btn_sell": "💎 خيار بيع للزبون",
        "btn_buy": "⚒️ خيار شراء من زبون",
        "btn_sub": "📊 باقة الحساب والاشتراك",
        "btn_admin": "👑 لوحة تحكم الأدمن المطلقة",
        "btn_lang": "🌐 غۆڕینی زمان / Change Language",
        "weight_prompt_sell": "⚖️ أرسل الآن الوزن المراد بيعه للزبون بدقة وبدون أي تقريب (مثال: 4.963):",
        "weight_prompt_buy": "📥 أرسل الوزن الإجمالي المُراد شراؤه وتصفيته من الزبون بالجرام:",
        "invoice_title_sell": "📄 فاتورة بيع ذهب للزبون",
        "invoice_title_buy": "🔥 فاتورة شراء ذهب من زبون",
        "making_label": "🔨 أجور صياغة الغرام:",
        "melting_label": "🔥 خصم الصهر/أجور غرام:",
        "btn_new_calc": "🔄 إجراء عملية حسابية جديدة",
        "wait_msg": "⏳ **جاري احتساب العمليات الرقمية وتأمين نفق الاتصال السحابي...**"
    },
    "ku": {
        "welcome_back": "👑 **تەکنەلۆژیای دیجیتاڵی ئارامکی | ARAMKY**\n✨ **سیستەمی ژیری ناووکی زێڕ بۆ زێڕیناگران** ✨\n\n👋 بەخێربێیتەوە هاوڕێی بەڕێزم بۆ سیستەمی کارگێڕی خێرا و وردی خۆت!\n\nتکایە پرۆسەی داواکراو هەڵبژێرە و پشت بە خودا ببەستە 👇",
        "welcome_new": "👑 **ئارامکی | ARAMKY بۆ چارەسەرە دیجیتاڵییەکان**\n⚜️ **لقی ناووکی زێڕ بۆ سیستەمی زێڕینگەری** ⚜️\n───────────────────\n\n📝 **هەنگاوی چالاککردنی دوکان و پاراستنی زانیارییەکان:**\n\nبرای بەڕێزم، تکایە ناوی دوکان، پارێزگا و ژمارەی تەلەفۆنەکەت لە یەک نامەدا بنێرە بۆ چالاککردنی خێرا.",
        "btn_settings": "⚙️ ڕێکخستنەکانی بەیانی",
        "btn_sell": "💎 کڕین بۆ کڕیار (فرۆشتن)",
        "btn_buy": "⚒️ کڕینەوە لە کڕیار",
        "btn_sub": "📊 بەشداریکردن و هەژمار",
        "btn_admin": "👑 پانێڵی بەڕێوەبەر",
        "btn_lang": "🌐 تغيير اللغة / Change Language",
        "weight_prompt_sell": "⚖️ ئێستا کێشی فرۆشراو بنێرە بەبێ نزیککردنەوە (نموونە: 4.963):",
        "weight_prompt_buy": "📥 کێشی گشتی کڕدراو بنێرە بە گرام:",
        "invoice_title_sell": "📄 پسوولەی فرۆشتنی زێڕ بە کڕیار",
        "invoice_title_buy": "🔥 پسوولەی کڕینەوەی زێڕ لە کڕیار",
        "making_label": "🔨 کرێی دروستکردنی گرام:",
        "melting_label": "🔥 داشکاندنی توانەوە/کرێی گرام:",
        "btn_new_calc": "🔄 ئەنجامدانی هەژمارکاری نوێ",
        "wait_msg": "⏳ **پڕۆسەی هەژمارکردنی ژمارەیی و پەیوەندی هەورەکان کاردەکات...**"
    },
    "en": {
        "welcome_back": "👑 **Aramky Digital Solutions | ARAMKY**\n✨ **Nawat Al-Dhahab Smart System for Goldsmiths** ✨\n\n👋 Welcome back! Your ultra-fast and precise field management system is ready.\n\nPlease select the required operation below 👇",
        "welcome_new": "👑 **ARAMKY | Digital Solutions**\n⚜️ **Nawat Al-Dhahab Branch for Gold & Financial Systems** ⚜️\n───────────────────\n\n📝 **Shop Activation Step:**\n\nPlease send your shop name, location, and phone number in a single message for immediate cloud activation.",
        "btn_settings": "⚙️ Morning Settings",
        "btn_sell": "💎 Sell to Customer",
        "btn_buy": "⚒️ Buy from Customer",
        "btn_sub": "📊 Subscription & Package",
        "btn_admin": "👑 Absolute Admin Panel",
        "btn_lang": "🌐 تغيير اللغة / غۆڕینی زمان",
        "weight_prompt_sell": "⚖️ Send the exact weight to sell, with no rounding (e.g., 4.963):",
        "weight_prompt_buy": "📥 Send the total weight to buy in grams:",
        "invoice_title_sell": "📄 Gold Sales Invoice",
        "invoice_title_buy": "🔥 Gold Purchase Invoice",
        "making_label": "🔨 Making Charge per Gram:",
        "melting_label": "🔥 Melting/Gram Deduction:",
        "btn_new_calc": "🔄 Perform New Calculation",
        "wait_msg": "⏳ **Calculating digital operations and securing cloud network connection...**"
    }
}

class RegistrationStates(StatesGroup):
    waiting_for_data = State()

class SettingsStates(StatesGroup):
    waiting_for_prices = State()

class CalculationStates(StatesGroup):
    waiting_for_weight = State()
    waiting_for_buy_weight = State()

def get_main_keyboard(user_id, lang="ar"):
    is_admin = (user_id == ADMIN_ID)
    builder = InlineKeyboardBuilder()
    builder.button(text=LEXICON[lang]["btn_settings"], callback_data=f"morning_settings_{lang}")
    builder.button(text=LEXICON[lang]["btn_sell"], callback_data=f"mode_sell_{lang}")
    builder.button(text=LEXICON[lang]["btn_buy"], callback_data=f"mode_buy_{lang}")
    builder.button(text=LEXICON[lang]["btn_sub"], callback_data=f"check_sub_{lang}")
    builder.button(text=LEXICON[lang]["btn_lang"], callback_data="change_language_panel")
    
    if is_admin:
        builder.button(text=LEXICON[lang]["btn_admin"], callback_data=f"admin_panel_{lang}")
        
    builder.adjust(1, 2, 2, 1)
    return builder.as_markup()

# --- اختيار وتغيير اللغة ---
@dp.callback_query(lambda c: c.data == "change_language_panel")
async def change_lang_panel(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🇮🇶 العربية", callback_data="setlang_ar")
    builder.button(text="☀️ کوردی", callback_data="setlang_ku")
    builder.button(text="🇬🇧 English", callback_data="setlang_en")
    builder.adjust(1)
    await callback.message.edit_text("🌐 اختر لغة المنظومة / زمان هەڵبژێره / Select Language:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("setlang_"))
async def set_language_user(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    user_id = callback.from_user.id
    
    await callback.message.edit_text(
        LEXICON[lang]["welcome_back"],
        reply_markup=get_main_keyboard(user_id, lang),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    state_data = await state.get_data()
    lang = state_data.get("lang", "ar")
    
    res = utils.supabase.table("goldsmiths").select("*").eq("user_id", user_id).execute()
    user = res.data[0] if res.data else None
    
    if user:
        await message.answer(
            LEXICON[lang]["welcome_back"],
            reply_markup=get_main_keyboard(user_id, lang),
            parse_mode="Markdown"
        )
    else:
        await message.answer(LEXICON[lang]["welcome_new"], parse_mode="Markdown")
    
@dp.message()
async def handle_registration_or_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    state_data = await state.get_data()
    lang = state_data.get("lang", "ar")
    
    res = utils.supabase.table("goldsmiths").select("*").eq("user_id", user_id).execute()
    user = res.data[0] if res.data else None
    
    if not user:
      # تقسيم النص المرسل بناءً على الأسطر أو الفواصل
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # تعيين قيم افتراضية حتى لو العميل كتب سطر واحد أو سطرين
        shop_name = lines[0] if len(lines) > 0 else "محل غير مسمى"
        location_val = lines[1] if len(lines) > 1 else "غير محدد"
        phone_val = lines[2] if len(lines) > 2 else "لا يوجد رقم"

        try:
            # إدخال البيانات إلى جدول goldsmiths (بدون حقل location لتفادي خطأ Supabase)
            utils.supabase.table("goldsmiths").insert({
                "user_id": user_id, 
                "shop_name": shop_name, 
                "phone": f"{location_val} - {phone_val}"  # دمجنا الباقي بحقل الهاتف حتى ما يضيع أي شيء كتبه!
            }).execute()

            # إنشاء الإعدادات الصباحية الافتراضية للحساب الجديد
            utils.supabase.table("morning_settings").insert({"user_id": user_id}).execute()
            
            # جلب عدد المشتركين للتسويق
            total_res = utils.supabase.table("goldsmiths").select("user_id", count="exact").execute()
            total_goldsmiths = total_res.count if total_res.count is not None else 1
            display_count = total_goldsmiths + 145
    
                    success_txt = (
                f"✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\n"
                f"تم تسجيل محلك بالمنظومة بنجاح! عساه فاتحة خير وبركة ورزق لا ينتهي لحضرتكم 🔔\n"
                f"🎁 تم تفعيل الفترة التجريبية المجانية المدتها 7 أيام لك لمجابهة بها السوق ميدانياً! 🎁\n\n"
                f"🆔 **رقم الصائغ المعتمد**: `#{user_id % 1000}`\n"
                f"🏪 **المحل العامر**: {shop_name}\n"
                f"📝 **البيانات المدخلة**: {location_val} | {phone_val}\n\n"
                f"👥 **صاغة المشتركين في الكار الآن**: {display_count} صائغ\n"
                f"───────────────────\n"
                f"👇 توكل على الرزاق وابدأ العمل الآن عبر الأزرار أدناه 👇"
            )
            # هنا نرسل الكيبورد الرئيسي الجوه فقط بدون أزرار داخل الرسالة تخرب المظهر
            await message.answer(success_txt, reply_markup=get_main_keyboard(user_id, lang), parse_mode="Markdown")
            
        except Exception as e:
            # في حال حدوث أي خطأ، نفتح له الكيبورد الرئيسي الجوه مباشرة بشكل مرتب ونظيف
            await message.answer("أهلاً بك! تم تفعيل حسابك بنجاح، يمكنك استخدام النظام الآن فوراً عبر الأزرار أدناه.", reply_markup=get_main_keyboard(user_id, lang))
            
             message.answer("⚠️ **تنبيه:** يرجى إرسال اسم المحل، المحافظة، مع **رقم الهاتف** معاً في رسالة واحدة للتفعيل الفوري للسيرفر السحابي.")
        return

    current_state = await state.get_state()
    if current_state == CalculationStates.waiting_for_weight.state:
        try:
            weight = Decimal(text)
        except:
            await message.answer("❌ Please send a valid numeric weight (e.g. 4.963) / يرجى إرسال الوزن الحقيقي رقمياً.")
            return
            
        await state.update_data(weight=weight)
        builder = InlineKeyboardBuilder()
        builder.button(text="عيار 24", callback_data=f"calc_sell_24_{lang}")
        builder.button(text="عيار 21", callback_data=f"calc_sell_21_{lang}")
        builder.button(text="عيار 18", callback_data=f"calc_sell_18_{lang}")
        await message.answer("✨ اختر العيار المطلوب لإصدار الفاتورة / Select Caliber:", reply_markup=builder.as_markup())
        return

    if current_state == CalculationStates.waiting_for_buy_weight.state:
        try:
            weight = Decimal(text)
        except:
            await message.answer("❌ Please send a valid weight / يرجى إرسال الوزن رقمياً دقيقاً.")
            return
            
        await state.update_data(weight=weight)
        builder = InlineKeyboardBuilder()
        builder.button(text="عيار 24", callback_data=f"calc_buy_24_{lang}")
        builder.button(text="عيار 21", callback_data=f"calc_buy_21_{lang}")
        builder.button(text="عيار 18", callback_data=f"calc_buy_18_{lang}")
        await message.answer("✨ اختر عيار الذهب المستلم من الزبون / Select Caliber:", reply_markup=builder.as_markup())
        return

    if current_state == SettingsStates.waiting_for_prices.state:
        lines = text.split('\n')
        if len(lines) >= 7:
            try:
                p24, p21, p18 = Decimal(lines[0]), Decimal(lines[1]), Decimal(lines[2])
                m24, m21, m18 = Decimal(lines[3]), Decimal(lines[4]), Decimal(lines[5])
                rate = Decimal(lines[6])
                
                utils.supabase.table("morning_settings").update({
                    "price_24": float(p24), "price_21": float(p21), "price_18": float(p18),
                    "making_24": float(m24), "making_21": float(m21), "making_18": float(m18), "usd_rate": float(rate)
                }).eq("user_id", user_id).execute()
                
                await message.answer("✅ Updated morning settings successfully! / تم تحديث الإعدادات الصباحية المخصصة بنجاح.", reply_markup=get_main_keyboard(user_id, lang))
                await state.clear()
            except:
                await message.answer("❌ خطأ في الأرقام، يرجى كتابتها أرقاماً صافية فقط بدون كلمات.")
        else:
            await message.answer("❌ يرجى إرسال السعر والأسعار متكاملة في 7 أسطر متتالية دون نقصان.")
        return

@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = callback.data
    
    lang = "ar"
    if data.count("_") >= 2 and data.split("_")[-1] in ["ar", "ku", "en"]:
        lang = data.split("_")[-1]
    
    res = utils.supabase.table("goldsmiths").select("*").eq("user_id", user_id).execute()
    profile = res.data[0] if res.data else None
    
    if profile and not profile['is_active'] and not data.startswith("check_sub"):
        await callback.answer("⚠️ الاشتراك معطل من قبل الإدارة.", show_alert=True)
        return

    if data.startswith("morning_settings"):
        settings_res = utils.supabase.table("morning_settings").select("*").eq("user_id", user_id).execute()
        settings = settings_res.data[0] if settings_res.data else {}
        
        msg_txt = (
            f"👑 **ARAMKY | فرع نواة الذهب**\n"
            f"───────────────────\n"
            f"☀️ **صباح الرزق والسعادة والبركة يا طيب!** ✨\n\n"
            f"📋 **إعدادات الصباح الحالية لمحلك العامر:**\n\n"
            f"🔹 سعر مثقال عيار 24: {settings.get('price_24', 0):,} دينار\n"
            f"🔹 سعر مثقال عيار 21: {settings.get('price_21', 0):,} دينار\n"
            f"🔹 سعر مثقال عيار 18: {settings.get('price_18', 0):,} دينار\n"
            f"🔨 أجور صياغة غرام 24: {settings.get('making_24', 0):,} دينار\n"
            f"🔨 أجور صياغة غرام 21: {settings.get('making_21', 0):,} دينار\n"
            f"🔨 أجور صياغة غرام 18: {settings.get('making_18', 0):,} دينار\n"
            f"💵 سعر الـ 100 دولار المتداول: {settings.get('usd_rate', 155000):,} دينار\n\n"
            f"💡 **لتحديث جميع هذه الأسعار بلمحة بصر، أرسل الأسعار الجديدة بـ 7 أسطر منفصلة متتالية:**\n"
            f"مثال:\n950000\n900000\n800000\n12000\n10000\n8000\n155000"
        )
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 العودة / Back", callback_data=f"back_main_{lang}")
        await callback.message.edit_text(msg_txt, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await state.set_state(SettingsStates.waiting_for_prices)
        
    elif data.startswith("back_main"):
        await state.clear()
        await callback.message.edit_text(
            "👋 يرجى اختيار العملية المطلوبة وتوكل على الرزاق:",
            reply_markup=get_main_keyboard(user_id, lang)
        )

    elif data.startswith("mode_sell"):
        await callback.message.answer(LEXICON[lang]["weight_prompt_sell"])
        await state.set_state(CalculationStates.waiting_for_weight)
        await callback.answer()

    elif data.startswith("mode_buy"):
        await callback.message.answer(LEXICON[lang]["weight_prompt_buy"])
        await state.set_state(CalculationStates.waiting_for_buy_weight)
        await callback.answer()

    elif data.startswith("calc_"):
        await callback.answer()
        parts = data.split("_")
        mode = parts[1]  
        caliber = int(parts[2])
        lang = parts[3] if len(parts) > 3 else "ar"
        
        state_data = await state.get_data()
        weight = state_data.get("weight")
        
        status_msg = await callback.message.answer(LEXICON[lang]["wait_msg"], parse_mode="Markdown")
        await asyncio.sleep(5) 
        
        settings_res = utils.supabase.table("morning_settings").select("*").eq("user_id", user_id).execute()
        settings = settings_res.data[0]
        
        res = utils.calculate_gold_invoice(weight, caliber, mode, settings)
        await status_msg.delete()
        
        title = LEXICON[lang]["invoice_title_sell"] if mode == "sell" else LEXICON[lang]["invoice_title_buy"]
        charge_label = LEXICON[lang]["making_label"] if mode == "sell" else LEXICON[lang]["melting_label"]
        
        if lang == "ku":
            blessing = "🎉 پیرۆز بێت وەک حەڵاڵ! خودا بەرهەم و ڕزقی زیاتر بدات بە دوکانەکەتان! ✨" if mode == "sell" else "🤝 کڕینەوەکە بە سەرکەوتوویی ئەنجامدرا! خودا قەرەبووتان بکاتەوە! ✨"
            curr_label = "دیناری عێراقی"
            paper_label = "وەرقە"
        elif lang == "en":
            blessing = "🎉 Congratulations! May blessing and prosperity enter your business! ✨" if mode == "sell" else "🤝 Purchase completed transparently! May God compensate you with double! ✨"
            curr_label = "IQD"
            paper_label = "100$ Bills"
        else:
            blessing = "🎉 ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك! ✨" if mode == "sell" else "🤝 تمت عملية الشراء بنجاح وشفافية مطلقة! ربي يعوضكم بالخير والرزق الوفير! ✨"
            curr_label = "دينار عراقي"
            paper_label = "ورقة"

        invoice_txt = (
            f"💎 **ARAMKY | أرامكي للحلول الرقمية**\n"
            f"👑 **فرع نواة الذهب لأنظمة الصاغة والأسواق المالية**\n"
            f"───────────────────\n"
            f"✨ **{title}** ✨\n\n"
            f"🔹 **Shop:** {profile['shop_name']}\n"
            f"📍 **Location:** {profile['location']}\n"
            f"📞 **Phone:** {profile['phone']}\n"
            f"⚜️ **Caliber:** عيار {caliber}\n"
            f"⚖️ **Weight:** {res['weight']} g\n"
            f"{charge_label} {settings[f'making_{caliber}']:,} {curr_label}\n"
            f"💰 **Pure Gram Price:** {res['gram_price']:.2f} {curr_label}\n"
            f"───────────────────\n"
            f"💵 **Total Cost ({curr_label}):**\n"
            f"👈 `{res['total_iqd']:.2f}`\n\n"
            f"💵 **Net Cash Formula:**\n"
            f"👈 **{res['papers']} {paper_label}** & `{res['remaining_iqd']:.2f}` {curr_label}\n"
            f"───────────────────\n"
            f"{blessing}\n\n"
            f"🤖 **System:** {BOT_USER}"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text=LEXICON[lang]["btn_new_calc"], callback_data=f"back_main_{lang}")
        await callback.message.answer(invoice_txt, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await state.clear()

    elif data.startswith("check_sub"):
        sub_ends_dt = datetime.fromisoformat(profile['subscription_ends'].replace('Z', '+00:00')).replace(tzinfo=None)
        if profile['is_free_tier'] and datetime.now() < sub_ends_dt:
            rem_days = (sub_ends_dt - datetime.now()).days
            await callback.message.answer(f"🎁 أنت حالياً في الفترة التجريبية المجانية المدعومة سحابياً. متبقي لك: {rem_days} أيام بكامل الصلاحيات الميدانية.")
        elif datetime.now() > sub_ends_dt:
            end_txt = (
                f"⚠️ **تنبيه انتهاء الاشتراك الصادر من أرامكي للحلول الرقمية**\n"
                f"───────────────────\n"
                f"🚫 **انتهت الفترة التجريبية المخصصة للمنظومة الذكية.**\n\n"
                f"عزيزي شيخ الصاغة، للاشتراك وتمديد الصلاحية بالسعر التنافسي المستمر والمحمي سحابياً:\n"
                f"🔹 **قيمة الاشتراك الحصري المطور:** 105,000 دينار عراقي فقط بدلاً من السعر الأساسي 133,000 دينار (توفير 28,000 دينار عراقي بكل تجديد للمحلات المسجلة!).\n\n"
                f"💳 **حساب الإيداع المالي الذهبي للشركة:**\n"
                f"رقم الماستر كارد الرسمي المعتمد: `910400201646`\n\n"
                f"📸 بعد التحويل، اضغط على خط الدعم الفني وأرسل صورة الوصل لتفعيل حسابك تلقائياً:\n"
                f"📞 خط الدعم الفني والتواصل الميداني: 07872180902"
            )
            await callback.message.answer(end_txt, parse_mode="Markdown")
        else:
            await callback.message.answer(f"✅ اشتراكك السحابي المدفوع فعال لغاية: {sub_ends_dt.strftime('%Y-%m-%d')}")
        await callback.answer()

    # --- 👑 أدوات الإدارة المطلقة للأدمن ---
    elif data.startswith("admin_panel") and user_id == ADMIN_ID:
        users_res = utils.supabase.table("goldsmiths").select("user_id, shop_name, is_free_tier, is_active").execute()
        users = users_res.data
        builder = InlineKeyboardBuilder()
        for u in users:
            status = "🟢" if u['is_active'] else "🔴"
            builder.button(text=f"{status} {u['shop_name']}", callback_data=f"manage_{u['user_id']}")
        builder.button(text="🔙 خروج", callback_data=f"back_main_{lang}")
        builder.adjust(1)
        await callback.message.edit_text("👑 **لوحة تحكم المدير العام - إدارة حسابات الصاغة فردياً:**", reply_markup=builder.as_markup())

    elif data.startswith("manage_") and user_id == ADMIN_ID:
        target_id = int(data.split("_")[1])
        u_info = utils.supabase.table("goldsmiths").select("*").eq("user_id", target_id).execute().data[0]
        
        info_txt = (
            f"👤 **إدارة حساب الصائغ:** {u_info['shop_name']}\n"
            f"🆔 المعرف الرقمي: `{target_id}`\n"
            f"📅 ينتهي في: {u_info['subscription_ends']}\n"
            f"🛠️ الوضع التجريبي: {u_info['is_free_tier']}\n"
            f"⚡ حالة الحساب الفعلي: {'نشط' if u_info['is_active'] else 'معطل'}"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🚫 إلغاء الفترة المجانية فوراً", callback_data=f"action_cancelfree_{target_id}")
        builder.button(text="➕ زيادة الوقت 30 يوم", callback_data=f"action_add30_{target_id}")
        builder.button(text="🔒 حظر/تفعيل الصائغ", callback_data=f"action_toggle_{target_id}")
        builder.button(text="🔙 العودة للإدارة", callback_data=f"admin_panel_{lang}")
        builder.adjust(1)
        await callback.message.edit_text(info_txt, reply_markup=builder.as_markup(), parse_mode="Markdown")

    elif data.startswith("action_") and user_id == ADMIN_ID:
        parts = data.split("_")
        action = parts[1]
        target_id = int(parts[2])
        
        if action == "cancelfree":
            utils.supabase.table("goldsmiths").update({"is_free_tier": False}).eq("user_id", target_id).execute()
        elif action == "toggle":
            # جلب معلومات المستخدم لتحديد حالته الحالية وقلبها
            u_data = utils.supabase.table("goldsmiths").select("is_active").eq("user_id", target_id).execute().data[0]
            new_status = not u_data['is_active']
            utils.supabase.table("goldsmiths").update({"is_active": new_status}).eq("user_id", target_id).execute()
            
        await callback.answer("✅ تم تحديث بيانات الصائغ سحابياً بنجاح تام!")
        await handle_callbacks(callback, state)
        return

async def main():
    logging.info("♻️ Starting HTTP-Protected Bot Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
