def generate_invoice(operation, weight, karat, total, usd_rate, papers, remaining, fractional_dollars):
    msg = f"**📊 تصفية الحسبة النهائية (سوق الذهب):**\n"
    msg += "_________________________\n"
    msg += f"🔄 العملية: {operation}\n"
    msg += f"⚖️ الوزن: {weight} غرام (عيار {karat})\n"
    msg += f"💵 سعر صرف الـ $100: {usd_rate:,.0f} د.ع\n"
    msg += "_________________________\n"
    msg += f"💰 صافي السعر بالدينار: **{total:,.0f} د.ع**\n\n"
    msg += f"💵 **في حال الدفع بالدولار (التصفية):**\n"
    msg += f"💵 المستلم بالورق الصافي: **{papers}$**\n"
    msg += f"↩️ يُرجع باقي للزبون بالدينار: **{remaining:,.0f} د.ع**\n"
    msg += f"* (قيمة الـ {fractional_dollars:,.2f}$ المتبقية بالكسر)*"
    return msg
