import os
import time
from datetime import datetime, timedelta
from supabase import create_client, Client

# ربط البيئة بمتغيرات Render الحساسة
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# ذاكرة مؤقتة لمنع التكرار وسرعة الاستجابة (Anti-Spam Cache)
user_locks = {}

def is_action_locked(user_id: int, delay: int = 4) -> bool:
    """تمنع العميل من الضغط المتكرر على /start أو الأزرار لتفادي التعليق"""
    current_time = time.time()
    if user_id in user_locks:
        if current_time - user_locks[user_id] < delay:
            return True
    user_locks[user_id] = current_time
    return False

def get_goldsmith(user_id: int):
    res = supabase.table("goldsmiths").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None

def update_goldsmith_status(user_id: int, is_active: bool):
    supabase.table("goldsmiths").update({"is_active": is_active}).eq("user_id", user_id).execute()

def update_trial_duration(user_id: int, days: int):
    new_expiry = datetime.now() + timedelta(days=days)
    supabase.table("goldsmiths").update({"trial_expires_at": new_expiry.isoformat()}).eq("user_id", user_id).execute()

def set_default_trial_days(days: int):
    supabase.table("system_settings").upsert({"key": "default_trial_days", "value": str(days)}).execute()

def get_default_trial_days() -> int:
    res = supabase.table("system_settings").select("value").eq("key", "default_trial_days").execute()
    return int(res.data[0]['value']) if res.data else 7
