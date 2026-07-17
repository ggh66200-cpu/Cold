import time, utils

def check_user(user_id):
    """
    يفحص حالة المشترك: هل هو مسجل؟ هل فترته التجريبية أو اشتراكه فعال؟
    """
    data = utils.get_data()
    uid = str(user_id)
    now = time.time()
    
    # 1. إذا كان المستخدم غير مسجل نهائياً
    if uid not in data['users'] or not isinstance(data['users'][uid], dict):
        if uid not in data['users']:
            data['total_count'] += 1
        data['users'][uid] = {
            "join_date": now,
            "lang": "ar",
            "shop_name": None,        # يملأه المستخدم لاحقاً
            "is_active": False,       # تفعيل الاشتراك يدوياً
            "expiry_date": 0,         # تاريخ انتهاء الاشتراك المدفوع
            "payment_pending": False  # هل بانتظار تأكيد الوصل من الأدمن؟
        }
        utils.save_data(data)
        return False, "REGISTRATION_REQUIRED"
    
    user = data['users'][uid]
    
    # 2. إذا كان مسجلاً لكن لم يكتب اسم المحل بعد
    if not user.get("shop_name"):
        return False, "REGISTRATION_REQUIRED"
        
    # 3. حساب فترة التجريب المجاني الديناميكية
    trial_days = data.get("trial_days", 7) # القيمة الافتراضية 7 أيام ويمكن للأدمن تغييرها
    trial_duration = trial_days * 24 * 60 * 60
    
    is_trial_active = (now - user.get("join_date", now)) < trial_duration
    is_premium_active = user.get("is_active", False) and (user.get("expiry_date", 0) > now)
    
    if is_trial_active or is_premium_active:
        return True, "ACTIVE"
    else:
        return False, "EXPIRED"
