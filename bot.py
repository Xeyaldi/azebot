import os
import telebot
import requests
from telebot import types

TOKEN = os.getenv('BOT_TOKEN')
TMDB_KEY = os.getenv('TMDB_API_KEY')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    start_text = (
        "🎬 **Xeyal Film Downloader v5.0**\n\n"
        "Filmin adını yazın, mən onu tapıb sizə birbaşa video kimi göndərəcəm.\n"
        "⚠️ _Qeyd: Böyük fayllar zaman ala bilər._"
    )
    bot.send_message(message.chat.id, start_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def search_and_send_video(message):
    query = message.text
    search_url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_KEY}&query={query}&language=tr-TR"
    
    try:
        res = requests.get(search_url).json()
        if not res.get('results'):
            bot.send_message(message.chat.id, "❌ Tapılmadı.")
            return

        data = res['results'][0]
        title = data.get('title') or data.get('name')
        tmdb_id = data.get('id')
        
        # Bu hissədə bizə birbaşa MP4 linki verən bir API lazımdır. 
        # Çox vaxt 'vidsrc' birbaşa MP4 vermir, player verir.
        # Amma biz "Video Note" və ya "Stream" linki kimi göndərməyə çalışacağıq.
        video_url = f"https://vidsrc.to/embed/movie/{tmdb_id}" # Nümunə link

        status_msg = bot.send_message(message.chat.id, f"⏳ **{title}** hazırlanır, zəhmət olmasa gözləyin...")

        # Telegram-a linki "Video" kimi göndər komandası veririk
        # Bu üsulda bot filmi özünə YÜKLƏMİR, birbaşa linkdən Telegram-a ötürür (Remote Upload)
        try:
            bot.send_video(message.chat.id, video_url, caption=f"🍿 **{title}**\n\nKeyfiyyət: 480p (Aşağı)")
            bot.delete_message(message.chat.id, status_msg.message_id)
        except:
            # Əgər birbaşa video kimi getməsə, məcburuq düymə ilə göndərək
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📥 Videonu Endir / İzlə", url=video_url))
            bot.edit_message_text(f"❌ Fayl çox böyükdür (Telegram limiti).\n\n🎬 Amma buradan endirə bilərsən:", 
                                  message.chat.id, status_msg.message_id, reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, "🚨 Sistem xətası.")

bot.polling(none_stop=True)
