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
            new_user = {"user_id": str(user_id), "full_name": "التواضع", "lang": "ar"}
            supabase.table("goldsmiths").insert(new_user).execute()
            return new_user
    except Exception as e:
        print(f"Supabase Error: {e}")
        return {"user_id": str(user_id), "full_name": "التواضع", "lang": "ar"}

def get_goldsmith_prices(user_id):
    try:
        res = supabase.table("morning_prices").select("*").eq("user_id", str(user_id)).execute()
        if res.data:
            return res.data[0]
        else:
            default_prices = {
                "user_id": str(user_id),
                "price_21": 900000,
                "price_18": 450000,
                "wage_21": 10000,
                "wage_18": 1000,
                "usd_rate": 155000
            }
            supabase.table("morning_prices").insert(default_prices).execute()
            return default_prices
    except Exception as e:
        print(f"Supabase Prices Error: {e}")
        # إرجاع القيم لتفادي توقف البوت، لكن التعديل أدناه في التحديث سيحل مشكلة الحفظ
        return {"price_21": 900000, "price_18": 450000, "wage_21": 10000, "wage_18": 1000, "usd_rate": 155000}

def update_goldsmith_prices(user_id, p21, p18, w21, w18, usd):
    try:
        data = {"price_21": p21, "price_18": p18, "wage_21": w21, "wage_18": w18, "usd_rate": usd}
        
        # نتحقق أولاً هل السجل موجود للمستخدم؟
        check = supabase.table("morning_prices").select("user_id").eq("user_id", str(user_id)).execute()
        
        if check.data:
            # إذا موجود نقوم بعمل تحديث (Update) مباشر ومضمون للسطح الخاص بالمستخدم
            supabase.table("morning_prices").update(data).eq("user_id", str(user_id)).execute()
        else:
            # إذا غير موجود نقوم بعمل إدخال (Insert) لأول مرة
            supabase.table("morning_prices").insert({"user_id": str(user_id), **data}).execute()
            
    except Exception as e:
        print(f"Supabase Update Error: {e}")
        # لكي ينتبه المطور أو يظهر في سجل الأخطاء بشكل واضح
        raise e 

def update_goldsmith_lang(user_id, lang_code):
    try:
        supabase.table("goldsmiths").update({"lang": lang_code}).eq("user_id", str(user_id)).execute()
    except Exception as e:
        print(f"Supabase Lang Update Error: {e}")
