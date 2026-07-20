import os
from decimal import Decimal
from supabase import create_client, Client

# استدعاء الرابط والمفتاح السري (service_role) للتحايل عبر منفذ الويب الافتراضي
SUPABASE_URL = os.getenv("SUPABASE_URL")  # الصق رابط المشروع المبتدئ بـ https://
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # الصق مفتاح service_role الطويل المبتدئ بـ eyJ

# إنشاء العميل السحابي عبر بروتوكول HTTP للتخلص من عوائق الـ DNS والمنافذ المغلقة
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def init_db():
    """
    تنبيه: نظراً لأننا انتقلنا للاتصال عبر بروتوكول الويب المحمي (API Client)،
    فإن الجداول تُنشأ مباشرة من لوحة تحكم Supabase (SQL Editor)،
    ولن نحتاج لدوال إنشاء الجداول عبر الأكواد لضمان أقصى سرعة خفيفة للبوت.
    """
    pass

def calculate_gold_invoice(weight: Decimal, caliber: int, mode: str, settings: dict):
    """
    إجراء العمليات الحسابية بدقة متناهية بدون تقريب نهائي مع تقسيم المثقال على 5.
    حساب الـ 100 دولار كورقة، وما دون الـ 100 دولار بالدينار العراقي حصراً.
    """
    # جلب الأسعار الافتراضية أو المسجلة صباحاً للعيارات
    calibers_map = {
        24: (Decimal(str(settings.get('price_24', 0))), Decimal(str(settings.get('making_24', 0)))),
        21: (Decimal(str(settings.get('price_21', 0))), Decimal(str(settings.get('making_21', 0)))),
        18: (Decimal(str(settings.get('price_18', 0))), Decimal(str(settings.get('making_18', 0))))
    }
    
    mitqal_price, making_charge = calibers_map[caliber]
    usd_rate = Decimal(str(settings.get('usd_rate', 155000)))
    
    # تقسيم سعر المثقال على 5 لاستخراج سعر الغرام الصافي الميداني
    gram_pure_price = mitqal_price / Decimal('5')
    
    # حساب السعر الإجمالي بالدينار العراقي
    if mode == "sell":
        total_price_iqd = (gram_pure_price + making_charge) * weight
    else:
        total_price_iqd = (gram_pure_price - making_charge) * weight
        
    # التحويل للورق والدينار المتبقي
    hundred_usd_price = usd_rate 
    total_usd = (total_price_iqd / hundred_usd_price) * Decimal('100')
    
    papers = int(total_usd / Decimal('100'))
    remaining_usd = total_usd - (Decimal(str(papers)) * Decimal('100'))
    remaining_iqd = (remaining_usd / Decimal('100')) * hundred_usd_price
    
    return {
        "gram_price": gram_pure_price,
        "total_iqd": total_price_iqd,
        "papers": papers,
        "remaining_iqd": remaining_iqd,
        "weight": weight
    }
