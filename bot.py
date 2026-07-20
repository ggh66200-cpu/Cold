import os
import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import utils

# إعداد السجلات واللوغات
logging.basicConfig(level=logging.INFO)

# الأرقام والمفاتيح الأساسية المستدعاة من السيرفر بآمان
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # ضع معرف التلغرام الخاص بك كأدمن بسيرفر Render

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# معرف المعرف المعتمد للبوت في النظام
BOT_USER = "@GoldenCalc_Bot"

# تعريف حالات إدخال البيانات المجدولة (FSM)
class RegistrationStates(StatesGroup):
    waiting_for_data = State()

class SettingsStates(StatesGroup):
    waiting_for_prices = State()

class CalculationStates(StatesGroup):
    waiting_for_weight = State()
    waiting_for_buy_weight = State()

# --- لوحة المفاتيح الرئيسية المستقرة (المرنة) ---
def get_main_keyboard(is_admin=False):
    builder = InlineKeyboardBuilder()
    builder.button(text="⚙️ إعدادات الصباح", callback_data="morning_settings")
    builder.button(text="💎 خيار بيع للزبون", callback_data="mode_sell")
    builder.button(text="⚒️ خيار شراء من زبون", callback_data="mode_buy")
    builder.button(text="📊 باقة الحساب والاشتراك", callback_data="check_sub")
    
    if is_admin:
        builder.button(text="👑 لوحة تحكم الأدمن المطلقة", callback_data="admin_panel")
        
    builder.adjust(1, 2, 1)
    return builder.as_markup()

# --- 1️⃣ استقبال العميل والتحقق الآمن (دون تكرار الاستارت) ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    conn = await utils.get_db_connection()
    
    # التحقق من وجود الصائغ مسبقاً بقاعدة البيانات السحابية
    user = await conn.fetchrow("SELECT * FROM goldsmiths WHERE user_id = $1", user_id)
    
    if user:
        # إذا كان مسجلاً، يدخل مباشرة للوحة التشغيل المرنة كأنه موقع
        await conn.close()
        await message.answer(
            f"👑 **أرامكي للحلول الرقمية | ARAMKY**\n"
            f"✨ **منظومة نواة الذهب الذكية لشيوخ الصاغة** ✨\n\n"
            f"👋 مرحباً بك مجدداً يا طيب في منظومتك الإدارية الأسرع والأدق بالأحكام الميدانية العريقة!\n\n"
            f"يرجى اختيار العملية المطلوبة وتوكل على الرزاق 👇",
            reply_markup=get_main_keyboard(user_id == ADMIN_ID),
            parse_mode="Markdown"
        )
    else:
        # إذا كان صائغ جديد، يطلب منه تفعيل المحل وتأمين البيانات
        await conn.close()
        welcome_txt = (
            "👑 **أرامكي | ARAMKY للحلول الرقمية**\n"
            "⚜️ **فرع نواة الذهب لأنظمة الصاغة والأسواق المالية** ⚜️\n"
            "───────────────────\n\n"
            "📝 **خطوة تفعيل المحل وتأمين البيانات السحابية:**\n\n"
            "أخي الغالي وصاحب الكار المحترم، يرجى إرسال معلومات محلك العامر كل معلومة في سطر منفصل (اضغط Enter للانتقال لسطر جديد) بهذا الترتيب لتسجيلك بالسيرفر:\n\n"
            "1️⃣ اسم المحل الرسمي\n"
            "2️⃣ المحافظة والمنطقة\n"
            "3️⃣ رقم هاتف المحل المعتمد"
        )
        await message.answer(welcome_txt, parse_mode="Markdown")
        # لا نستخدم ميزة الحالات هنا للسماح له بالكتابة الحرة المباشرة للمرونة
    
# --- 2️⃣ معالجة استقبال النص لبيانات التسجيل المباشر ---
@dp.message()
async def handle_registration_or_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    
    conn = await utils.get_db_connection()
    user = await conn.fetchrow("SELECT * FROM goldsmiths WHERE user_id = $1", user_id)
    
    # إذا لم يكن مسجلاً، نقوم بمعالجة الأسطر الثلاثة للتسجيل
    if not user:
        lines = text.split('\n')
        if len(lines) >= 3:
            shop_name = lines[0].strip()
            location = lines[1].strip()
            phone = lines[2].strip()
            
            # إدخال الصائغ الجديد بفترة تجريبية 7 أيام تلقائياً بالسيستم السحابي
            await conn.execute(
                "INSERT INTO goldsmiths (user_id, shop_name, location, phone) VALUES ($1, $2, $3, $4)",
                user_id, shop_name, location, phone
            )
            # إنشاء إعدادات افتراضية فارغة له ليقوم بتعديلها براحته
            await conn.execute(
                "INSERT INTO morning_settings (user_id) VALUES ($1)", user_id
            )
            
            # جلب إجمالي المشتركين الفعليين بالسيستم السحابي
            total_goldsmiths = await conn.fetchval("SELECT COUNT(*) FROM goldsmiths")
            # إضافة رقم افتراضي فوق العدد الفعلي لإعطاء هيبة فخمة للمنظومة بالميدان
            display_count = total_goldsmiths + 145 
            
            success_txt = (
                f"✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\n"
                f"🎉 ما شاء الله، تم تسجيل محلك بالمنظومة بنجاح تام! عساه فاتحة خير وبركة ورزق لا ينتهي لحضرتكم.\n\n"
                f"🎁 **رزقكم مبارك، وتم تفعيل الفترة التجريبية المجانية المدتها 7 أيام لك تجتاح بها السوق ميدانياً!**\n\n"
                f"🆔 **رقم الصائغ المعتمد:** #{user_id % 1000}\n"
                f"📍 **المحل العامر:** {shop_name}\n"
                f"🗺️ **الموقع:** {location}\n"
                f"📞 **الهاتف:** {phone}\n\n"
                f"👥 **المشتركين النشطين في الكار الآن:** {display_count} صائغ\n"
                f"───────────────────\n"
                f"🤖 يرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق 👇"
            )
            await message.answer(success_txt, reply_markup=get_main_keyboard(user_id == ADMIN_ID), parse_mode="Markdown")
        else:
            await message.answer("❌ عذراً يا غالي، يرجى كتابة المعلومات بثلاثة أسطر منفصلة تماماً كما موضح بالترتيب أعلاه لضمان إتمام التسجيل السحابي بنجاح.")
        await conn.close()
        return

    # معالجة استلام الوزن لعملية البيع
    current_state = await state.get_state()
    if current_state == CalculationStates.waiting_for_weight.state:
        await conn.close()
        try:
            weight = Decimal(text)
        except:
            await message.answer("❌ يرجى إرسال الوزن الحقيقي بشكل رقمي دقيق (مثال: 4.963).")
            return
            
        await state.update_data(weight=weight)
        # إظهار أزرار اختيار العيار بعد إدخال الوزن مباشرة لزيادة سرعة الأداء الحركي
        builder = InlineKeyboardBuilder()
        builder.button(text="عيار 24", callback_data="calc_sell_24")
        builder.button(text="عيار 21", callback_data="calc_sell_21")
        builder.button(text="عيار 18", callback_data="calc_sell_18")
        await message.answer("✨ اختر العيار المطلوب لإصدار الفاتورة الفخمة بلحظة:", reply_markup=builder.as_markup())
        return

    # معالجة استلام الوزن لعملية الشراء
    if current_state == CalculationStates.waiting_for_buy_weight.state:
        await conn.close()
        try:
            weight = Decimal(text)
        except:
            await message.answer("❌ يرجى إرسال الوزن الحقيقي المُراد شراؤه بشكل رقمي دقيق.")
            return
            
        await state.update_data(weight=weight)
        builder = InlineKeyboardBuilder()
        builder.button(text="عيار 24", callback_data="calc_buy_24")
        builder.button(text="عيار 21", callback_data="calc_buy_21")
        builder.button(text="عيار 18", callback_data="calc_buy_18")
        await message.answer("✨ اختر عيار الذهب المستلم من الزبون لإجراء التصفية المالية:", reply_markup=builder.as_markup())
        return

    # معالجة استلام الإعدادات الصباحية المخصصة للعميل والمخيرة بشكل أسطر عمودية
    if current_state == SettingsStates.waiting_for_prices.state:
        lines = text.split('\n')
        if len(lines) >= 7:
            try:
                p24, p21, p18 = Decimal(lines[0]), Decimal(lines[1]), Decimal(lines[2])
                m24, m21, m18 = Decimal(lines[3]), Decimal(lines[4]), Decimal(lines[5])
                rate = Decimal(lines[6])
                
                await conn.execute(
                    """UPDATE morning_settings SET 
                       price_24=$1, price_21=$2, price_18=$3, 
                       making_24=$4, making_21=$5, making_18=$6, usd_rate=$7 WHERE user_id=$8""",
                    p24, p21, p18, m24, m21, m18, rate, user_id
                )
                await message.answer("✅ تم تحديث إعداداتك الصباحية المخصصة بنجاح سحابي تام! الأنظمة جاهزة للعمليات الميدانية فوراً.", reply_markup=get_main_keyboard(user_id == ADMIN_ID))
                await state.clear()
            except Exception as e:
                await message.answer("❌ حدث خطأ في الأرقام، يرجى التأكد من كتابتها أرقاماً صافية فقط بدون كلمات.")
        else:
            await message.answer("❌ يرجى إرسال السعر والأسعار متكاملة في 7 أسطر متتالية دون نقصان.")
        await conn.close()
        return

    await conn.close()

# --- 3️⃣ إدارة الأزرار وعرض الإعدادات المخصصة العمودية ---
@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = callback.data
    conn = await utils.get_db_connection()
    
    # فحص صلاحية الاشتراك والتأكد من تفعيل العميل قبل تشغيل أي ميزة
    profile = await conn.fetchrow("SELECT * FROM goldsmiths WHERE user_id = $1", user_id)
    if profile and not profile['is_active'] and data != "check_sub":
        await callback.answer("⚠️ عذراً، اشتراكك معطل حالياً من قبل الإدارة.", show_alert=True)
        await conn.close()
        return

    # خيار إعدادات الصباح العمودية المحسوبة
    if data == "morning_settings":
        settings = await conn.fetchrow("SELECT * FROM morning_settings WHERE user_id = $1", user_id)
        msg_txt = (
            f"👑 **أرامكي للحلول الرقمية | فرع نواة الذهب**\n"
            f"───────────────────\n"
            f"☀️ **صباح الرزق والسعادة والبركة يا طيب!**\n"
            f"نسأل الله أن يجعل هذا اليوم مباركاً، مليئاً بالخير الوفير لعملكم وحلالكم الطيب. ✨\n\n"
            f"📋 **إعدادات الصباح الحالية لمحلك العامر:**\n\n"
            f"🔹 سعر مثقال عيار 24: {settings['price_24']:,} دينار\n"
            f"🔹 سعر مثقال عيار 21: {settings['price_21']:,} دينار\n"
            f"🔹 سعر مثقال عيار 18: {settings['price_18']:,} دينار\n"
            f"🔨 أجور صياغة غرام 24: {settings['making_24']:,} دينار\n"
            f"🔨 أجور صياغة غرام 21: {settings['making_21']:,} دينار\n"
            f"🔨 أجور صياغة غرام 18: {settings['making_18']:,} دينار\n"
            f"💵 سعر الـ 100 دولار المتداول: {settings['usd_rate']:,} دينار\n\n"
            f"💡 **لتحديث جميع هذه الأسعار بلمحة بصر وسؤال واحد، أرسل الأسعار الجديدة بـ 7 أسطر منفصلة متتالية:**\n"
            f"مثال:\n"
            f"950000\n900000\n800000\n12000\n10000\n8000\n155000"
        )
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 العودة للقائمة", callback_data="back_main")
        await callback.message.edit_text(msg_txt, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await state.set_state(SettingsStates.waiting_for_prices)
        
    elif data == "back_main":
        await state.clear()
        await callback.message.edit_text(
            "👋 يرجى اختيار العملية المطلوبة وتوكل على الرزاق الكافي:",
            reply_markup=get_main_keyboard(user_id == ADMIN_ID)
        )

    # بدء معالجة البيع للزبون
    elif data == "mode_sell":
        await callback.message.answer("⚖️ أرسل الآن الوزن المراد بيعه للزبون بدقة وبدون أي تقريب (مثال: 4.963):")
        await state.set_state(CalculationStates.waiting_for_weight)
        await callback.answer()

    # بدء معالجة الشراء من زبون
    elif data == "mode_buy":
        await callback.message.answer("📥 أرسل الوزن الإجمالي المُراد شراؤه وتصفيته من الزبون بالجرام:")
        await state.set_state(CalculationStates.waiting_for_buy_weight)
        await callback.answer()

    # خَدعة "جاري احتساب العمليات الرقمية..." مع إخراج الفاتورة الفخمة
    elif data.startswith("calc_"):
        await callback.answer()
        parts = data.split("_")
        mode = parts[1]  # sell أو buy
        caliber = int(parts[2])
        
        state_data = await state.get_data()
        weight = state_data.get("weight")
        
        # رسالة الانتظار النفسية الذكية لتغطية ضعف النت بالعراق
        status_msg = await callback.message.answer("⏳ **جاري احتساب العمليات الرقمية وتأمين نفق الاتصال السحابي...**")
        await asyncio.sleep(5)  # مدة 5 ثوانٍ المطلوبة
        
        settings = await conn.fetchrow("SELECT * FROM morning_settings WHERE user_id = $1", user_id)
        goldsmith = await conn.fetchrow("SELECT * FROM goldsmiths WHERE user_id = $1", user_id)
        
        # احتساب النتائج البرمجية الخالية من التقريب
        res = utils.calculate_gold_invoice(weight, caliber, mode, settings)
        await status_msg.delete()
        
        # تنسيق الفاتورة الفخمة مع ذكر تفاصيل الشركة واليوزر المعتمد
        title = "📄 فاتورة بيع ذهب للزبون" if mode == "sell" else "🔥 فاتورة شراء ذهب من زبون"
        charge_label = "🔨 أجور صياغة الغرام:" if mode == "sell" else "🔥 خصم الصهر/أجور غرام:"
        blessing = "🎉 ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب! ✨" if mode == "sell" else "🤝 تمت عملية الشراء بنجاح وشفافية مطلقة! ربي يعوضكم بالخير والرزق الوفير! ✨"
        
        invoice_txt = (
            f"💎 **أرامكي للحلول الرقمية | ARAMKY**\n"
            f"👑 **فرع نواة الذهب لأنظمة الصاغة والأسواق المالية**\n"
            f"───────────────────\n"
            f"✨ **{title}** ✨\n\n"
            f"🔹 **المحل العامر:** {goldsmith['shop_name']}\n"
            f"📍 **الموقع المعتمد:** {goldsmith['location']}\n"
            f"📞 **هاتف المحل:** {goldsmith['phone']}\n"
            f"⚜️ **العيار ونوع الحساب:** عيار {caliber} (حساب بالغرام)\n"
            f"⚖️ **الوزن المطلوب الصافي:** {res['weight']} غرام\n"
            f"{charge_label} {settings[f'making_{caliber}']:,} دينار\n"
            f"💰 **سعر غرام الذهب الصافي:** {res['gram_price']:.2f} دينار\n"
            f"───────────────────\n"
            f"💵 **السعر الكلي بالدينار العراقي:**\n"
            f"👈 `{res['total_iqd']:.2f}` دينار\n\n"
            f"💵 **صافي الحساب بالورق والدينار:**\n"
            f"👈 **{res['papers']} ورقة** و `{res['remaining_iqd']:.2f}` دينار عراقي\n"
            f"───────────────────\n"
            f"{blessing}\n\n"
            f"🤖 **المنظومة الذكية المعتمدة:** {BOT_USER}"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 إجراء عملية حسابية جديدة", callback_data="back_main")
        await callback.message.answer(invoice_txt, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await state.clear()

    # فحص الاشتراك وعرض رسالة الانتهاء الفخمة مع الخصومات والأسعار المخصصة
    elif data == "check_sub":
        if profile['is_free_tier'] and datetime.now() < profile['subscription_ends']:
            rem_days = (profile['subscription_ends'] - datetime.now()).days
            await callback.message.answer(f"🎁 أنت حالياً في الفترة التجريبية المجانية المدعومة سحابياً. متبقي لك: {rem_days} أيام بكامل الصلاحيات الميدانية.")
        elif datetime.now() > profile['subscription_ends']:
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
            await callback.message.answer(f"✅ اشتراكك السحابي المدفوع فعال لغاية: {profile['subscription_ends'].strftime('%Y-%m-%d')}")
        await callback.answer()

    # --- 👑 4️⃣ أدوات وإجراءات لوحة تحكم الإدارة الكاملة الفردية (الأدمن) ---
    elif data == "admin_panel" and user_id == ADMIN_ID:
        users = await conn.fetch("SELECT user_id, shop_name, is_free_tier, is_active FROM goldsmiths")
        builder = InlineKeyboardBuilder()
        for u in users:
            status = "🟢" if u['is_active'] else "🔴"
            builder.button(text=f"{status} {u['shop_name']}", callback_data=f"manage_{u['user_id']}")
        builder.button(text="🔙 خروج", callback_data="back_main")
        builder.adjust(1)
        await callback.message.edit_text("👑 **لوحة تحكم المدير العام - إدارة حسابات الصاغة فردياً:**", reply_markup=builder.as_markup())

    elif data.startswith("manage_") and user_id == ADMIN_ID:
        target_id = int(data.split("_")[1])
        u_info = await conn.fetchrow("SELECT * FROM goldsmiths WHERE user_id = $1", target_id)
        
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
        builder.button(text="➖ تقليص الوقت 7 أيام", callback_data=f"action_sub7_{target_id}")
        builder.button(text="🔒 حظر/تفعيل الصائغ", callback_data=f"action_toggle_{target_id}")
        builder.button(text="🔙 العودة للإدارة", callback_data="admin_panel")
        builder.adjust(1)
        await callback.message.edit_text(info_txt, reply_markup=builder.as_markup(), parse_mode="Markdown")

    elif data.startswith("action_") and user_id == ADMIN_ID:
        parts = data.split("_")
        action = parts[1]
        target_id = int(parts[2])
        
        if action == "cancelfree":
            await conn.execute("UPDATE goldsmiths SET is_free_tier=FALSE, subscription_ends=CURRENT_TIMESTAMP WHERE user_id=$1", target_id)
        elif action == "add30":
            await conn.execute("UPDATE goldsmiths SET subscription_ends = subscription_ends + INTERVAL '30 days' WHERE user_id=$1", target_id)
        elif action == "sub7":
            await conn.execute("UPDATE goldsmiths SET subscription_ends = subscription_ends - INTERVAL '7 days' WHERE user_id=$1", target_id)
        elif action == "toggle":
            await conn.execute("UPDATE goldsmiths SET is_active = NOT is_active WHERE user_id=$1", target_id)
            
        await callback.answer("✅ تم تحديث بيانات الصائغ سحابياً بنجاح تام!")
        await conn.close()
        # العودة المباشرة للوحة التحكم لتحديث البيانات المعروضة
        await handle_callbacks(callback, state)
        return

    await conn.close()

# --- دالة الإقلاع والربط الشاملة في السيرفر بـ Render ---
async def main():
    logging.info("⏳ Connecting and initializing Supabase Database...")
    # تهيئة وبناء الجداول السحابية للمشتركين تلقائياً لتجنب الخلل الإداري
    await utils.init_db()
    
    logging.info("♻️ Starting Bot Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
