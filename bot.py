import os
import telebot
from supabase import create_client, Client

# إعداد مفاتيح البيئة للبوت وقاعدة البيانات
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "أهلاً بكِ في بوت المعلمات السري! 🌸\n\n"
        "هذا البوت مخصص لمساعدتكِ في رفع ملفاتكِ، وتتبع درجات الطلاب، "
        "وتنظيم أعمالكِ التعليمية بكل سهولة.\n\n"
        "الرجاء اختيار الخدمة المطلوبة من القائمة أو رفع الملف مباشرة."
    )
    bot.reply_to(message, welcome_text)
  @bot.message_handler(content_types=['document', 'photo'])
def handle_docs_photos(message):
    try:
        bot.reply_to(message, "جاري استقبال الملف ورفعه إلى السحابة... برجاء الانتظار ⏳")
        
        # تحديد نوع الملف وجلب بياناته
        if message.content_type == 'document':
            file_id = message.document.file_id
            file_name = message.document.file_name
        else:
            file_id = message.photo[-1].file_id
            file_name = f"photo_{file_id[:10]}.jpg"
            
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # رفع الملف مباشرة إلى مجلد Supabase
        bucket_name = "teacher_submissions"
        res = supabase.storage.from_(bucket_name).upload(
            path=file_name,
            file=downloaded_file,
            file_options={"content-type": "application/octet-stream"}
        )
        
        bot.reply_to(message, f"✅ تم رفع الملف بنجاح باسم: {file_name}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء الرفع: {str(e)}")

# تشغيل البوت بشكل مستمر
if __name__ == "__main__":
    bot.infinity_polling()
                     
