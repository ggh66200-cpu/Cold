import os
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

FREE_TRIAL_DAYS = 3

def calculate_remaining_days(expiry_date_str):
    if not expiry_date_str:
        return FREE_TRIAL_DAYS
    try:
        if 'T' in str(expiry_date_str):
            exp_date = datetime.fromisoformat(str(expiry_date_str).replace('Z', '+00:00')).date()
        else:
            exp_date = datetime.strptime(str(expiry_date_str).split()[0], "%Y-%m-%d").date()
        
        current_date = datetime.now(timezone.utc).date()
        delta = (exp_date - current_date).days
        return max(0, delta)
    except Exception as e:
        print(f"Date calculation error: {e}")
        return FREE_TRIAL_DAYS

def get_goldsmith(user_id):
    try:
        res = supabase.table("goldsmiths").select("*").eq("user_id", str(user_id)).execute()
        if res.data:
            gs = res.data[0]
            
            if "is_registered" not in gs:
                gs["is_registered"] = True
            
            expiry = gs.get("trial_expires_at")
            if not expiry:
                now_utc = datetime.now(timezone.utc)
                new_expiry = now_utc + timedelta(days=FREE_TRIAL_DAYS)
                expiry_str = new_expiry.isoformat()
                try:
                    supabase.table("goldsmiths").update({"trial_expires_at": expiry_str, "is_registered": True}).eq("user_id", str(user_id)).execute()
                except:
                    pass
                gs["trial_expires_at"] = expiry_str
            
            gs["remaining_days"] = calculate_remaining_days(gs.get("trial_expires_at"))
            
            # تحديد نوع الحالة (تجريبي أو مدفوع)
            created_at = gs.get("created_at")
            gs["subscription_type"] = "مجاني (تجريبي)" if gs["remaining_days"] <= FREE_TRIAL_DAYS else "اشتراك مدفوع"
            return gs
        else:
            return {"user_id": str(user_id), "full_name": "أرامكي للحلول الرقمية", "is_registered": False, "remaining_days": 0, "subscription_type": "غير مسجل"}
    except Exception as e:
        print(f"Supabase Error: {e}")
        return {"user_id": str(user_id), "full_name": "أرامكي للحلول الرقمية", "is_registered": False, "remaining_days": 0, "subscription_type": "غير مسجل"}

def search_goldsmith(query_str):
    """بحث فعّال عن عميل بالاسم، المعرف، أو رقم الهاتف"""
    try:
        query_str = str(query_str).strip()
        # محاولة البحث بالمعرف أو الهاتف أو جزء من الاسم
        res = supabase.table("goldsmiths").select("*").or_(f"user_id.eq.{query_str},phone.ilike.%{query_str}%,full_name.ilike.%{query_str}%").execute()
        
        goldsmiths = res.data if res.data else []
        for gs in goldsmiths:
            gs["remaining_days"] = calculate_remaining_days(gs.get("trial_expires_at"))
        return goldsmiths
    except Exception as e:
        print(f"Search Error: {e}")
        return []

def get_all_goldsmiths():
    try:
        res = supabase.table("goldsmiths").select("*").order("created_at", desc=False).execute()
        goldsmiths = res.data if res.data else []
        
        now_utc = datetime.now(timezone.utc)
        for index, gs in enumerate(goldsmiths):
            if "is_registered" not in gs:
                gs["is_registered"] = True
                
            expiry = gs.get("trial_expires_at")
            if not expiry:
                new_expiry = now_utc + timedelta(days=FREE_TRIAL_DAYS)
                expiry_str = new_expiry.isoformat()
                try:
                    supabase.table("goldsmiths").update({"trial_expires_at": expiry_str}).eq("user_id", str(gs.get("user_id"))).execute()
                except:
                    pass
                gs["trial_expires_at"] = expiry_str
            
            gs["remaining_days"] = calculate_remaining_days(gs.get("trial_expires_at"))
            gs["member_serial"] = 145 + index
            
            # تحديد نوع الاشتراك بدقة للأدمن
            exp_date_str = gs.get("trial_expires_at", "")
            gs["subscription_type"] = "🎁 فترة تجريبية مجانية" if gs["remaining_days"] <= FREE_TRIAL_DAYS else "💎 اشتراك رسمي مدفوع"
            
        return goldsmiths
    except Exception as e:
        print(f"Supabase All Users Error: {e}")
        return []

def register_goldsmith_details(user_id, shop_name, phone):
    try:
        initial_expiry = (datetime.now(timezone.utc) + timedelta(days=FREE_TRIAL_DAYS)).isoformat()
        
        data = {
            "user_id": str(user_id),
            "full_name": shop_name,
            "phone": phone,
            "is_registered": True,
            "trial_expires_at": initial_expiry
        }
        supabase.table("goldsmiths").upsert(data).execute()
    except Exception as e:
        print(f"Error registering: {e}")
        raise e

def update_goldsmith_subscription(user_id, days):
    """إضافة أو خصم أيام من اشتراك العميل"""
    try:
        res = supabase.table("goldsmiths").select("trial_expires_at").eq("user_id", str(user_id)).execute()
        current_expiry = None
        if res.data and res.data[0].get("trial_expires_at"):
            current_expiry_str = res.data[0]["trial_expires_at"]
            try:
                if 'T' in str(current_expiry_str):
                    current_expiry = datetime.fromisoformat(str(current_expiry_str).replace('Z', '+00:00'))
                else:
                    current_expiry = datetime.strptime(str(current_expiry_str).split()[0], "%Y-%m-%d")
                    current_expiry = current_expiry.replace(tzinfo=timezone.utc)
            except:
                pass
        
        now_utc = datetime.now(timezone.utc)
        
        # إذا كانت الأيام سالبة (خصم) أو موجبة (إضافة)
        base_time = current_expiry if (current_expiry and current_expiry > now_utc) else now_utc
        new_expiry = base_time + timedelta(days=int(days))
            
        supabase.table("goldsmiths").update({"trial_expires_at": new_expiry.isoformat()}).eq("user_id", str(user_id)).execute()
    except Exception as e:
        print(f"Error updating sub: {e}")
        raise e

def adjust_goldsmith_days(user_id, days, set_zero=False):
    try:
        if set_zero:
            now_str = datetime.now(timezone.utc).isoformat()
            supabase.table("goldsmiths").update({"trial_expires_at": now_str}).eq("user_id", str(user_id)).execute()
        else:
            update_goldsmith_subscription(user_id, days)
    except Exception as e:
        print(f"Error adjusting days: {e}")

def get_goldsmith_prices(user_id):
    try:
        res = supabase.table("morning_prices").select("*").eq("user_id", int(user_id)).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        print(f"Supabase Prices Error: {e}")
    return {
        "price_21": 900000,
        "price_18": 450000,
        "wage_21": 4500,
        "wage_18": 7500,
        "usd_rate": 153000
    }

def update_morning_prices(user_id, p21, p18, w21, w18, usd_r):
    try:
        uid = int(user_id)
        data = {
            "user_id": uid,
            "price_21": float(p21),
            "price_18": float(p18),
            "wage_21": float(w21),
            "wage_18": float(w18),
            "usd_rate": float(usd_r)
        }
        supabase.table("morning_prices").upsert(data).execute()
    except Exception as e:
        print(f"Supabase Update Error: {e}")
        raise e
