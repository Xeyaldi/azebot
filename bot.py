import os
import telebot
import requests

# Heroku-dan gələcək Tokeni oxuyuruq
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Start Mesajı
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_first_name = message.from_user.first_name
    welcome_text = (
        f"🕵️‍♂️ **Salam, {user_first_name}!**\n\n"
        "Mən **Xeyal OSINT Bot**-am. Rəqəmsal dünyada gizli məlumatları tapmaq üçün proqramlaşdırılmışam.\n\n"
        "🔍 **Nələri edə bilərəm?**\n"
        "• `/search [username]` — Sosial şəbəkələrdə axtarış\n"
        "• `/ip [ip_adresi]` — IP haqqında məlumat\n"
        "• `/info` — Bot haqqında məlumat\n\n"
        "⚡ *Diqqət:* Bu bot sırf təhsil və təhlükəsizlik məqsədilə yaradılıb."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# Username Axtarışı
@bot.message_handler(commands=['search'])
def search_user(message):
    try:
        username = message.text.split()[1]
        msg = bot.send_message(message.chat.id, f"🔎 `{username}` axtarılır...", parse_mode='Markdown')
        
        platforms = {
            "GitHub": f"https://github.com/{username}",
            "Instagram": f"https://www.instagram.com/{username}",
            "TikTok": f"https://www.tiktok.com/@{username}",
            "Twitter": f"https://twitter.com/{username}"
        }
        
        results = []
        for name, url in platforms.items():
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                results.append(f"✅ {name}: [Keçid et]({url})")
            else:
                results.append(f"❌ {name}: Tapılmadı")
        
        bot.edit_message_text("\n".join(results), message.chat.id, msg.message_id, parse_mode='Markdown', disable_web_page_preview=True)
    except IndexError:
        bot.reply_to(message, "⚠️ Zəhmət olmasa istifadəçi adını yazın. Məsələn: `/search xeyaldi`", parse_mode='Markdown')

# IP Axtarışı
@bot.message_handler(commands=['ip'])
def ip_info(message):
    try:
        ip = message.text.split()[1]
        data = requests.get(f"http://ip-api.com/json/{ip}").json()
        
        if data['status'] == 'success':
            response = (
                f"🌍 **IP Analizi:** `{ip}`\n\n"
                f"📍 Ölkə: {data['country']}\n"
                f"🏙️ Şəhər: {data['city']}\n"
                f"📶 Provayder: {data['isp']}\n"
                f"🗺️ Koordinat: {data['lat']}, {data['lon']}"
            )
        else:
            response = "❌ IP ünvanı yanlışdır və ya məlumat tapılmadı."
            
        bot.reply_to(message, response, parse_mode='Markdown')
    except IndexError:
        bot.reply_to(message, "⚠️ IP ünvanını yazın. Məsələn: `/ip 8.8.8.8`", parse_mode='Markdown')

bot.polling()
