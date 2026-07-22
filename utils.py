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
            "trial_expires_at": trial_expiry,
            "lang": "ar"
        }
        res = supabase.table("goldsmiths").insert(data).execute()
        return res.data
    except Exception as e:
        print(f"Error registering goldsmith: {e}")
        return None

def check_goldsmith_validity(user_id: int):
    """[تمت الإضافة] فحص صلاحية المحل وحساب الأيام المتبقية لمنع توقف البوت"""
    try:
        goldsmith = get_goldsmith(user_id)
        if not goldsmith:
            return False, 0
        
        if not goldsmith.get("is_active", False):
            return False, 0
            
        expiry_str = goldsmith.get("trial_expires_at")
        if not expiry_str:
            return True, 30 # افتراضي إذا لم يحدد التاريخ
            
        # تنظيف التنسيق القادم من قاعدة البيانات
        expiry_str = expiry_str.replace("Z", "").split("+")[0]
        expiry_date = datetime.fromisoformat(expiry_str)
        
        remaining = expiry_date - datetime.utcnow()
        days_left = remaining.days
        
        if days_left >= 0:
            return True, days_left
        return False, 0
    except Exception as e:
        print(f"Error checking validity: {e}")
        return True, 5 # تمرير مؤقت لحين استقرار الاتصال بالـ DB

def modify_goldsmith_subscription(user_id: int, days: int):
    """[تمت الإضافة] تمديد اشتراك الصائغ من قبل الأدمن بعد استلام الوصل"""
    try:
        goldsmith = get_goldsmith(user_id)
        if goldsmith:
            expiry_str = goldsmith.get("trial_expires_at")
            if expiry_str:
                expiry_str = expiry_str.replace("Z", "").split("+")[0]
                base_date = max(datetime.fromisoformat(expiry_str), datetime.utcnow())
            else:
                base_date = datetime.utcnow()
                
            new_expiry = (base_date + timedelta(days=days)).isoformat()
            supabase.table("goldsmiths").update({
                "trial_expires_at": new_expiry,
                "is_active": True
            }).eq("tg_id", user_id).execute()
            return True
        return False
    except Exception as e:
        print(f"Error modifying subscription: {e}")
        return False

def get_total_active_goldsmiths() -> int:
    """جلب العدد الإجمالي الحركي للمشتركين النشطين لعرض قوة المنظومة تسويقياً"""
    try:
        res = supabase.table("goldsmiths").select("id", count="exact").eq("is_active", True).execute()
        if res.count is not None:
            return res.count
        return len(res.data) if res.data else 0
    except:
        return 0

def get_goldsmith_lang(user_id: int):
    """[تمت الإضافة] جلب لغة الواجهة الحالية المخصصة لمحلك"""
    try:
        goldsmith = get_goldsmith(user_id)
        if goldsmith:
            return goldsmith.get("lang", "ar")
        return "ar"
    except:
        return "ar"

def update_goldsmith_lang(user_id: int, lang: str):
    """[تمت الإضافة] تحديث لغة الواجهة للصائغ في قاعدة البيانات عمودياً"""
    try:
        supabase.table("goldsmiths").update({"lang": lang}).eq("tg_id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error updating language: {e}")
        return False

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

def update_goldsmith_prices(user_id: int, p21: float, p18: float, w21: float, w18: float, usd_rate: float):
    """[تمت الإضافة] حفظ وتحديث أسعار الصباح الحرة الخاصة بمحلك"""
    try:
        # فحص إذا كان المحل لديه سجل أسعار سابق لتحديثه أو إنشاء سجل جديد (Upsert)
        res = supabase.table("daily_prices").select("id").eq("tg_id", user_id).execute()
        data = {
            "tg_id": user_id,
            "price_21": p21,
            "price_18": p18,
            "wage_21": w21,
            "wage_18": w18,
            "usd_rate": usd_rate,
            "updated_at": datetime.utcnow().isoformat()
        }
        if res.data and len(res.data) > 0:
            supabase.table("daily_prices").update(data).eq("tg_id", user_id).execute()
        else:
            supabase.table("daily_prices").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error updating prices: {e}")
        return False

def update_goldsmith_status(user_id: int, status: bool):
    """تفعيل أو إيقاف اشتراك الصائغ من لوحة التحكم السرية للأدمن"""
    try:
        supabase.table("goldsmiths").update({"is_active": status}).eq("tg_id", user_id).execute()
    except Exception as e:
        print(f"Error updating status: {e}")
