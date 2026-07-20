import aiosqlite
import logging
from datetime import datetime, timedelta

DB_NAME = "nawat_al_dhahab.db"

# نصوص ترحيبية وتعريفية بالشركة باللغات الثلاث
INTRO_TEXTS = {
    'ar': (
        "💎 أرامكي للحلول الرقمية | ARAMKY\n"
        "⚜️ فرع نواة الذهب لأنظمة الصاغة الذكية\n\n"
        "أهلاً بك يا طيب في منظومتك الإدارية الأسرع والأدق بالأسواق العريقة!\n"
        "نظام متكامل يتيح لك إدارة فواتير البيع والشراء، جرد المخازن، والاطلاع على الأسعار الصباحية بدقة متناهية وفق الأعراف التجارية العراقية."
    ),
    'ku': (
        "💎 ARAMKY بۆ چارەسەرە دیجیتاڵییەکان\n"
        "⚜️ لقی ناوکی زێڕ بۆ سیستمە زیرەکەکانی زێڕنگەری\n\n"
        "بەخێرهاتنت دەکەین هاوڕێی بەڕێز لە خێراترین و وردترین سیستمی کارگێڕی بازاڕ!\n"
        "سیستمێکی گشتگیر بۆ بەڕێوەبردنی پسوڵەی کڕین و فرۆشتن و وردبینی کۆگا."
    ),
    'en': (
        "💎 ARAMKY for Digital Solutions\n"
        "⚜️ Nawat Al-Dhahab Branch for Smart Goldsmith Systems\n\n"
        "Welcome to the fastest and most precise management system in the market!\n"
        "A comprehensive system to manage buying and selling invoices, inventory, and morning updates."
    )
}

async def init_and_refresh_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # جدول العملاء (التجار والصاغة) مع إدارة الاشتراكات
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
        # جدول الأسعار الصباحية لكل عميل بشكل اختياري
        await db.execute("""
            CREATE TABLE IF NOT EXISTS morning_prices (
                user_id INTEGER PRIMARY KEY,
                gold_21_buy REAL DEFAULT 0,
                gold_18_buy REAL DEFAULT 0,
                 صياغة_21 REAL DEFAULT 0,
                صياغة_18 REAL DEFAULT 0,
                usd_rate REAL DEFAULT 0
            )
        """)
        await db.commit()
        logging.info("✅ تم تهيئة وجرد قاعدة بيانات نواة الذهب بنجاح.")

async def register_user(user_id, shop_name, location, phone, lang='ar'):
    # إعطاء 7 أيام فترة تجريبية افتراضية للفخامة الميدانية
    trial_ends = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (user_id, shop_name, location, phone, lang, trial_ends, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET 
                shop_name=col.shop_name, location=col.location, phone=col.phone
        """, (user_id, shop_name, location, phone, lang, trial_ends))
        # إنشاء سجل أسعار افتراضي
        await db.execute("INSERT OR IGNORE INTO morning_prices (user_id) VALUES (?)", (user_id,))
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_user_prices(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM morning_prices WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def update_user_lang(user_id, lang):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
        await db.commit()

async def check_trial(user_id):
    user = await get_user(user_id)
    if not user:
        return False, "unregistered"
    if user['is_active'] == 0:
        return False, "suspended"
    
    end_date = datetime.strptime(user['trial_ends'], "%Y-%m-%d %H:%M:%S")
    if datetime.now() > end_date:
        return False, "expired"
    return True, "active"
