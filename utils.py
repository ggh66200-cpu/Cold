# utils.py
import time
import random

# دعم اللغات الثلاث (العربية، الكردية، الإنجليزية)
LANG_PACKS = {
    'ar': {
        'welcome': "✨ أهلاً بك في نظام الـنـواة الـذهـبـيـة للمجوهرات والذهب ✨\nنظامك المساعد لإدارة حساباتك وفواتيرك بكل دقة وسرعة.",
        'trial_msg': "🎁 فترتك التجريبية المجانية الحالية هي: {}",
        'loading': "⚡ جاري تحميل العمليات الذهبية وتحديث أسعار السوق العراقي... ⏳",
        'register_start': "📝 يرجى ملء استمارة المعلومات للبدء فورا:",
        'locked': "🔒 النظام مقفل حالياً. يرجى تفعيل الاشتراك أو التواصل مع الإدارة للاستمرار.",
        'invoice_title': "⚜️ فاتورة عميل - مجوهرات الذهب ⚜️"
    },
    'ku': {
        'welcome': "✨ بەخێربێن بۆ سیستەمی ناوکی زێڕین بۆ زێڕینگەری و زێڕ ✨\nسیستەمی یاریدەدەرەت بۆ بەڕێوەبردنی حسابات و پسووڵەکانت بە وردی.",
        'trial_msg': "🎁 ماوەی تاقیکردنەوەی بێبەرامبەری ئێستات: {}",
        'loading': "⚡ کارە زێڕینەکان باردەکرێن و نرخی بازاڕی عێراق نوێ دەکرێتەوە... ⏳",
        'register_start': "📝 تکایە فۆرمی زانیارییەکان پڕبکەرەوە بۆ دەستپێکردن:",
        'locked': "🔒 سیستەمەکە ئێستا قفڵە. تکایە بەشدارییەکەت چالاک بکە یان پەیوەندی بە بەڕێوبەرایەتییەوە بکە.",
        'invoice_title': "⚜️ پسووڵەی کڕیار - زێڕینگەری ⚜️"
    },
    'en': {
        'welcome': "✨ Welcome to the Gold Nucleus System for Jewelry & Gold ✨\nYour assistant system for precise and fast accounting and invoicing.",
        'trial_msg': "🎁 Your current free trial period is: {}",
        'loading': "⚡ Loading golden operations and updating Iraqi market rates... ⏳",
        'register_start': "📝 Please fill out the information form to start immediately:",
        'locked': "🔒 The system is currently locked. Please activate your subscription or contact admin.",
        'invoice_title': "⚜️ Customer Invoice - Gold Jewelry ⚜️"
    }
}

# تصفير الملفات القديمة وبيانات المشترك القديمة للبدء بنظافة
def reset_user_session(user_id, database):
    """تصفير بيانات الجلسة الحالية وإعادة تعيئة الحقول"""
    database[user_id] = {
        'status': 'pending_registration',
        'lang': 'ar',
        'region': 'غير محدد',
        'trial_end': 0,
        'is_active': False,
        'step': 'name'
    }
    return database[user_id]

# تحويل وتنسيق العملة (100 دولار = ورقة، والكسور/الباقي بالدينار العراقي)
def format_currency_iqd_usd(usd_amount, exchange_rate=1500):
    """
    حساب المبلغ: الـ 100 دولار تحسب (ورقة) والباقي بالدينار العراقي مع الكسور.
    """
    papers = int(usd_amount // 100)
    remaining_usd = usd_amount % 100
    iqd_equivalent = remaining_usd * exchange_rate
    
    result = ""
    if papers > 0:
        result += f"💵 {papers} ورقة "
    if iqd_equivalent > 0:
        if papers > 0:
            result += " و "
        result += f"{iqd_equivalent:,.0f} دينار عراقي"
    
    return result if result else "0 دينار"

# توليد الرقم الترند المميز للفواتير (يعطي هيبة وقوة للشركة)
def generate_trend_number():
    prefix = "TRND"
    random_num = random.randint(10000, 99999)
    return f"⚡ #{prefix}-{random_num}"

# 📄 أولاً: فاتورة آرامكي الموجهة لصاحب محل الذهب (العميل الخاص بك)
def generate_aramky_invoice(user_id, shop_name, plan_name, duration_str):
    trend = generate_trend_number()
    invoice = (
        f"👑 *آرامكي للحلول الرقمية - فرع نواة الذهب* 👑\n"
        f"----------------------------------------\n"
        f"🧾 *فاتورة تفعيل نظام المشترك*\n"
        f"🔢 الرقم الترند: `{trend}`\n"
        f"🏪 اسم المحل: {shop_name}\n"
        f"🆔 معرف الحساب: `{user_id}`\n"
        f"📦 الباقة: {plan_name}\n"
        f"⏳ الصلاحية: {duration_str}\n"
        f"----------------------------------------\n"
        f"💰 *قيمة الاشتراك الرسمي:* \n"
        f"❌ السعر الأساسي: 133,000 د.ع\n"
        f"✅ السعر الحالي المدعوم: 105,000 د.ع فقط لا غير.\n"
        f"----------------------------------------\n"
        f"🚀 *شكراً لثقتكم بنواة الذهب. نظامكم مفعل وجاهز للانطلاق.*"
    )
    return invoice

# 📄 ثانياً: فاتورة المحل الموجهة لزبائنهم (تظهر قوة النظام وتحتوي رابط البوت)
def generate_customer_invoice(shop_name, client_name, gold_weight, total_usd, lang='ar'):
    trend = generate_trend_number()
    currency_text = format_currency_iqd_usd(total_usd)
    
    title = LANG_PACKS[lang]['invoice_title']
    
    invoice = (
        f"👑 *{shop_name}* 👑\n"
        f"✨ {title} ✨\n"
        f"----------------------------------------\n"
        f"🔢 رقم العملية (الترند): `{trend}`\n"
        f"👤 اسم الزبون: {client_name}\n"
        f"⚖️ وزن الذهب: {gold_weight} غرام\n"
        f"💵 الإجمالي الاحتسابي: ${total_usd}\n"
        f"💰 القيمة الموازية: {currency_text}\n"
        f"----------------------------------------\n"
        f"🤖 تم الحساب والتنظيم رقمياً عبر البوت الرسمي:\n"
        f"🔗 @GoldenCalc_Bot\n"
        f"💎 *نظام نواة الذهب - خيار النخبة لإدارة المجوهرات.*"
    )
    return invoice
