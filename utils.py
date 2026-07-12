import json

def get_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def format_invoice(invoice_id, weight, total, papers=None, rem=None, type="buy"):
    if type == "buy":
        return f"🧾 **فاتورة شراء من زبون**\n\nرقم الفاتورة: `#{invoice_id}`\nالوزن: {weight} غرام ⚖️\nالسعر الكلي: {total:,.0f} د.ع 💰\n\n**تفاصيل الدفع:**\nالاستلام بالدولار: {papers}$ 💵\nالباقي بالعراقي: {rem:,.0f} د.ع 💴\n\n✅ *تم توثيق الفاتورة*"
    else:
        return f"🧾 **فاتورة بيع للزبون**\n\nرقم الفاتورة: `#{invoice_id}`\nالوزن: {weight} غرام ⚖️\nالسعر المطلوب: {total:,.0f} د.ع 💰\n\n✅ *تم توثيق الفاتورة*"
