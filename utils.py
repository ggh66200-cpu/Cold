import aiosqlite
import logging

DB_NAME = "nawat_al_dhahab.db"

async def init_and_refresh_db():
    """تهيئة قاعدة البيانات المتكاملة بنظام أرامكي الفاخر"""
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            # جدول المستخدمين والتسجيل الأول واللغات
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    shop_name TEXT,
                    location TEXT,
                    phone TEXT,
                    lang TEXT DEFAULT 'ar',
                    is_admin INTEGER DEFAULT 0,
                    is_registered INTEGER DEFAULT 0,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول الأسعار الصباحية المخزن من قبل الإدارة
            await db.execute("""
                CREATE TABLE IF NOT EXISTS morning_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gold_price_21 REAL,
                    gold_price_18 REAL,
                    wage_21 REAL,
                    wage_18 REAL,
                    usd_rate REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول الفواتير والجرد للعمليات
            await db.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT, -- 'purchase' or 'sell'
                    client_name TEXT,
                    weight_18 REAL,
                    weight_21 REAL,
                    total_iqd REAL,
                    total_usd_papers REAL,
                    remaining_iqd REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
            logging.info("👑 تم تهيئة نظام البيانات وجرد الفواتير لشركة أرامكي بنجاح.")
    except Exception as e:
        logging.error(f"❌ خطأ في قاعدة البيانات: {e}")

async def get_user_data(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()

async def register_user(user_id: int, username: str, shop_name: str, location: str, phone: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, shop_name, location, phone, is_registered) 
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET shop_name=?, location=?, phone=?, is_registered=1
        """, (user_id, username, shop_name, location, phone, shop_name, location, phone))
        await db.commit()

async def update_user_lang(user_id: int, lang: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
        await db.commit()

async def get_latest_prices():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM morning_settings ORDER BY id DESC LIMIT 1")
        return await cursor.fetchone()

async def save_invoice(user_id: int, inv_type: str, weight_18: float, weight_21: float, total_iqd: float, usd_papers: float, rem_iqd: float):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO invoices (user_id, type, weight_18, weight_21, total_iqd, total_usd_papers, remaining_iqd)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, inv_type, weight_18, weight_21, total_iqd, usd_papers, rem_iqd))
        await db.commit()

def calculate_gold_mechanics(weight_18: float, weight_21: float, price_21: float, wage: float, usd_rate: float):
    """حساب الميكانيكية الذهبية المتوافقة مع صياغة عيار 18 وعيار 21"""
    # تحويل عيار 18 إلى ما يكافئه من عيار 21 (18 / 21)
    converted_18_to_21 = weight_18 * (18.0 / 21.0)
    total_pure_weight_21 = converted_18_to_21 + weight_21
    
    # حساب المثاقيل (المثقال = 5 غرام)
    total_mitqals = total_pure_weight_21 / 5.0
    
    # حساب المبالغ
    pure_price_per_gram = price_21 / 5.0
    total_gold_value = total_pure_weight_21 * pure_price_per_gram
    total_wages = (weight_18 + weight_21) * wage
    grand_total_iqd = total_gold_value + total_wages
    
    # تقسيم المبلغ العراقي إلى أوراق فئة 100 دولار وباقي عراقي
    usd_value_of_100 = usd_rate # سعر الـ 100 دولار بالدينار
    total_usd_papers = int(grand_total_iqd // usd_value_of_100)
    remaining_iqd = grand_total_iqd % usd_value_of_100
    
    return total_pure_weight_21, total_mitqals, grand_total_iqd, total_usd_papers, remaining_iqd
