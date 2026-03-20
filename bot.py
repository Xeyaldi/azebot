import os
import telebot
import time
import threading
import requests
from telebot import types

# Heroku Config Vars (Bunları Heroku-da mütləq qeyd et)
TOKEN = os.getenv('BOT_TOKEN')
TMDB_KEY = os.getenv('TMDB_API_KEY') 
bot = telebot.TeleBot(TOKEN)

# Mesajları 60 saniyə sonra silən funksiya
def auto_delete(chat_id, message_id, seconds=60):
    time.sleep(seconds)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🎬 **Xeyal Film v4.5 (API Powered)**\n\n"
        "İstədiyiniz film və ya serialın adını yazın.\n"
        "Mən dünyanın ən böyük bazalarından (TMDB & Vidsrc) tapıb gətirəcəm.\n\n"
        "🛡 **Gizlilik:** Mesajlar 1 dəqiqə sonra silinir."
    )
    msg = bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')
    # Start mesajlarını 30 saniyə sonra silirik
    threading.Thread(target=auto_delete, args=(message.chat.id, msg.message_id, 30)).start()
    threading.Thread(target=auto_delete, args=(message.chat.id, message.message_id, 30)).start()

@bot.message_handler(func=lambda message: True)
def search_media(message):
    query = message.text
    # 1. TMDB API ilə filmi axtarırıq (Ağıllı Axtarış)
    search_url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_KEY}&query={query}&language=tr-TR"
    
    try:
        res = requests.get(search_url).json()
        if not res.get('results'):
            bot.reply_to(message, "❌ Təəssüf ki, bu adla heç bir film tapılmadı.")
            return

        data = res['results'][0]
        m_type = data.get('media_type', 'movie')
        title = data.get('title') or data.get('name')
        tmdb_id = data.get('id')
        poster = data.get('poster_path')
        year = (data.get('release_date') or data.get('first_air_date') or "0000")[:4]

        # 2. Video API Linkləri (Vidsrc bazası)
        if m_type == 'movie':
            # Film üçün birbaşa TMDB ID ilə link qururuq (Ən dəqiq yol budur)
            watch_url = f"https://vidsrc.to/embed/movie/{tmdb_id}"
        else:
            # Serial üçün (Sezon 1, Bölüm 1 olaraq açılır)
            watch_url = f"https://vidsrc.to/embed/tv/{tmdb_id}/1/1"

        # Düymə
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"▶️ {title} ({year}) İzlə", url=watch_url))

        caption = f"🍿 **Nəticə:** {title}\n📅 **İl:** {year}\n\n⚠️ _Bu mesaj 60 saniyə sonra silinəcək._"

        if poster:
            img_url = f"https://image.tmdb.org/t/p/w500{poster}"
            sent_msg = bot.send_photo(message.chat.id, img_url, caption=caption, parse_mode='Markdown', reply_markup=markup)
        else:
            sent_msg = bot.send_message(message.chat.id, caption, parse_mode='Markdown', reply_markup=markup)

        # 3. Avtomatik Silmə İşləri
        threading.Thread(target=auto_delete, args=(message.chat.id, message.message_id, 60)).start()
        threading.Thread(target=auto_delete, args=(message.chat.id, sent_msg.message_id, 60)).start()

    except Exception as e:
        print(f"Xəta: {e}")
        bot.reply_to(message, "🚨 API bağlantısında xəta baş verdi.")

bot.polling(none_stop=True)
