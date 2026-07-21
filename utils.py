import os
import time
from datetime import datetime, timedelta
from supabase import create_client, Client

# ربط البيئة بقاعدة بيانات Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# قفل لمنع التكرار والسبام (Anti-Spam)
_LOCKS = {}

def is_action_locked(user_id: int, delay: int = 2) -> bool:
    """يمنع الصائغ من النقر المتكرر لضمان عدم تعليق السيرفر"""
    current_time = time.time()
    if user_id in _LOCKS and (current_time - _LOCKS[user_id] < delay):
        return True
    _LOCKS[user_id] = current_time
    return False

def get_goldsmith(user_id: int):
    """جلب بيانات الصائغ والتحقق من اشتراكه"""
    try:
        res = supabase.table("goldsmiths").select("*").eq("tg_id", user_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        print(f"Error getting goldsmith: {e}")
        return None

def register_new_goldsmith(user_id: int, full_name: str, location: str, phone: str):
    """تسجيل صائغ جديد وتفعيل الفترة التجريبية 7 أيام تلقائياً"""
    try:
        trial_expiry = (datetime.utcnow() + timedelta(days=7)).isoformat()
        data = {
            "tg_id": user_id,
            "full_name": full_name,
            "location": location,
            "phone": phone,
            "is_active": True,
            "trial_expires_at": trial_expiry
        }
        res = supabase.table("goldsmiths").insert(data).execute()
        return res.data
    except Exception as e:
        print(f"Error registering goldsmith: {e}")
        return None

def get_total_active_goldsmiths() -> int:
    """جلب العدد الإجمالي الحركي للمشتركين النشطين لعرض قوة المنظومة تسويقياً"""
    try:
        res = supabase.table("goldsmiths").select("id", count="exact").eq("is_active", True).execute()
        if res.count is not None:
            return res.count
        return len(res.data) if res.data else 167
    except:
        return 167

def get_goldsmith_prices(user_id: int) -> dict:
    """جلب أسعار الصباح المخزنة للصائغ، وإذا لم توجد يعطيه الأسعار الافتراضية للسوق"""
    try:
        res = supabase.table("daily_prices").select("*").eq("tg_id", user_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception as e:
        print(f"Error getting prices: {e}")
        
    return {
        "price_21": 900000,
        "price_18": 450000,
        "wage_21": 10000,
        "wage_18": 1000,
        "usd_rate": 155000
    }

def update_goldsmith_status(user_id: int, status: bool):
    """تفعيل أو إيقاف اشتراك الصائغ من لوحة التحكم السرية للأدمن"""
    try:
        supabase.table("goldsmiths").update({"is_active": status}).eq("tg_id", user_id).execute()
    except Exception as e:
        print(f"Error updating status: {e}")
