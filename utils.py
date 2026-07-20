import os
import asyncio
import logging
from decimal import Decimal, ROUND_DOWN
import asyncpg

# جلب رابط الاتصال الموحد المدمج به كلمة المرور من متغيرات البيئة بـ Render
DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db_connection():
    """إنشاء اتصال آمن ومباشر بقاعدة بيانات Supabase"""
    return await asyncpg.connect(DATABASE_URL)

async def init_db():
    """تهيئة وبناء جداول الصاغة تلقائياً في Supabase فور إقلاع النظام"""
    conn = await get_db_connection()
    try:
        # جدول الصاغة المشتركين وبيانات محلاتهم
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS goldsmiths (
                user_id BIGINT PRIMARY KEY,
                shop_name TEXT,
                location TEXT,
                phone TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_free_tier BOOLEAN DEFAULT TRUE,
                subscription_ends TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '7 days',
                is_active BOOLEAN DEFAULT TRUE
            );
        ''')
        
        # جدول الإعدادات الصباحية الخاصة بكل صائغ بشكل منفصل ومخير
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS morning_settings (
                user_id BIGINT PRIMARY KEY REFERENCES goldsmiths(user_id) ON DELETE CASCADE,
                price_24 DECIMAL DEFAULT 0,
                price_21 DECIMAL DEFAULT 0,
                price_18 DECIMAL DEFAULT 0,
                making_24 DECIMAL DEFAULT 0,
                making_21 DECIMAL DEFAULT 0,
                making_18 DECIMAL DEFAULT 0,
                usd_rate DECIMAL DEFAULT 155000
            );
        ''')
        logging.info("✅ Supabase tables initialized successfully.")
    except Exception as e:
        logging.error(f"❌ Error initializing database tables: {e}")
    finally:
        await conn.close()

# --- دالة الحسابات الهندسية الدقيقة الفخمة ---
def calculate_gold_invoice(weight: Decimal, caliber: int, mode: str, settings: dict):
    """
    إجراء العمليات الحسابية بدون تقريب نهائي مع تقسيم المثقال على 5
    حساب الـ 100 دولار كورقة، وما دون الـ 100 دولار بالدينار العراقي حصراً
    """
    # جلب الأسعار حسب العيار المحدد
    calibers_map = {
        24: (Decimal(str(settings['price_24'])), Decimal(str(settings['making_24']))),
        21: (Decimal(str(settings['price_21'])), Decimal(str(settings['making_21']))),
        18: (Decimal(str(settings['price_18'])), Decimal(str(settings['making_18'])))
    }
    
    mitqal_price, making_charge = calibers_map[caliber]
    usd_rate = Decimal(str(settings['usd_rate']))
    
    # تقسيم سعر المثقال على 5 لاستخراج سعر الغرام الصافي الصباحي
    gram_pure_price = mitqal_price / Decimal('5')
    
    # حساب السعر الإجمالي بالدينار
    if mode == "sell":
        # للبيع: (سعر الغرام الصافي + أجور الصياغة) * الوزن
        total_price_iqd = (gram_pure_price + making_charge) * weight
    else:
        # للشراء: (سعر غرام الشراء الصافي - خصم الصهر إن وجد) * الوزن
        # في الشراء نعتبر أجور الصياغة المكتوبة بالصباح كخصم صهر أو صافي مباشرة
        total_price_iqd = (gram_pure_price - making_charge) * weight
        
    # التحويل للدولار
    # سعر ورقة الـ 100 دولار المقررة صباحاً
    hundred_usd_price = usd_rate 
    
    # إجمالي الدولار الكلي الدقيق
    total_usd = (total_price_iqd / hundred_usd_price) * Decimal('100')
    
    # استخراج الأوراق الصحيحة (كل 100 دولار = 1 ورقة)
    papers = int(total_usd / Decimal('100'))
    
    # المبلغ المتبقي بالدولار والذي يقل عن 100 دولار
    remaining_usd = total_usd - (Decimal(str(papers)) * Decimal('100'))
    
    # تحويل المتبقي الأصغر من 100 دولار إلى دينار عراقي
    remaining_iqd = (remaining_usd / Decimal('100')) * hundred_usd_price
    
    return {
        "gram_price": gram_pure_price,
        "total_iqd": total_price_iqd,
        "papers": papers,
        "remaining_iqd": remaining_iqd,
        "weight": weight
    }
