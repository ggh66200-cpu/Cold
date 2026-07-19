import aiosqlite
import datetime

DB_NAME = "gold_calc.db"

# النصوص والترحيبات الفاخرة باللغة العربية (ويمكنك قياس الكردية والإنجليزية عليها)
LANGUAGES = {
    "ar": {
        "welcome": (
            "✨ *يا فتاح يا عليم يا رزاق يا كريم* ✨\n\n"
            "أهلاً ومرحباً بك يا طيب في منظومتك الإدارية الأسرع والأدق بالأسواق العريقة! 🌸\n\n"
            "🎁 *رزقكم مبارك*، وتم تفعيل الفترة التجريبية المجانية المدتّها 7 أيام لك تجتاح بها السوق ميدانياً!\n\n"
            "🔢 *رقم الصائغ المعتمد:* #168\n"
            "📍 *المحل العامر:* محلات محمد جايم\n"
            "🗺️ *الموقع:* بغداد - سوق الكاظمية التجاري\n"
            "📞 *الهاتف المعتمد:* 789\n\n"
            "👥 *المشتركين النشطين في الكار الآن:* 167 صائغ\n"
            "_______________________________\n\n"
            "🤖 يرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق 👇"
        ),
        "main_menu": "القائمة الرئيسية 👑",
        "no_sub": (
            "👑 *منظومة آرامكي للحلول الرقمية - فرع نواة الذهب* 👑\n\n"
            "زميلنا الصائغ المحترم.. نود إعلامكم بأن الفترة التجريبية المخصصة لحسابكم قد انتهت صلاحيتها الزوجية.\n"
            "حرصاً على استمرار دقة حساباتكم اليومية وتفادي أي تأخير في تنظيم فواتير محلك العامر، يرجى تجديد الاشتراك السنوي/الشهري.\n\n"
            " الباقة الذهبية المعتمدة حالياً:\n"
            "💰 *105,000 دينار عراقي شهرياً فقط* (بدلاً من السعر الأساسي المقدر بـ 133,000 د.ع).\n\n"
            "📞 للتفعيل الفوري وتلقي كود التجديد، يرجى التواصل مباشرة مع الإدارة الفنية لنواة الذهب."
        ),
        "enter_weight": "⚖️ يرجى إدخال وزن الذهب الحالي بالجرام:",
        "enter_karat": "👑 يرجى اختيار عيار الذهب المطلوب:",
        "enter_workmanship": "🛠️ يرجى إدخال أجور الصياغة المعتمدة لكل جرام (بالدينار العراقي):",
        "loading": "⏳ جاري تدقيق أسعار السوق وحساب العمليات المعتمدة...",
        "result_title": "✨ *النتيجة الحسابية الرسمية المعتمدة* ✨\n\n",
        "invoice_header": "📜 *فاتورة رقمية فاخرة - صادرة عن SMART GOLD SYSTEM* 📜\n\n"
    }
}

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                lang TEXT DEFAULT 'ar',
                sub_status TEXT DEFAULT 'trial',
                trial_start TEXT,
                sub_end TEXT
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
                    "INSERT INTO users (user_id, username, lang, sub_status, trial_start, sub_end) VALUES (?, ?, 'ar', 'trial', ?, ?)",
                    (user_id, username, now, trial_end)
                )
                await db.commit()

async def get_user_lang(user_id):
    return 'ar'  # افتراضي للسرعة والتركيز على الواجهة العربية الحالية المطلوبة بالسوق

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

async def get_subscription_details(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT sub_status, sub_end FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def db_activate_trial(user_id, days=7):
    new_end = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET sub_status = 'trial', sub_end = ? WHERE user_id = ?", (new_end, user_id))
        await db.commit()

async def db_add_subscription(user_id, days=30):
    new_end = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET sub_status = 'active', sub_end = ? WHERE user_id = ?", (new_end, user_id))
        await db.commit()

async def db_get_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c1: total = (await c1.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE sub_status = 'active'") as c2: active = (await c2.fetchone())[0]
        return total, active

async def db_get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            return [r[0] for r in await cursor.fetchall()]

def calculate_gold_price(weight, karat, workmanship, global_price_per_gram, calc_type="sell"):
    """
    حساب الذهب المطور: يراعي نوع العملية (بيع للزبون أو شراء سريع من الزبون)
    """
    karat_purities = {24: 1.0, 22: 0.916, 21: 0.875, 18: 0.750}
    purity = karat_purities.get(karat, 0.875)
    
    base_price = weight * (global_price_per_gram * purity)
    
    if calc_type == "sell":
        total_workmanship = weight * workmanship
        final_price = base_price + total_workmanship
    else:
        # في حالة الشراء السريع من الزبون يتم خصم أجور الصياغة أو حساب صافي الوزن والذهب
        total_workmanship = 0 
        final_price = base_price
        
    return round(base_price, 2), round(total_workmanship, 2), round(final_price, 2)
