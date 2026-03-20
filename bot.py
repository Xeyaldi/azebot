import os
import telebot
import requests
import json

# Heroku-dan Tokeni oxuyuruq
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Variant yaradan funksiya (Eyni qalır)
def generate_variants(base_username):
    variants = [base_username, f"{base_username}06", f"{base_username}_", f"{base_username}."]
    return list(set(variants))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🕵️‍♂️ **XEYAL OSINT v3.1**\n\nKomanda: `/smartfind [username]`", parse_mode='Markdown')

@bot.message_handler(commands=['smartfind'])
def smart_find_user(message):
    try:
        base_username = message.text.split()[1]
        variants = generate_variants(base_username)
        
        bot.send_message(message.chat.id, f"🔍 `{base_username}` üçün {len(variants)} variant yoxlanılır...")
        
        all_results = []
        
        # Ən populyar saytları birbaşa yoxlayaq (Sherlock xətası verməsin deyə)
        platforms = {
            "Instagram": "https://www.instagram.com/{}",
            "GitHub": "https://github.com/{}",
            "TikTok": "https://www.tiktok.com/@{}",
            "Twitter": "https://twitter.com/{}",
            "Pinterest": "https://www.pinterest.com/{}/",
            "Telegram": "https://t.me/{}"
        }

        for nick in variants:
            found_for_nick = []
            for name, url_template in platforms.items():
                url = url_template.format(nick)
                try:
                    # 5 saniyə gözlə, əgər sayt açılsa tapıldı sayılır
                    r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                    if r.status_code == 200:
                        found_for_nick.append(f"✅ {name}: [Keçid]({url})")
                except:
                    continue
            
            if found_for_nick:
                all_results.append(f"👤 **Ad:** `{nick}`\n" + "\n".join(found_for_nick))

        if all_results:
            bot.send_message(message.chat.id, "\n\n---\n\n".join(all_results), parse_mode='Markdown', disable_web_page_preview=True)
        else:
            bot.send_message(message.chat.id, "❌ Heç bir iz tapılmadı.")

    except Exception as e:
        bot.reply_to(message, f"🚨 Xəta: {str(e)}")

bot.polling()
