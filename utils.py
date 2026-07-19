import aiosqlite
import datetime

DB_NAME = "gold_nucleus.db"

# رسالة الترحيب والشرح الفاخرة المعتمدة لهيبة المنظومة
WELCOME_MESSAGE = (
    "👑 *مرحباً بك في منظومة SMART GOLD SYSTEM الذكية* 👑\n"
    "المنصة الإدارية والحسابية الأولى والأسرع المصممة خصيصاً لأسواق الذهب العريقة في العراق 🇮🇶\n\n"
    "✨ *أبرز مميزات المنظومة الاحترافية:* ✨\n"
    "🔹 *أتمتة قانون المثقال العراقي:* حسابات ذكية تقسم المثقال على 5 غرامات فوراً وتدمج الأجور بدون أي هامش خطأ.\n"
    "🔹 *معادلة الصرف المحلية:* تحويل الحسابات بلحظات إلى فئة (الورقة 100$) والكسور المتبقية بالدينار العراقي.\n"
    "🔹 *الفواتير الرقمية الفاخرة:* إصدار فواتير ترويجية مخيرة تحمل هوية محلك وتدعم انتشار اسم شركتك بالسوق.\n"
    "🔹 *سرعة فائقة (ثوانٍ معدودة):* معالجة سحابية متطورة تنهي تعليق النظام وقفل الشاشات ميدانياً.\n\n"
    "_______________________________\n\n"
    "✨ *يا فتاح يا عليم يا رزاق يا كريم* ✨\n"
    "🎁 مبارك لكم، تم منح حسابكم فترة تجريبية مجانية مدتها 7 أيام لاكتساح السوق ميكانيكياً!\n\n"
    "🤖 يرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق الحكيم 👇"
)

async def init_and_refresh_db():
    """تهيئة قاعدة البيانات وتصفير السجلات لمنح المستخدمين القدامى فترة جديدة"""
    async with aiosqlite.connect(DB_NAME) as db:
        # إنشاء جدول المستخدمين
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                sub_status TEXT DEFAULT 'trial',
                trial_start TEXT,
                sub_end TEXT,
                shop_name TEXT DEFAULT 'محلات الصائغ المعتمد',
                shop_phone TEXT DEFAULT '077XXXXXXXX',
                shop_address TEXT DEFAULT 'بغداد - سوق الكاظمية'
            )
        """)
        # إنشاء جدول الإعدادات المركزية لأسعار الصباح والدولار
        await db.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # وضع قيم افتراضية لأسعار الصباح إذا لم تكن موجودة
        await db.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('mithqal_price', '480000')")
        await db.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('usd_rate', '153000')") # سعر المئة دولار بالدينار
        
        # --- خدعة تصفير السجل المطلوبة ---
        # تحديث كافة الحسابات الحالية لتصبح تجريبية نشطة من تاريخ اليوم وتصفير القيود السابقة
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        fresh_end = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        await db.execute("UPDATE users SET sub_status = 'trial', trial_start = ?, sub_end = ?", (now, fresh_end))
        
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

async def get_shop_details(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT shop_name, shop_phone, shop_address FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def update_shop_details(user_id, name, phone, address):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET shop_name = ?, shop_phone = ?, shop_address = ? WHERE user_id = ?", (name, phone, address, user_id))
        await db.commit()

async def get_system_config():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT key, value FROM system_config") as cursor:
            rows = await cursor.fetchall()
            return {r[0]: float(r[1]) for r in rows}

async def update_system_config(mithqal, usd):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE system_config SET value = ? WHERE key = 'mithqal_price'", (str(mithqal),))
        await db.execute("UPDATE system_config SET value = ? WHERE key = 'usd_rate'", (str(usd),))
        await db.commit()

# --- دالة الحساب المعتمدة على قانون المثقال والورقة العراقية ---
def calculate_iraqi_gold(weight_grams, workmanship_per_gram, mithqal_price, usd_exchange_rate):
    """
    قانون المثقال = سعر المثقال / 5 غرامات لإخراج سعر الغرام الصافي.
    إجمالي السعر بالدينار = (سعر الغرام الصافي + أجور الصياغة للغرام) * الوزن بالغرام.
    تحويل العملة = تقسيم الإجمالي على سعر الورقة (100 دولار) لإخراج عدد الأوراق والباقي بالدينار العراقي.
    """
    gram_base_price = mithqal_price / 5.0
    total_gram_cost = gram_base_price + workmanship_per_gram
    total_price_iqd = total_gram_cost * weight_grams
    
    # حسبة السوق: كم ورقة والباقي عراقي
    # سعر الدولار الفردي = سعر الورقة / 100
    single_usd_rate = usd_exchange_rate / 100.0
    total_usd_value = total_price_iqd / single_usd_rate
    
    waraqa_count = int(total_usd_value // 100)
    remaining_usd = total_usd_value % 100
    remaining_iqd = remaining_usd * single_usd_rate
    
    return round(gram_base_price, 2), round(total_price_iqd, 0), waraqa_count, round(remaining_iqd, 0)

# أدوات الإدارة المطلوبة للسيطرة المطلقة
async def db_manage_user_status(user_id, status, days=30):
    end_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET sub_status = ?, sub_end = ? WHERE user_id = ?", (status, end_date, user_id))
        await db.commit()

async def db_get_all_users_full():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, username, sub_status, sub_end FROM users") as cursor:
            return await cursor.fetchall()
