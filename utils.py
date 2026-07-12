import time
import json
import os

DATA_FILE = 'data.json'

def get_data():
    if not os.path.exists(DATA_FILE):
        return {"subs": {}, "usd_100": 150000} # قيم افتراضية
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# دالة فحص الاشتراك
def is_subscribed(user_id):
    data = get_data()
    subs = data.get('subs', {})
    expiry = subs.get(str(user_id), 0)
    return time.time() < expiry

# دالة إضافة اشتراك (للأدمن)
def add_subscription(user_id, days):
    data = get_data()
    if 'subs' not in data: data['subs'] = {}
    data['subs'][str(user_id)] = time.time() + (int(days) * 86400)
    save_data(data)

# دالة الفاتورة المرتبة
def generate_invoice(operation, weight, karat, total, usd_rate, papers, remaining, fractional_dollars):
    return (f"**📊 تصفية الحسبة النهائية (سوق الذهب):**\n"
            "_________________________\n"
            f"🔄 العملية: {operation}\n"
            f"⚖️ الوزن: {weight} غرام (عيار {karat})\n"
            f"💵 سعر صرف الـ $100: {usd_rate:,.0f} د.ع\n"
            "_________________________\n"
            f"💰 صافي السعر بالدينار: **{total:,.0f} د.ع**\n\n"
            f"💵 **في حال الدفع بالدولار (التصفية):**\n"
            f"💵 المستلم بالورق الصافي: **{papers}$**\n"
            f"↩️ يُرجع باقي للزبون بالدينار: **{remaining:,.0f} د.ع**\n"
            f"* (قيمة الـ {fractional_dollars:,.2f}$ المتبقية بالكسر)*")
