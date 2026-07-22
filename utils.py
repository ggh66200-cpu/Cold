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
    """تسجيل صائغ جديد وتفعيل الفترة التجريبية تلقائياً"""
    try:
        # نجلب الإعداد الافتراضي للأيام أو نضع 7 كقيمة احتياطية
        trial_days = get_system_setting("trial_days", 7)
        trial_expiry = (datetime.utcnow() + timedelta(days=trial_days)).isoformat()
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
    """فحص صلاحية المحل وحساب الأيام المتبقية لمنع توقف البوت"""
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
    """تمديد اشتراك الصائغ أو قفله (إذا كانت الأيام سالب) من قبل الأدمن"""
    try:
        goldsmith = get_goldsmith(user_id)
        if goldsmith:
            if days == -999:
                # قفل الحساب فوراً
                supabase.table("goldsmiths").update({
                    "is_active": False,
                    "trial_expires_at": datetime.utcnow().isoformat()
                }).eq("tg_id", user_id).execute()
                return True
                
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

def get_total_registered_users_count() -> int:
    """[تمت الإضافة لحل نقص bot.py] جلب كل المسجلين كلياً لترقيم كود الصائغ التسلسلي"""
    try:
        res = supabase.table("goldsmiths").select("id", count="exact").execute()
        if res.count is not None:
            return res.count
        return len(res.data) if res.data else 0
    except:
        return 0

def get_goldsmith_lang(user_id: int):
    """جلب لغة الواجهة الحالية المخصصة لمحلك"""
    try:
        goldsmith = get_goldsmith(user_id)
        if goldsmith:
            return goldsmith.get("lang", "ar")
        return "ar"
    except:
        return "ar"

def update_goldsmith_lang(user_id: int, lang: str):
    """تحديث لغة الواجهة للصائغ في قاعدة البيانات عمودياً"""
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
        "price_21": 490000,
        "price_18": 420000,
        "wage_21": 0,
        "wage_18": 0,
        "usd_rate": 153000
    }

def update_goldsmith_prices(user_id: int, p21: float, p18: float, w21: float, w18: float, usd_rate: float):
    """حفظ وتحديث أسعار الصباح الحرة الخاصة بمحلك"""
    try:
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

# ================= الدوال الجديدة المضافة لإصلاح كراش السيرفر بنجاح =================

def get_system_setting(setting_name: str, default_value):
    """[تمت الإضافة] جلب إعدادات النظام الحركية مثل عدد أيام الفترة التجريبية الافتراضية"""
    try:
        res = supabase.table("system_settings").select("setting_value").eq("setting_key", setting_name).execute()
        if res.data and len(res.data) > 0:
            return int(res.data[0]["setting_value"])
    except Exception as e:
        print(f"Error getting system setting: {e}")
    return default_value

def set_system_setting(setting_name: str, value):
    """[تمت الإضافة] تحديث وحفظ قيم إعدادات النظام من قبل الأدمن المركزي"""
    try:
        res = supabase.table("system_settings").select("id").eq("setting_key", setting_name).execute()
        data = {"setting_key": setting_name, "setting_value": str(value)}
        if res.data and len(res.data) > 0:
            supabase.table("system_settings").update(data).eq("setting_key", setting_name).execute()
        else:
            supabase.table("system_settings").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error setting system setting: {e}")
        return False

def get_all_registered_goldsmiths():
    """[تمت الإضافة] جلب كل الصاغة المسجلين لبناء أزرار الجرد التلقائي في لوحة الأدمن بدون الحاجة لكتابة الأيدي"""
    try:
        res = supabase.table("goldsmiths").select("tg_id, full_name, location, phone").execute()
        output = []
        if res.data:
            for item in res.data:
                output.append({
                    "user_id": item["tg_id"],
                    "full_name": item["full_name"],
                    "location": item["location"],
                    "phone": item["phone"]
                })
        return output
    except Exception as e:
        print(f"Error getting all goldsmiths: {e}")
        return []
