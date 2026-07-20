import aiosqlite
import datetime

DB_NAME = "aramky_gold_nucleus.db"

async def init_and_refresh_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # جدول المستخدمين الشامل لبيانات المحل والأسعار الخاصة بكل صائغ
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                sub_status TEXT DEFAULT 'trial',
                trial_start TEXT,
                sub_end TEXT,
                shop_name TEXT DEFAULT 'محلات الصائغ المعتمد',
                shop_phone TEXT DEFAULT '077XXXXXXXX',
                shop_address TEXT DEFAULT 'بغداد - سوق الكاظمية',
                lang TEXT DEFAULT 'ar',
                m21_price REAL DEFAULT 480000,
                m18_price REAL DEFAULT 410000,
                usd_rate REAL DEFAULT 153000
            )
        """)
        await db.commit()

async def add_or_update_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            if not await cursor.fetchone():
                now = datetime.datetime.now().strftime("%Y-%m-%d")
                trial_end = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
                await db.execute(
                    "INSERT INTO users (user_id, username, sub_status, trial_start, sub_end) VALUES (?, ?, 'trial', ?, ?)",
                    (user_id, username, now, trial_end)
                )
                await db.commit()

async def check_subscription(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT sub_status, sub_end FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row: return False
            status, end_date_str = row
            if status == 'active': return True
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            if datetime.datetime.now() <= end_date: return True
            return False

async def get_user_data(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def update_morning_prices(user_id, m21, m18, usd):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET m21_price = ?, m18_price = ?, usd_rate = ? WHERE user_id = ?", (m21, m18, usd, user_id))
        await db.commit()

async def update_shop_profile(user_id, name, phone, address):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET shop_name = ?, shop_phone = ?, shop_address = ? WHERE user_id = ?", (name, phone, address, user_id))
        await db.commit()

async def update_user_lang(user_id, lang):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
        await db.commit()

def calculate_gold(weight, workmanship, mithqal_price, usd_rate):
    # قانون المثقال العراقي: المثقال يساوي 5 غرامات
    gram_base = mithqal_price / 5.0
    total_gram_cost = gram_base + workmanship
    total_iqd = total_gram_cost * weight
    
    # حسبة الورق الموازي بالسوق
    usd_single_rate = usd_rate / 100.0
    total_usd = total_iqd / usd_single_rate
    waraqa = int(total_usd // 100)
    remain_iqd = (total_usd % 100) * usd_single_rate
    
    return gram_base, total_iqd, waraqa, remain_iqd

async def db_get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, username, sub_status, sub_end FROM users") as cursor:
            return await cursor.fetchall()

async def db_set_status(user_id, status, days=30):
    end_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET sub_status = ?, sub_end = ? WHERE user_id = ?", (status, end_date, user_id))
        await db.commit()
