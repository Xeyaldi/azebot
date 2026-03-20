import os
import telebot
import subprocess # Sherlock-u çağırmaq üçün
import time

# Heroku-dan Tokeni oxuyuruq
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- Ağıllı Variant Yaradan Funksiya ---
def generate_variants(base_username):
    # Bu siyahı hədəfin istifadə edə biləcəyi ehtimal olunan ləqəbləri yaradır
    variants = [
        base_username,
        f"{base_username}06",    # Doğum ili və ya rayon kodu təxmini
        f"{base_username}2006",
        f"{base_username}_",      
        f"{base_username}.",      
        f"{base_username}_official",
        f"iam{base_username}",
        f"real{base_username}"
    ]
    # Təkrarları silirik və siyahını qaytarırıq
    return list(set(variants))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
        "💀 **SHERLOCK SMART ENGINE v3.0 ACTİVE**\n\n"
        "İstifadəçi adını yaz, 400+ saytda və 10-dan çox variantda axtarım:\n\n"
        "👉 `/smartfind [username]`", 
        parse_mode='Markdown')

@bot.message_handler(commands=['smartfind'])
def smart_find_user(message):
    try:
        base_username = message.text.split()[1]
        
        # Ağıllı variantları yaradırıq
        variants = generate_variants(base_username)
        
        start_msg = bot.send_message(message.chat.id, 
            f"🧠 **Ağıllı Analiz Başladı...**\n`{base_username}` üçün {len(variants)} fərqli variant (ləqəb) yoxlanılır.\n\n"
            "(Bu bir az vaxt ala bilər, zəhmət olmasa gözləyin)", parse_mode='Markdown')
        
        all_found_links = []
        
        for nick in variants:
            # Hər variant üçün Sherlock-u işə salırıq
            # --timeout 1: sayt cavab verməsə çox gözləməsin
            cmd = f"sherlock {nick} --timeout 1 --print-found"
            
            # Prosesi başladırıq
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, _ = process.communicate()

            if stdout:
                # Tapılan linkləri təmizləyib siyahıya əlavə edirik
                found_links = [line for line in stdout.split('\n') if "http" in line]
                if found_links:
                    all_found_links.append(f"👤 **Ad:** `{nick}`\n" + "\n".join(found_links))
        
        if all_found_links:
            final_text = "\n\n---\n\n".join(all_found_links)
            
            # Mesaj çox uzundursa, hissə-hissə göndər (Telegram mesaj limiti 4096 simvoldur)
            if len(final_text) > 4000:
                for i in range(0, len(final_text), 4000):
                    bot.send_message(message.chat.id, final_text[i:i+4000], disable_web_page_preview=True)
            else:
                bot.send_message(message.chat.id, f"🎯 **Tapılan Hesablar:**\n\n{final_text}", parse_mode='Markdown', disable_web_page_preview=True)
        else:
            bot.send_message(message.chat.id, "❌ Heç bir variantda nəticə tapılmadı.")

    except IndexError:
        bot.reply_to(message, "⚠️ Zəhmət olmasa istifadəçi adını yazın. Məsələn: `/smartfind xeyaldi`", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"🚨 Sistem xətası: {str(e)}")

bot.polling()
