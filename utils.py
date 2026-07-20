import aiosqlite
import logging

DB_NAME = "nawat_al_dhahab.db"

async def init_and_refresh_db():
    """تهيئة قاعدة البيانات بهيكلية معززة تدعم الفترات التجريبية وجرد العملاء الفاخر"""
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            # جدول العملاء مع تفاصيل التسجيل والفترة التجريبية والحالة المالية
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    shop_name TEXT,
                    location TEXT,
                    phone TEXT,
                    lang TEXT DEFAULT 'ar',
                    is_active INTEGER DEFAULT 1,
                    trial_days INTEGER DEFAULT 7,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول الأسعار الصباحية المركزية المعتمدة
            await db.execute("""
                CREATE TABLE IF NOT EXISTS morning_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gold_21_price REAL DEFAULT 900000,
                    gold_18_price REAL DEFAULT 450000,
                    making_21 REAL DEFAULT 10000,
                    making_18 REAL DEFAULT 1000,
                    usd_rate REAL DEFAULT 155000,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # إدراج سطر إعدادات افتراضي إذا كانت قاعدة البيانات فارغة
            async with db.execute("SELECT COUNT(*) FROM morning_settings") as cursor:
                if (await cursor.fetchone())[0] == 0:
                    await db.execute("""
                        INSERT INTO morning_settings (gold_21_price, gold_18_price, making_21, making_18, usd_rate)
                        VALUES (900000, 450000, 10000, 1000, 155000)
                    """)
            
            await db.commit()
            logging.info("✅ تم تهيئة وجرد قاعدة البيانات وهيكلتها بنجاح تام.")
    except Exception as e:
        logging.error(f"❌ خطأ أثناء تهيئة قاعدة البيانات: {e}")

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def register_user(user_id: int, shop_name: str, location: str, phone: str, lang: str = 'ar'):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (user_id, shop_name, location, phone, lang, is_active, trial_days)
            VALUES (?, ?, ?, ?, ?, 1, 7)
            ON CONFLICT(user_id) DO UPDATE SET shop_name=?, location=?, phone=?
        """, (user_id, shop_name, location, phone, lang, shop_name, location, phone))
        await db.commit()

async def update_user_lang(user_id: int, lang: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
        await db.commit()

async def get_morning_prices():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM morning_settings ORDER BY id DESC LIMIT 1") as cursor:
            return await cursor.fetchone()

async def update_morning_prices(g21, g18, m21, m18, usd):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE morning_settings 
            SET gold_21_price=?, gold_18_price=?, making_21=?, making_18=?, usd_rate=?
            WHERE id = 1
        """, (g21, g18, m21, m18, usd))
        await db.commit()

async def change_user_status(user_id: int, status: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET is_active = ? WHERE user_id = ?", (status, user_id))
        await db.commit()

async def get_all_users_count():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0
