import telebot
from telebot import types

ADMIN_ID = 0  # ضع معرف المدير هنا إذا لزم الأمر
MASTER_CARD = "5391 0000 0000 0000"
MONTHLY_PRICE = "25,000 دينار"
COMPANY_HEADER = "⚜️ <b>ARAMKY | SMART GOLD SYSTEM</b> ⚜️\n"

def admin_panel_start(message, bot):
    try:
        bot.send_message(
            message.chat.id,
            "🛠️ <b>أهلاً بك في لوحة تحكم الإدارة البرمجية:</b>\n\nالمنظومة تعمل بشكل سليم.",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Admin panel error: {e}")

def register_admin_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin_sub_"))
    def handle_admin_subscription_callbacks(call):
        try:
            parts = call.data.split("_")
            action = parts[2]
            target_user_id = int(parts[3])
            
            if action == "30":
                bot.answer_callback_query(call.id, text="✅ تم تفعيل الاشتراك بنجاح!")
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                bot.send_message(call.message.chat.id, f"✅ تم تفعيل اشتراك المستخدم <code>{target_user_id}</code> لمدة شهر بنجاح.", parse_mode="HTML")
                try:
                    bot.send_message(target_user_id, "🎉 <b>مبروك! تم تفعيل اشتراكك بنجاح في منظومة أرامكي.</b>", parse_mode="HTML")
                except Exception:
                    pass
            elif action == "zero":
                bot.answer_callback_query(call.id, text="❌ تم رفض الوصل.")
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                bot.send_message(call.message.chat.id, f"❌ تم رفض وصل المستخدم <code>{target_user_id}</code>.", parse_mode="HTML")
        except Exception as e:
            print(f"Admin callback error: {e}")
          
