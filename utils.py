import aiosqlite
import logging
from datetime import datetime, timedelta

DB_NAME = "nawat_al_dhahab.db"

# النصوص الرسمية للترحيب وشرح النظام باللغات الثلاث
LANG_TEXTS = {
    'ar': {
        'welcome': (
            "👑 **ARAMKY | أرامكي للحلول الرقمية**\n"
            "✨ *فرع نواة الذهب لأنظمة الصاغة والأسواق المالية*\n\n"
            "مرحباً بك يا طيب في منظومتك الإدارية الأسرع والأدق! 🚀\n"
            "تم تصميم هذا النظام خصيصاً لتبسيط وجرد عمليات الصياغة اليومية بدقة متناهية.\n\n"
            "⚙️ **مميزات المنظومة:**\n"
            "1. احتساب الفواتير الفورية (بيع وشراء) بالدينار والورق.\n"
            "2. اعتماد أوزان المثقال الشرعي بدقة (مثقال 21 = 5 غرام، ومثقال 18 أقل من 21).\n"
            "3. إدارة الإعدادات الصباحية وجرد الأوزان المخزنة.\n\n"
            "🎁 تم تفعيل الفترة التجريبية المجانية الخاصة بك!"
        ),
        'expired': (
            "⚠️ **شريكنا العزيز.. انتهت الفترة التجريبية المخصصة للمنظومة.**\n\n"
            "للاشتراك وتمديد الصلاحية بالسعر التنافسي المستمر بقيمة **105,000 دينار عراقي فقط** بدلاً من 133,000 دينار.\n\n"
            "🏦 **حساب الإيداع المالي الذهبي للشركة:**\n"
            "💳 رقم الماستر كارد الرسمي المعتمد: `910400201646`\n\n"
            "📸 بعد التحويل، يرجى الضغط على زر **(إرسال وصل التحويل)** وإرفاق صورة الوصل لتفعيل حسابك تلقائياً.\n"
            "📞 خط الدعم الفني: `07872180902`"
        )
    },
    'ku': {
        'welcome': (
            "👑 **ARAMKY | چارەسەرە دیجیتاڵییەکان**\n"
            "✨ *لقی ناوکی زێڕ بۆ سیستەمی زێڕنگەران و بازاڕە داراییەکان*\n\n"
            "بەخێربێیت هاوڕێی بەڕێزم بۆ ناو سیستەمی بەڕێوەبردنی خێرا و ورد! 🚀\n"
            "ئەم سیستەمە بە تایبەت دیزاین کراوە بۆ ئاسانکاری و جەردی کارەکانی ڕۆژانە.\n\n"
            "🎁 ماوەی تاقیکردنەوەی بێ بەرامبەر چالاک کرا!"
        ),
        'expired': (
            "⚠️ **هاوبەشی بەڕێز.. ماوەی تاقیکردنەوەی سیستەمەکەت کۆتایی هات.**\n\n"
            "بۆ نوێکردنەوەی بەشداریکردن بە نرخی **105,000 دیناری عێراقی**.\n"
            "💳 ژمارەی ماستەرکاردی فەرمی: `910400201646`\n"
            "📸 تکایە وێنەی پسوڵەی گواستنەوە بنێرە."
        )
    },
    'en': {
        'welcome': (
            "👑 **ARAMKY | Digital Solutions**\n"
            "✨ *Nawat Al-Dhahab Branch for Goldsmiths & Financial Systems*\n\n"
            "Welcome to your fastest and most accurate administrative system! 🚀\n"
            "Designed specifically to streamline daily goldsmith operations and inventory.\n\n"
            "🎁 Your free trial period has been activated!"
        ),
        'expired': (
            "⚠️ **Dear Partner.. Your system trial period has expired.**\n\n"
            "To subscribe and extend validity, the price is **105,000 IQD only**.\n"
            "💳 Official Master Card: `910400201646`\n"
            "📸 Please send the transfer receipt image to activate your account."
        )
    }
}

async def init_and_refresh_db():
    """تهيئة قاعدة البيانات وجداول العملاء والإدارة والمخازن"""
    async with aiosqlite.connect(DB_NAME) as db:
        # جدول المستخدمين (العملاء الصاغة)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                shop_name TEXT,
                location TEXT,
                phone TEXT,
                lang TEXT DEFAULT 'ar',
                trial_ends TEXT,
                is_active INTEGER DEFAULT 1,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # جدول الإعدادات الصباحية المخصصة لكل صائغ (اختيارية)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS shop_settings (
                user_id INTEGER PRIMARY KEY,
                gold_21_buy REAL DEFAULT 900000,
                gold_18_buy REAL DEFAULT 450000,
                making_21 REAL DEFAULT 10000,
                making_18 REAL DEFAULT 1000,
                usd_rate REAL DEFAULT 155000
            )
        """)
        await db.commit()

async def register_user(user_id, shop_name, location, phone):
    """تسجيل العميل وإعطائه فترة تجريبية 7 أيام"""
    trial_ends = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (user_id, shop_name, location, phone, trial_ends, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET shop_name=?, location=?, phone=?
        """, (user_id, shop_name, location, phone, trial_ends, shop_name, location, phone))
        
        # إنشاء إعدادات افتراضية له
        await db.execute("""
            INSERT OR IGNORE INTO shop_settings (user_id) VALUES (?)
        """, (user_id,))
        await db.commit()
    return trial_ends

async def check_user_status(user_id):
    """التحقق من حالة اشتراك العميل"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT is_active, trial_ends, lang FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return "NOT_REGISTERED", 'ar'
            
            is_active, trial_ends_str, lang = row
            if is_active == 0:
                return "SUSPENDED", lang
            
            trial_ends = datetime.strptime(trial_ends_str, "%Y-%m-%d %H:%M:%S")
            if datetime.now() > trial_ends:
                return "EXPIRED", lang
            
            return "ACTIVE", lang

async def update_settings(user_id, g21, g18, m21, m18, usd):
    """تحديث الأسعار الصباحية الخاصة بمحل العميل"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO shop_settings (user_id, gold_21_buy, gold_18_buy, making_21, making_18, usd_rate)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
                gold_21_buy=?, gold_18_buy=?, making_21=?, making_18=?, usd_rate=?
        """, (user_id, g21, g18, m21, m18, usd, g21, g18, m21, m18, usd))
        await db.commit()

async def get_shop_settings(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT gold_21_buy, gold_18_buy, making_21, making_18, usd_rate FROM shop_settings WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_total_users_count():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0

async def admin_modify_trial(user_id, days_to_add):
    """خاص بالادمن: زيادة الفترة المجانية للعميل"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT trial_ends FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                current_ends = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                new_ends = (current_ends if current_ends > datetime.now() else datetime.now()) + timedelta(days=days_to_add)
                await db.execute("UPDATE users SET trial_ends = ?, is_active = 1 WHERE user_id = ?", (new_ends.strftime("%Y-%m-%d %H:%M:%S"), user_id))
                await db.commit()
                return True
    return False

async def admin_suspend_user(user_id):
    """إيقاف فوري لاشتراك عميل وتوجيهه لطلب الدفع"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET is_active = 0 WHERE user_id = ?", (user_id,))
        await db.commit()
