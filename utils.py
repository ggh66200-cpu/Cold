import aiosqlite
import datetime

DB_NAME = "gold_calc.db"

# قاموس اللغات الكامل المعتمد للنظام لمنع أي نقص في الواجهات
LANGUAGES = {
    "ar": {
        "welcome": "أهلاً بك في بوت الحاسبة الذهبية من آرامكي للحلول الرقمية ✨\nيرجى اختيار الإجراء من القائمة أدناه:",
        "select_lang": "الرجاء اختيار اللغة / التكافية زماني هلبژيرن:",
        "main_menu": "القائمة الرئيسية 👑",
        "calc_gold": "🧮 حساب الذهب",
        "subscribe_status": "💳 حالة الاشتراك",
        "make_invoice": "🧾 إصدار فاتورة فاخرة",
        "no_sub": "⚠️ عذراً، يجب تفعيل الاشتراك للاستمرار. الاشتراك الحالي منتهي أو غير فعال.",
        "trial_msg": "انتهت الفترة التجريبية. سعر الاشتراك الحالي هو 105,000 دينار عراقي شهرياً (بدلاً من 133,000 د.ع).",
        "enter_weight": "يرجى إدخال وزن الذهب بالجرام:",
        "enter_karat": "يرجى اختيار العيار (18، 21، 22، 24):",
        "enter_workmanship": "يرجى إدخال أجور الصياغة لكل جرام (بالدينار):",
        "loading": "جاري المعالجة والحساب... ⏳",
        "result_title": "👑 النتيجة الحسابية المعتمدة 👑\n\n",
        "invoice_header": "📜 فاتورة رقمية فاخرة - نواة الذهب 📜\n"
    },
    "ku": {
        "welcome": "سلاو، بەخێربێن بۆ بۆتی حاسیبەی زێڕین لە ئارامکی ✨\nتکایە کارێک لە لیستی خوارەوە هەڵبژێرە:",
        "select_lang": "تکایە زمانێک هەڵبژێرە:",
        "main_menu": "پێڕستی سەرەکی 👑",
        "calc_gold": "🧮 ئەژمارکردنی زێڕ",
        "subscribe_status": "💳 دۆخی بەشداری",
        "make_invoice": "🧾 دەرکردنی پسوولە",
        "no_sub": "⚠️ ببورە، پێویستە بەشدارییەکەت چالاک بکەیت بۆ بەردەوامبوون.",
        "trial_msg": "ماوەی تاقیکاری کۆتایی هاتووە. نرخی بەشداری 105,000 دیناری عێراقییە لە مانگێکدا.",
        "enter_weight": "تکایە کێشی زێڕەکە بە گرام بنووسە:",
        "enter_karat": "تکایە عەیار هەڵبژێرە (18، 21، 22، 24):",
        "enter_workmanship": "تکایە کرێی دروستکردن بۆ هەر گرامێک بنووسە:",
        "loading": "خەریکە ئەژمار دەکرێت... ⏳",
        "result_title": "👑 ئەنجامی ئەژمارکردن 👑\n\n",
        "invoice_header": "📜 پسوولەی دیجیتاڵی شاهانە - ناووکی زێڕ 📜\n"
    },
    "en": {
        "welcome": "Welcome to Golden Calculator Bot by ARAMKY ✨\nPlease select an option from the menu below:",
        "select_lang": "Please select your language:",
        "main_menu": "Main Menu 👑",
        "calc_gold": "🧮 Calculate Gold",
        "subscribe_status": "💳 Subscription Status",
        "make_invoice": "🧾 Issue Luxury Invoice",
        "no_sub": "⚠️ Access denied. Active subscription required.",
        "trial_msg": "Trial ended. Premium subscription is 105,000 IQD/month (Discounted from 133,000 IQD).",
        "enter_weight": "Please enter gold weight in grams:",
        "enter_karat": "Please select Karat (18, 21, 22, 24):",
        "enter_workmanship": "Please enter workmanship per gram (in IQD):",
        "loading": "Processing and calculating... ⏳",
        "result_title": "👑 Certified Calculation Result 👑\n\n",
        "invoice_header": "📜 Premium Digital Invoice - Gold Nucleus 📜\n"
    }
}

async def init_db():
    """تهيئة قاعدة البيانات بشكل كامل وجاهز للإنتاج لمنع مشاكل القفل"""
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
                trial_end = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d") # 7 أيام تجريبي تلقائي
                await db.execute(
                    "INSERT INTO users (user_id, username, lang, sub_status, trial_start, sub_end) VALUES (?, ?, 'ar', 'trial', ?, ?)",
                    (user_id, username, now, trial_end)
                )
                await db.commit()

async def get_user_lang(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 'ar'

async def set_user_lang(user_id, lang):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
        await db.commit()

async def check_subscription(user_id):
    """التحقق الذكي والآمن من صلاحية حساب الصائغ"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT sub_status, sub_end FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return False
            status, end_date_str = row
            if status == 'active':
                return True
            
            # التحقق من تاريخ انتهاء الفترة التجريبية أو الاشتراك المدفوع
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            if datetime.datetime.now() <= end_date:
                return True
            else:
                # تحديث تلقائي للحالة في حال الانتهاء لمنع ثغرات الدخول
                await db.execute("UPDATE users SET sub_status = 'expired' WHERE user_id = ?", (user_id,))
                await db.commit()
                return False

async def get_subscription_details(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT sub_status, sub_end FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

# أوامر الإدارة لتعديل قاعدة البيانات مباشرة
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
        async with db.execute("SELECT COUNT(*) FROM users") as c1:
            total = (await c1.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE sub_status = 'active'") as c2:
            active = (await c2.fetchone())[0]
        return total, active

async def db_get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]

def calculate_gold_price(weight, karat, workmanship, global_price_per_gram, profit_margin=0.05):
    """
    المعادلة الحسابية الصارمة للذهب:
    العيارات المعتمدة ونسب نقائها لتفادي أي خطأ حسابي في السوق المحلي.
    """
    karat_purities = {24: 1.0, 22: 0.916, 21: 0.875, 18: 0.750}
    purity = karat_purities.get(karat, 0.875)
    
    base_price = weight * (global_price_per_gram * purity)
    total_workmanship = weight * workmanship
    subtotal = base_price + total_workmanship
    final_price = subtotal * (1 + profit_margin)
    
    return round(base_price, 2), round(total_workmanship, 2), round(final_price, 2)
