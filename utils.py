import aiosqlite
import datetime

DB_NAME = "aramky_gold_nucleus.db"

async def init_and_refresh_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # جدول المستخدمين الشامل لتواريخ الدخول بدقة، الفترات المجانية والمدفوعة، وإعدادات الصباح الشخصية
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                shop_name TEXT DEFAULT '',
                shop_phone TEXT DEFAULT '',
                shop_address TEXT DEFAULT '',
                lang TEXT DEFAULT 'ar',
                m21_price REAL DEFAULT 480000,
                m18_price REAL DEFAULT 410000,
                w21_charge REAL DEFAULT 10000,
                w18_charge REAL DEFAULT 8000,
                usd_rate REAL DEFAULT 153000,
                sub_status TEXT DEFAULT 'trial',
                reg_time TEXT,
                trial_start TEXT,
                trial_end TEXT,
                sub_start TEXT,
                sub_end TEXT
            )
        """)
        # جدول الإعدادات المركزية للماستر (مثل التحكم بالوقت المجاني الافتراضي وترند العمليات)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('default_trial_hours', '168')") # 7 أيام افتراضية
        await db.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('trend_counter', '1452')") # عداد الترند الوهمي
        await db.commit()

async def add_or_update_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            if not await cursor.fetchone():
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                now_date = datetime.datetime.now()
                
                # جلب الوقت المجاني الافتراضي المحدد من قبل الأدمن
                async with db.execute("SELECT value FROM system_config WHERE key = 'default_trial_hours'") as c2:
                    row = await c2.fetchone()
                    hours = int(row[0]) if row else 168
                
                trial_end_date = (now_date + datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
                
                await db.execute("""
                    INSERT INTO users (user_id, username, sub_status, reg_time, trial_start, trial_end, sub_start, sub_end)
                    VALUES (?, ?, 'trial', ?, ?, ?, '', '')
                """, (user_id, username, now_str, now_str, trial_end_date))
                await db.commit()

async def get_user_data(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def update_morning_config(user_id, m21, m18, w21, w18, usd):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users SET m21_price = ?, m18_price = ?, w21_charge = ?, w18_charge = ?, usd_rate = ?
            WHERE user_id = ?
        """, (m21, m18, w21, w18, usd, user_id))
        await db.commit()

async def update_shop_profile(user_id, name, phone, address):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users SET shop_name = ?, shop_phone = ?, shop_address = ? WHERE user_id = ?
        """, (name, phone, address, user_id))
        await db.commit()

async def check_subscription(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT sub_status, trial_end, sub_end FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row: return False
            status, trial_end_str, sub_end_str = row
            
            now = datetime.datetime.now()
            if status == 'active' and sub_end_str:
                if now <= datetime.datetime.strptime(sub_end_str, "%Y-%m-%d %H:%M:%S"):
                    return True
            if trial_end_str:
                if now <= datetime.datetime.strptime(trial_end_str, "%Y-%m-%d %H:%M:%S"):
                    return True
            return False

async def get_trend_number():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT value FROM system_config WHERE key = 'trend_counter'") as cursor:
            row = await cursor.fetchone()
            current = int(row[0]) if row else 1452
            next_val = current + 1
            await db.execute("UPDATE system_config SET value = ? WHERE key = 'trend_counter'", (str(next_val),))
            await db.commit()
            return current

async def admin_get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, username, shop_name, sub_status, trial_end, sub_end FROM users") as cursor:
            return await cursor.fetchall()

async def admin_modify_user_time(user_id, action_type, days):
    async with aiosqlite.connect(DB_NAME) as db:
        now = datetime.datetime.now()
        if action_type == "add_sub":
            future = (now + datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            await db.execute("UPDATE users SET sub_status = 'active', sub_start = ?, sub_end = ? WHERE user_id = ?", 
                             (now.strftime("%Y-%m-%d %H:%M:%S"), future, user_id))
        elif action_type == "reduce_trial":
            # تقليص الوقت الفوري للعميل
            future = (now + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            await db.execute("UPDATE users SET trial_end = ? WHERE user_id = ?", (future, user_id))
        elif action_type == "block":
            past = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            await db.execute("UPDATE users SET sub_status = 'expired', trial_end = ?, sub_end = ? WHERE user_id = ?", (past, past, user_id))
        await db.commit()

async def admin_set_global_trial(hours):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE system_config SET value = ? WHERE key = 'default_trial_hours'", (str(hours),))
        await db.commit()

async def admin_get_global_trial_string():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT value FROM system_config WHERE key = 'default_trial_hours'") as cursor:
            row = await cursor.fetchone()
            hours = int(row[0]) if row else 168
            if hours >= 24:
                return f"{hours // 24} أيام"
            return f"{hours} ساعة"
