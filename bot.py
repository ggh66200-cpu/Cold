import os
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiohttp import web

import utils

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# حالات إدخال البيانات الموحدة لمنع التكرار
class FormStates(StatesGroup):
    waiting_for_sell_data = State()
    waiting_for_buy_data = State()
    waiting_for_morning_prices = State()
    waiting_for_admin_days = State()
    waiting_for_admin_msg = State()

LEXICON = {
    "ar": {
        "btn_morning": "⚙️ الإعدادات الصباحية للمحل",
        "btn_sell": "💎 بيع للزبون (صياغة جديدة)",
        "btn_buy": "⚒️ شراء من زبون (ذهب كسر)",
        "btn_lang": "🌐 تغيير اللغة / غۆڕینی زمان"
    },
    "ku": {
        "btn_morning": "⚙️ ڕێکخستنەکانی نرخی بەیانی",
        "btn_sell": "💎 کڕین بۆ کڕیار (فرۆشتن)",
        "btn_buy": "⚒️ کڕینەوە لە کڕیار (شکاو)",
        "btn_lang": "🌐 تغيير اللغة / Change Language"
    },
    "en": {
        "btn_morning": "⚙️ Morning Settings",
        "btn_sell": "💎 Sell to Customer",
        "btn_buy": "⚒️ Buy from Customer",
        "btn_lang": "🌐 تغيير اللغة / غۆڕینی زمان"
    }
}

def get_customer_keyboard(lang="ar"):
    builder = ReplyKeyboardBuilder()
    builder.button(text=LEXICON[lang]["btn_morning"])
    builder.button(text=LEXICON[lang]["btn_sell"])
    builder.button(text=LEXICON[lang]["btn_buy"])
    builder.button(text=LEXICON[lang]["btn_lang"])
    builder.adjust(1, 2, 1) # ترتيب الكيبورد الثابت الأنيق
    return builder.as_markup(resize_keyboard=True)

async def get_welcome_text(user_id, lang="ar"):
    # جلب الإعدادات الافتراضية للنظام من قاعدة البيانات سبيس
    sys_cfg = utils.supabase.table("system_config").select("*").eq("id", 1).execute()
    free_days = sys_cfg.data[0]["default_free_days"] if sys_cfg.data else 7
    welcome_msg = sys_cfg.data[0]["welcome_msg"] if sys_cfg.data else "أهلاً بكم في نظامنا المطور."
    
    profile = utils.get_or_create_user(user_id)
    sub_ends = datetime.fromisoformat(profile['subscription_ends'].replace('Z', '+00:00')).replace(tzinfo=None)
    rem_days = (sub_ends - datetime.utcnow()).days
    status_text = f"🎁 متبقي لك: {rem_days} يوم مجاني" if rem_days > 0 else "⚠️ انتهى الاشتراك، يرجى إرسال صورة التحويل لتفعيله يدوياً."
    
    if lang == "ar":
        return f"👑 **أرامكي لِلحلول الرقمية | فرع نواة الذهب**\n⚜️ {welcome_msg} ⚜️\n\n🎯 **الحالة الحالية للحساب:**\n👈 {status_text}\n\nيرجى اختيار العملية المطلوبة من الكيبورد أدناه وتوكل على الرزاق الفتاح 👇"
    elif lang == "ku":
        return f"👑 **تەکنەلۆژیای ئارامکی | لقی ناووکی زێڕ**\n⚜️ سیستەمی ژیری زێڕینگەری ⚜️\n\n👈 ماوەی بەکارهێنان: {rem_days} ڕۆژ ماوە."
    else:
        return f"👑 **ARAMKY Digital Solutions | Gold Branch**\n⚜️ Smart Goldsmith Calculator ⚜️\n\n👈 Active Status: {rem_days} Days Remaining."

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    profile = utils.get_or_create_user(user_id, message.from_user.username)
    lang = profile.get("language", "ar")
    
    txt = await get_welcome_text(user_id, lang)
    await message.answer(txt, reply_markup=get_customer_keyboard(lang), parse_mode="Markdown")

# --- معالجة الحسبة الفورية (البيع) واحد جوة واحد ---
@dp.message(lambda m: "بيع للزبون" in m.text or "Sell to" in m.text or "فرۆشتن" in m.text)
async def sell_init(message: types.Message, state: FSMContext):
    await message.answer(
        "💎 **واجهة الاحتساب الملكي الموحد (البيع للزبون):**\n\n"
        "يرجى إرسال المدخلات متتالية (واحد جوة واحد) في رسالة واحدة بالشكل التالي:\n"
        "العيار (24 أو 21 أو 18)\n"
        "الوزن الدقيق بالغرام (مثل 12.340)\n\n"
        "📝 **مثال لإرسال الرسالة:**\n`21`\n`5.420`", parse_mode="Markdown"
    )
    await state.set_state(FormStates.waiting_for_sell_data)

@dp.message(FormStates.waiting_for_sell_data)
async def sell_process(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lines = [line.strip() for line in message.text.split("\n") if line.strip()]
    if len(lines) < 2:
        await message.answer("❌ يرجى إرسال العيار والوزن متتاليين (واحد جوة واحد) في رسالة واحدة عيني.")
        return
    try:
        caliber = int(lines[0])
        weight = Decimal(lines[1])
        if caliber not in [18, 21, 24]: raise ValueError()
    except:
        await message.answer("❌ خطأ بالمدخلات، تأكد أن العيار (24، 21، 18) والوزن أرقام صافية.")
        return
    
    settings = utils.supabase.table("morning_settings").select("*").eq("user_id", user_id).execute().data[0]
    res = utils.calculate_sell(weight, caliber, settings)
    
    invoice = (
        f"👑 **محل الصائغ الكريم**\n"
        f"⚜️ **فاتورة بيع طوق ملكي فخم** ⚜️\n"
        f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d | %I:%M %p')}\n"
        f"───────────────────\n"
        f"💎 **نوع العيار الملكي:** عيار {caliber}\n"
        f"⚖️ **الوزن الإجمالي:** {res['weight']} غرام\n"
        f"🔨 أجور الصياغة المباركة للغرام: {settings[f'making_{caliber}']:,} دينار\n"
        f"💰 **سعر الغرام الصافي للدقيقة:** {res['gram_price']:.2f} دينار\n"
        f"───────────────────\n"
        f"💵 **المبلغ الكلي المطلوب للعملية:**\n"
        f"👈 `{res['total_iqd']:.2f}` دينار عراقي\n\n"
        f"💵 **تفصيل الكاش لتسهيل العد (حسبة أرامكي الذهب):**\n"
        f"👈 **{res['papers']} ورقة فئة 100$** + الباقي بالفراطة `{res['remaining_iqd']:.2f}` دينار\n"
        f"───────────────────\n"
        f"🎉 ألف مبروك وحلال عليكم عيني! ربي يجعلها فاتحة خير وبركة ورزق متبارك لا ينتهي! ✨\n\n"
        f"🔒 صُممت هذه الحاسبة الذكية بكل فخر لتبسيط كاركم بواسطة: أرامكي للحلول الرقمية 🛡️"
    )
    await message.answer(invoice, parse_mode="Markdown")
    await state.clear()

# --- معالجة الحسبة الفورية (الشراء) واحد جوة واحد ---
@dp.message(lambda m: "شراء من زبون" in m.text or "Buy from" in m.text or "کڕینەوە" in m.text)
async def buy_init(message: types.Message, state: FSMContext):
    await message.answer(
        "⚒️ **واجهة الشراء وتصفية الذهب الكسر (واحد جوة واحد):**\n\n"
        "يرجى إرسال المعلومات كاملة برسالة واحدة متتالية:\n"
        "العيار (24 أو 21 أو 18)\n"
        "سعر مثقال الصباح المتداول بالشاشة\n"
        "أجور الخصم أو الصهر المُراد طرحها للغرام\n"
        "الوزن المراد شراؤه\n\n"
        "📝 **مثال للإرسال السريع:**\n`21`\n`920000`\n`5000`\n`10.500`", parse_mode="Markdown"
    )
    await state.set_state(FormStates.waiting_for_buy_data)

@dp.message(FormStates.waiting_for_buy_data)
async def buy_process(message: types.Message, state: FSMContext):
    lines = [line.strip() for line in message.text.split("\n") if line.strip()]
    if len(lines) < 4:
        await message.answer("❌ يرجى إرسال الأسطر الأربعة كاملة (واحد جوة واحد) دون نقصان حجي.")
        return
    try:
        caliber = int(lines[0])
        mithqal_buy_price = Decimal(lines[1])
        making_deduction = Decimal(lines[2])
        weight = Decimal(lines[3])
    except:
        await message.answer("❌ خطأ بالبيانات الرقمية، يرجى إعادة الإرسال بدقة وصورة صحيحة.")
        return
        
    res = utils.calculate_buy(weight, caliber, mithqal_buy_price, making_deduction)
    
    invoice = (
        f"👑 **منظومة نواة الذهب الذكية**\n"
        f"🔥 **فاتورة شراء واستلام ذهب كسر** 🔥\n"
        f"───────────────────\n"
        f"⚜️ العيار المستلم: عيار {caliber}\n"
        f"⚖️ الوزن الصافي الموزون: {res['weight']} غرام\n"
        f"📉 أجور خصم الصهر المطرودة للغرام: {making_deduction:,} دينار\n"
        f"💰 سعر الغرام الصافي المستحق (المثقال ÷ 5 مع الطرح): {res['gram_price']:.2f} دينار\n"
        f"───────────────────\n"
        f"💵 **المبلغ الكلي الواجب تسليمه للزبون فوراً:**\n"
        f"👈 `{res['total_iqd']:.2f}` دينار عراقي الصافي\n"
        f"───────────────────\n"
        f"🤝 تمت عملية الشراء والاستلام بنجاح وشفافية مطلقة متبادلة! ✨\n\n"
        f"🔒 أرامكي لِلحلول الرقمية - هيبة برمجية تخدم أسواقكم العريقة 🛡️"
    )
    await message.answer(invoice, parse_mode="Markdown")
    await state.clear()

# --- تحديث الإعدادات الصباحية الموحدة ---
@dp.message(lambda m: "الإعدادات الصباحية" in m.text or "Morning Settings" in m.text or "ڕێکخستنەکانی" in m.text)
async def morning_init(message: types.Message, state: FSMContext):
    await message.answer(
        "⚙️ **تحديث أسعار الصباح للسيرفر السحابي (أرامكي):**\n\n"
        "أرسل الأسعار السبعة الجديدة (واحد جوة واحد) لتثبيتها بذاكرة المنظومة:\n"
        "سعر مثقال 24\nسعر مثقال 21\nسعر مثقال 18\nصياغة غرام 24\nصياغة غرام 21\nصياغة غرام 18\nسعر الـ 100 دولار المتداول بالفراطة", parse_mode="Markdown"
    )
    await state.set_state(FormStates.waiting_for_morning_prices)

@dp.message(FormStates.waiting_for_morning_prices)
async def morning_process(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lines = [line.strip() for line in message.text.split("\n") if line.strip()]
    if len(lines) < 7:
        await message.answer("❌ يجب إرسال الـ 7 أسطر كاملة متتالية حجي الورد.")
        return
    try:
        utils.supabase.table("morning_settings").update({
            "price_24": float(lines[0]), "price_21": float(lines[1]), "price_18": float(lines[2]),
            "making_24": float(lines[3]), "making_21": float(lines[4]), "making_18": float(lines[5]), "usd_rate": float(lines[6])
        }).eq("user_id", user_id).execute()
        await message.answer("✅ تم تحديث وتأمين الأسعار الصباحية لمحلك بنجاح تام بالسيرفر السحابي!", reply_markup=get_customer_keyboard("ar"))
        await state.clear()
    except:
        await message.answer("❌ يرجى إرسال أرقام صافية فقط حجي بدون كلمات.")

# --- واجهة اختيار اللغات الثلاث المتكاملة ---
@dp.message(lambda m: "تغيير اللغة" in m.text or "Change Language" in m.text or "زمان" in m.text)
async def lang_panel(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🇮🇶 العربية", callback_data="lang_ar")
    builder.button(text="☀️ کوردی", callback_data="lang_ku")
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.adjust(1)
    await message.answer("🌐 اختر لغة الحاسبة الذكية المعتمدة / زمان هەڵبژێره:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def lang_set(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    utils.supabase.table("goldsmiths").update({"language": lang}).eq("user_id", user_id).execute()
    await callback.message.delete()
    txt = await get_welcome_text(user_id, lang)
    await callback.message.answer(txt, reply_markup=get_customer_keyboard(lang), parse_mode="Markdown")
    await callback.answer()

# 👑 👑 👑 لوحة تحكم الإدارة والأدمن المطلقة لشركة أرامكي 👑 👑 👑
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    builder = InlineKeyboardBuilder()
    builder.button(text="⏱️ تغيير أيام الوقت المجاني الافتراضي", callback_data="adm_change_days")
    builder.button(text="📝 تعديل الرسالة الترحيبية المعسلة", callback_data="adm_change_msg")
    builder.button(text="👥 إدارة وتفعيل حسابات الصاغة", callback_data="adm_manage_users")
    builder.adjust(1)
    await message.answer("👑 **لوحة تحكم المدير العام لشركة أرامكي الرقمية**\n\nأهلاً بك يا قائد، تحكم بالمنظومة بمرونة مطلقة عبر الأزرار:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == "adm_change_days" and c.from_user.id == ADMIN_ID)
async def adm_days_init(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("⏱️ أرسل الرقم الجديد لعدد الأيام المجانية الافتراضية للعملاء الجدد (مثال: `10`):")
    await state.set_state(FormStates.waiting_for_admin_days)
    await callback.answer()

@dp.message(FormStates.waiting_for_admin_days)
async def adm_days_save(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        days = int(message.text.strip())
        utils.supabase.table("system_config").update({"default_free_days": days}).eq("id", 1).execute()
        await message.answer(f"✅ تم تحديث عدد الأيام المجانية الافتراضية إلى: {days} يوم بنجاح!")
        await state.clear()
    except:
        await message.answer("❌ أرسل رقماً صحيحاً فقط.")

@dp.callback_query(lambda c: c.data == "adm_change_msg" and c.from_user.id == ADMIN_ID)
async def adm_msg_init(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 أرسل الديباجة أو الرسالة الترحيبية الجديدة التي تظهر للعملاء عند فتح البوت لتبرز هيبتنا:")
    await state.set_state(FormStates.waiting_for_admin_msg)
    await callback.answer()

@dp.message(FormStates.waiting_for_admin_msg)
async def adm_msg_save(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    msg = message.text.strip()
    utils.supabase.table("system_config").update({"welcome_msg": msg}).eq("id", 1).execute()
    await message.answer("✅ تم تحديث الرسالة الترحيبية المعسلة بنجاح سحابياً!")
    await state.clear()

@dp.callback_query(lambda c: c.data == "adm_manage_users" and c.from_user.id == ADMIN_ID)
async def adm_manage_users(callback: types.CallbackQuery):
    users = utils.supabase.table("goldsmiths").select("*").execute().data
    builder = InlineKeyboardBuilder()
    for u in users:
        status = "🟢" if u['is_active'] else "🔴"
        name = u['username'] if u['username'] else f"صائغ-{u['user_id']%1000}"
        builder.button(text=f"{status} {name}", callback_data=f"usr_{u['user_id']}")
    builder.adjust(1)
    await callback.message.answer("👥 اختر حساب الصائغ لإدارته، تفعيله أو إلغاء اشتراكه بلملمة واحدة:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("usr_") and c.from_user.id == ADMIN_ID)
async def adm_user_action(callback: types.CallbackQuery):
    target_id = int(callback.data.split("_")[1])
    u = utils.supabase.table("goldsmiths").select("*").eq("user_id", target_id).execute().data[0]
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⚡ تفعيل فوري / إلغاء الحظر", callback_data=f"act_toggle_{target_id}")
    builder.button(text="➕ تمديد شهر مدفوع (30 يوم)", callback_data=f"act_add30_{target_id}")
    builder.button(text="🚫 إلغاء الاشتراك والوقت فوراً", callback_data=f"act_expire_{target_id}")
    builder.adjust(1)
    
    await callback.message.answer(
        f"👤 **إدارة حساب العميل المعتمد:**\n"
        f"🆔 المعرف: `{target_id}`\n"
        f"📅 نهاية صلاحية الدخول: {u['subscription_ends']}\n"
        f"الحالة: {'نشط ومفعل 🟢' if u['is_active'] else 'معطل ومحجوب 🔴'}",
        reply_markup=builder.as_markup(), parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("act_") and c.from_user.id == ADMIN_ID)
async def adm_execute_action(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    action = parts[1]
    target_id = int(parts[2])
    
    if action == "toggle":
        u = utils.supabase.table("goldsmiths").select("is_active").eq("user_id", target_id).execute().data[0]
        utils.supabase.table("goldsmiths").update({"is_active": not u['is_active']}).eq("user_id", target_id).execute()
    elif action == "add30":
        new_date = datetime.utcnow() + timedelta(days=30)
        utils.supabase.table("goldsmiths").update({"subscription_ends": new_date.isoformat(), "is_active": True}).eq("user_id", target_id).execute()
    elif action == "expire":
        past_date = datetime.utcnow() - timedelta(days=1)
        utils.supabase.table("goldsmiths").update({"subscription_ends": past_date.isoformat(), "is_active": False}).eq("user_id", target_id).execute()
        
    await callback.answer("✅ تم تنفيذ أمر الإدارة السريع وحفظ البيانات سحابياً بـ Supabase!")

# --- 🚀 خدعة خادم الويب (جعل البوت يعمل كسيرفر مستقل على ريندر لمنع الانهيار) ---
async def web_handle(request):
    return web.Response(text="Nawat Al-Dhahab Smart Server is running perfectly in Iraq!")

async def main():
    app = web.Application()
    app.router.add_get("/", web_handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "8080")))
    asyncio.create_task(site.start())
    
    # بدء الاستماع والبولينج المباشر للبوت
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
