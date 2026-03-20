import os
import telebot
import requests
from telebot import types

# Heroku Config Vars-dan oxuyuruq
TOKEN = os.getenv('BOT_TOKEN')
TMDB_KEY = os.getenv('TMDB_API_KEY')
bot = telebot.TeleBot(TOKEN)

# 1. Start Mesajı
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🎬 **Xeyal Film & Serial Botuna Xoş Gəldiniz!**\n\n"
        "Mən sizə istənilən film və serialı tapmaqda kömək edəcəyəm.\n\n"
        "📖 **Təlimat:**\n"
        "1. Filmin adını bura yazın.\n"
        "2. Qarşınıza çıxan 5 nəticədən birini seçin.\n"
        "3. 'Yüklə və İzlə' düyməsinə basaraq videonu açın.\n\n"
        "🍿 *Xoş izləmələr!*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')

# 2. Axtarış və Top 5 Nəticənin Düymə ilə Göstərilməsi
@bot.message_handler(func=lambda message: True)
def search_top_5(message):
    query = message.text
    search_url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_KEY}&query={query}&language=tr-TR"
    
    try:
        res = requests.get(search_url).json()
        results = res.get('results', [])[:5] # İlk 5 nəticəni götürürük

        if not results:
            bot.reply_to(message, "❌ Təəssüf ki, heç bir nəticə tapılmadı. Adı düzgün yazdığınızdan əmin olun.")
            return

        markup = types.InlineKeyboardMarkup()
        for item in results:
            title = item.get('title') or item.get('name')
            year = (item.get('release_date') or item.get('first_air_date') or "0000")[:4]
            media_type = item.get('media_type', 'movie')
            tmdb_id = item.get('id')
            
            # Düyməyə basanda id və tip göndərilir
            callback_data = f"select_{media_type}_{tmdb_id}"
            markup.add(types.InlineKeyboardButton(text=f"🎬 {title} ({year})", callback_data=callback_data))

        bot.send_message(message.chat.id, f"🔍 '{query}' üçün ən uyğun nəticələr:", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, "🚨 API xətası baş verdi.")

# 3. Seçilən Filmin Detalları və Yükləmə Linki
@bot.callback_query_handler(func=lambda call: call.data.startswith('select_'))
def get_movie_details(call):
    # Data parçalanır: select_movie_12345
    _, m_type, tmdb_id = call.data.split('_')
    
    # Detalları çəkmək üçün TMDB-yə yenidən sorğu
    detail_url = f"https://api.themoviedb.org/3/{m_type}/{tmdb_id}?api_key={TMDB_KEY}&language=tr-TR"
    data = requests.get(detail_url).json()
    
    title = data.get('title') or data.get('name')
    overview = data.get('overview', 'Məlumat yoxdur.')[:200] + "..."
    
    # Video bazası linki (Arxa fonda yükləyib açan pleyer)
    if m_type == 'movie':
        watch_url = f"https://vidsrc.to/embed/movie/{tmdb_id}"
    else:
        watch_url = f"https://vidsrc.to/embed/tv/{tmdb_id}/1/1"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="📥 YÜKLƏ VƏ İZLƏ (MP4)", url=watch_url))

    caption = f"✅ **{title}** seçildi.\n\n📝 **Haqqında:** {overview}\n\n🎬 Videonu aşağıdakı düymədən dərhal açın:"

    poster = data.get('poster_path')
    if poster:
        bot.send_photo(call.message.chat.id, f"https://image.tmdb.org/t/p/w500{poster}", caption=caption, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(call.message.chat.id, caption, reply_markup=markup, parse_mode='Markdown')

bot.polling(none_stop=True)
