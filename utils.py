import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_goldsmith(user_id):
    try:
        res = supabase.table("goldsmiths").select("*").eq("user_id", str(user_id)).execute()
        if res.data:
            return res.data[0]
        else:
            return {"user_id": str(user_id), "full_name": "أرامكي للحلول الرقمية", "is_registered": False, "remaining_days": 0}
    except Exception as e:
        print(f"Supabase Error: {e}")
        return {"user_id": str(user_id), "full_name": "أرامكي للحلول الرقمية", "is_registered": False, "remaining_days": 0}

def register_goldsmith_details(user_id, shop_name, phone):
    try:
        data = {
            "user_id": str(user_id),
            "full_name": shop_name,
            "phone": phone,
            "is_registered": True
        }
        supabase.table("goldsmiths").upsert(data).execute()
    except Exception as e:
        print(f"Error registering: {e}")

def update_goldsmith_subscription(user_id, days):
    try:
        res = supabase.table("goldsmiths").select("remaining_days").eq("user_id", str(user_id)).execute()
        current_days = 0
        if res.data and res.data[0].get("remaining_days"):
            current_days = int(res.data[0]["remaining_days"])
        
        new_days = current_days + days
        supabase.table("goldsmiths").update({"remaining_days": new_days}).eq("user_id", str(user_id)).execute()
    except Exception as e:
        print(f"Error updating sub: {e}")

def adjust_goldsmith_days(user_id, days, set_zero=False):
    try:
        if set_zero:
            supabase.table("goldsmiths").update({"remaining_days": 0}).eq("user_id", str(user_id)).execute()
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
