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
            new_user = {"user_id": str(user_id), "full_name": "أرامكي للحلول الرقمية"}
            supabase.table("goldsmiths").insert(new_user).execute()
            return new_user
    except Exception as e:
        print(f"Supabase Error: {e}")
        return {"user_id": str(user_id), "full_name": "أرامكي للحلول الرقمية"}

def get_goldsmith_prices(user_id):
    try:
        res = supabase.table("morning_prices").select("*").eq("user_id", int(user_id)).execute()
        if res.data:
            return res.data[0]
        else:
            default_prices = {
                "user_id": int(user_id),
                "price_21": 900000,
                "price_18": 450000,
                "wage_21": 4500,
                "wage_18": 7500,
                "usd_rate": 153000
            }
            supabase.table("morning_prices").insert(default_prices).execute()
            return default_prices
    except Exception as e:
        print(f"Supabase Prices Error: {e}")
        return {"price_21": 900000, "price_18": 450000, "wage_21": 4500, "wage_18": 7500, "usd_rate": 153000}

def update_goldsmith_prices(user_id, p21, p18, w21, w18, usd):
    try:
        uid = int(user_id)
        data = {
            "user_id": uid,
            "price_21": float(p21),
            "price_18": float(p18),
            "wage_21": float(w21),
            "wage_18": float(w18),
            "usd_rate": float(usd)
        }
        supabase.table("morning_prices").upsert(data).execute()
            
    except Exception as e:
        print(f"Supabase Update Error: {e}")
        raise e 
