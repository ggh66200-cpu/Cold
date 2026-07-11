import telebot, os, json
from flask import Flask
from threading import Thread

# قراءة الإعدادات من السيرفر مباشرة للأمان
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')
bot = telebot.TeleBot(TOKEN)
DATA_FILE = "gold_data.json"

# نظام الخداع البصري للسيرفر (Flask)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Active"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
Thread(target=run).start()

# نظام حفظ البيانات لضمان عدم ضياعها
def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

# (هنا يوضع باقي الكود الخاص باللغات، الحاسبة، والاشتراكات)
# عند كل عملية تفعيل، استدعِ دالة save_data() ليتم حفظ التعديلات في الملف
