import os
from decimal import Decimal
from datetime import datetime, timedelta
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_or_create_user(user_id: int, username: str = None):
    """جلب بيانات العميل أو إنشائه تلقائياً في سبيس لحفظ البيانات"""
    res = supabase.table("goldsmiths").select("*").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]
    
    # قراءة إعدادات النظام الافتراضية للوقت التجريبي
    sys_res = supabase.table("system_config").select("*").eq("id", 1).execute()
    free_days = sys_res.data[0]["default_free_days"] if sys_res.data else 7
    
    end_date = datetime.utcnow() + timedelta(days=free_days)
    new_user = {
        "user_id": user_id,
        "username": username,
        "language": "ar",
        "is_active": True,
        "subscription_ends": end_date.isoformat()
    }
    supabase.table("goldsmiths").insert(new_user).execute()
    # إنشاء سطر الإعدادات الصباحية الافتراضية للعميل الجديد
    supabase.table("morning_settings").insert({"user_id": user_id}).execute()
    return new_user

def calculate_sell(weight: Decimal, caliber: int, settings: dict) -> dict:
    """حساب عملية البيع للزبون بالتفصيل العراقي والدولار"""
    # جلب سعر المثقال من الإعدادات الصباحية وتقسيمه على 5 لمعرفة سعر الغرام
    mithqal_price = Decimal(str(settings.get(f"price_{caliber}", 0)))
    making_charge = Decimal(str(settings.get(f"making_{caliber}", 0)))
    usd_rate = Decimal(str(settings.get("usd_rate", 155000)))
    
    gram_gold_price = mithqal_price / Decimal("5")
    total_gram_price = gram_gold_price + making_charge
    
    total_iqd = weight * total_gram_price
    
    # حسبة الـ 100 دولار (الورقة) والباقي فراطة بالدينار العراقي
    papers = int(total_iqd // usd_rate)
    remaining_iqd = total_iqd % usd_rate
    
    return {
        "weight": weight,
        "gram_price": total_gram_price,
        "total_iqd": total_iqd,
        "papers": papers,
        "remaining_iqd": remaining_iqd
    }

def calculate_buy(weight: Decimal, caliber: int, mithqal_buy_price: Decimal, making_deduction: Decimal) -> dict:
    """حساب عملية الشراء من الزبون (الكسر)"""
    gram_gold_price = mithqal_buy_price / Decimal("5")
    final_gram_price = gram_gold_price - making_deduction
    total_iqd = weight * final_gram_price
    
    return {
        "weight": weight,
        "gram_price": final_gram_price,
        "total_iqd": total_iqd
    }
