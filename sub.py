import os

ADMIN_ID = os.environ.get('ADMIN_ID')

def is_subscribed(user_id):
    # إذا كان الشخص هو الأدمن، يفتح البوت دائماً
    if str(user_id) == str(ADMIN_ID): 
        return True
    
    # هنا مستقبلاً نربط قاعدة بيانات المشتركين
    # حالياً سنتركه True لكي تتمكن من الفحص والتجربة
    return True 
