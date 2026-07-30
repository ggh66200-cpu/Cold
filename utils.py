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
        if 'T' in expiry_date_str:
            exp_date = datetime.fromisoformat(expiry_date_str.replace('Z', '+00:00')).date()
        else:
            exp_date = datetime.strptime(expiry_date_str.split()[0], "%Y-%m-%d").date()
        
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
            
            expiry = gs.get("expiry_date")
            if not expiry:
                today = datetime.now(timezone.utc).date()
                new_expiry = today + timedelta(days=FREE_TRIAL_DAYS)
                expiry = new_expiry.strftime("%Y-%m-%d")
                try:
                    supabase.table("goldsmiths").update({"expiry_date": expiry, "is_registered": True}).eq("user_id", str(user_id)).execute()
                except:
                    pass
                gs["expiry_date"] = expiry
            
            gs["remaining_days"] = calculate_remaining_days(gs.get("expiry_date"))
            return gs
        else:
            return {"user_id": str(user_id), "full_name": "أرامكي للحلول الرقمية", "is_registered": False, "remaining_days": 0}
    except Exception as e:
        print(f"Supabase Error: {e}")
        return {"user_id": str(user_id), "full_name": "أرامكي للحلول الرقمية", "is_registered": False, "remaining_days": 0}

def get_all_goldsmiths():
    try:
        res = supabase.table("goldsmiths").select("*").order("created_at", desc=False).execute()
        goldsmiths = res.data if res.data else []
        
        today = datetime.now(timezone.utc).date()
        for index, gs in enumerate(goldsmiths):
            if "is_registered" not in gs:
                gs["is_registered"] = True
                
            expiry = gs.get("expiry_date")
            if not expiry:
                new_expiry = today + timedelta(days=FREE_TRIAL_DAYS)
                expiry = new_expiry.strftime("%Y-%m-%d")
                try:
                    supabase.table("goldsmiths").update({"expiry_date": expiry}).eq("user_id", str(gs.get("user_id"))).execute()
                except:
                    pass
                gs["expiry_date"] = expiry
            
            gs["remaining_days"] = calculate_remaining_days(gs.get("expiry_date"))
            gs["member_serial"] = 145 + index
        return goldsmiths
    except Exception as e:
        print(f"Supabase All Users Error: {e}")
        return []

def register_goldsmith_details(user_id, shop_name, phone):
    try:
        initial_expiry = (datetime.now(timezone.utc) + timedelta(days=FREE_TRIAL_DAYS)).strftime("%Y-%m-%d")
        
        data = {
            "user_id": str(user_id),
            "full_name": shop_name,
            "phone": phone,
            "is_registered": True,
            "expiry_date": initial_expiry
        }
        supabase.table("goldsmiths").upsert(data).execute()
    except Exception as e:
        print(f"Error registering: {e}")
        raise e

def update_goldsmith_subscription(user_id, days):
    try:
        res = supabase.table("goldsmiths").select("expiry_date").eq("user_id", str(user_id)).execute()
        current_expiry = None
        if res.data and res.data[0].get("expiry_date"):
            current_expiry_str = res.data[0]["expiry_date"]
            try:
                if 'T' in current_expiry_str:
                    current_expiry = datetime.fromisoformat(current_expiry_str.replace('Z', '+00:00')).date()
                else:
                    current_expiry = datetime.strptime(current_expiry_str.split()[0], "%Y-%m-%d").date()
            except:
                pass
        
        today = datetime.now(timezone.utc).date()
        
        if current_expiry and current_expiry > today:
            new_expiry = current_expiry + timedelta(days=days)
        else:
            new_expiry = today + timedelta(days=days)
            
        supabase.table("goldsmiths").update({"expiry_date": new_expiry.strftime("%Y-%m-%d")}).eq("user_id", str(user_id)).execute()
    except Exception as e:
        print(f"Error updating sub: {e}")
        raise e

def adjust_goldsmith_days(user_id, days, set_zero=False):
    try:
        if set_zero:
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            supabase.table("goldsmiths").update({"expiry_date": today_str}).eq("user_id", str(user_id)).execute()
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
