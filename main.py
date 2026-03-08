import os
import time
import threading
import requests
import telebot
from telebot.types import Message
from pymongo import MongoClient
from flask import Flask
from sambanova import SambaNova
import html # Added for safe formatting fallback

# ================= Configuration ================= #
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" # Tumi tomar token bosao
MONGO_URI = "YOUR_MONGO_URI_HERE" # Tumi tomar URI bosao
SAMBA_API_KEY = "057d42ba-2ab5-4afa-a35b-78446a8ed165"

OWNER_IDS = [6703335929, 5136260272]

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
app = Flask(__name__)

# ================= MongoDB Setup ================= #
client_db = MongoClient(MONGO_URI)
db = client_db["dxsimu"]
sudo_collection = db["CODE-AI"]

def get_sudo_users():
    users = sudo_collection.find()
    return [user["user_id"] for user in users]

def add_sudo_user(user_id):
    if not sudo_collection.find_one({"user_id": user_id}):
        sudo_collection.insert_one({"user_id": user_id})

def remove_sudo_user(user_id):
    sudo_collection.delete_one({"user_id": user_id})

# ================= Fancy Font System ================= #
def fancy_text(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    fancy =  "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    mapping = str.maketrans(normal, fancy)
    return text.translate(mapping)

# ================= SambaNova AI Setup ================= #
ai_client = SambaNova(
    api_key=SAMBA_API_KEY,
    base_url="https://api.sambanova.ai/v1",
)

# [HYPER LOGIC] Strict System Prompt for Telegram HTML
SYSTEM_PROMPT = """You are Dx-Simu, an advanced AI chatbot. 
Your model name is "niko 1.0" and your developer is "DX-CODEX".

CRITICAL HTML FORMATTING RULES FOR TELEGRAM:
1. You MUST ONLY use these EXACT HTML tags: <b>, <i>, <u>, <s>, <code>, <pre>, <blockquote>.
2. DO NOT USE <ul>, <ol>, <li>, <p>, <br>, <h1>, <h2>, etc. Use standard characters like "-" for bullets.
3. For CODE blocks, you MUST use this format: <pre><code class="language-python">code here</code></pre>.
4. For inline code or filenames, use <code>name</code>.
5. For titles or important text, use <b>Title</b>.
6. Absolutely NO markdown like **bold** or `code`. ONLY use the allowed HTML tags.
Answer strictly in the requested language."""

# ================= Keep Alive & Web Server ================= #
@app.route('/')
def home():
    return "Dx-Simu Bot is Running perfectly!"

def keep_alive():
    B = "INFO" 
    port = int(os.environ.get('PORT', 8080))
    URL = os.environ.get('RENDER_EXTERNAL_URL', f"http://localhost:{port}")
    while True:
        try:
            requests.get(URL)
            print(f"[{B}] Pinging server ({URL}) to stay awake...")
        except Exception as e:
            print(f"[{B}] Ping failed: {e}")
        time.sleep(300)

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# ================= Authorization Check ================= #
def is_authorized(user_id):
    if user_id in OWNER_IDS:
        return True
    if user_id in get_sudo_users():
        return True
    return False

# ================= Bot Commands ================= #

@bot.message_handler(commands=['start'])
def start_cmd(message: Message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, fancy_text("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ. ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ."))
        return
    text = fancy_text("ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴅx-sɪᴍᴜ (ɴɪᴋᴏ 1.0)!\n\nɪ ᴀᴍ ʀᴇᴀᴅʏ ᴛᴏ ᴀssɪsᴛ ʏᴏᴜ. sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴏʀ ᴄᴏᴅᴇ ᴘʀᴏᴍᴘᴛ.")
    bot.reply_to(message, text)

@bot.message_handler(commands=['sudo'])
def sudo_manager(message: Message):
    if message.from_user.id not in OWNER_IDS:
        bot.reply_to(message, fancy_text("ᴏɴʟʏ ᴛʜᴇ sᴜᴘʀᴇᴍᴇ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!"))
        return

    parts = message.text.split()
    if len(parts) == 1:
        users = get_sudo_users()
        if not users:
            bot.reply_to(message, fancy_text("sᴜᴅᴏ ʟɪsᴛ ɪs ᴇᴍᴘᴛʏ."))
        else:
            msg = fancy_text("ᴄᴜʀʀᴇɴᴛ sᴜᴅᴏ ᴜsᴇʀs:\n") + "\n".join([f"<code>{u}</code>" for u in users])
            bot.reply_to(message, msg)
    else:
        try:
            new_id = int(parts[1])
            add_sudo_user(new_id)
            bot.reply_to(message, fancy_text(f"sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ {new_id} ᴛᴏ sᴜᴅᴏ ʟɪsᴛ!"))
        except ValueError:
            bot.reply_to(message, fancy_text("ɪɴᴠᴀʟɪᴅ ɪᴅ ғᴏʀᴍᴀᴛ."))

@bot.message_handler(commands=['rm'])
def rm_sudo(message: Message):
    if message.from_user.id not in OWNER_IDS:
        bot.reply_to(message, fancy_text("ᴏɴʟʏ ᴛʜᴇ sᴜᴘʀᴇᴍᴇ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!"))
        return
    
    parts = message.text.split()
    if len(parts) > 1:
        try:
            rm_id = int(parts[1])
            remove_sudo_user(rm_id)
            bot.reply_to(message, fancy_text(f"sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ {rm_id} ғʀᴏᴍ sᴜᴅᴏ ʟɪsᴛ!"))
        except ValueError:
            bot.reply_to(message, fancy_text("ɪɴᴠᴀʟɪᴅ ɪᴅ ғᴏʀᴍᴀᴛ."))
    else:
        bot.reply_to(message, fancy_text("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ɪᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ. ᴇxᴀᴍᴘʟᴇ: /ʀᴍ 12345678"))

# ================= Chat Handler ================= #
@bot.message_handler(func=lambda message: True)
def ai_chat(message: Message):
    if not is_authorized(message.from_user.id):
        return
    
    loading_text = fancy_text("⏳ ᴘ ʀ ᴏ ᴄ ᴇ s s ɪ ɴ ɢ   ʏ ᴏ ᴜ ʀ   ʀ ᴇ ǫ ᴜ ᴇ s ᴛ . . .")
    sent_msg = bot.reply_to(message, f"<b>{loading_text}</b>")
    
    try:
        response = ai_client.chat.completions.create(
            model="ALLaM-7B-Instruct-preview",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.3,
            top_p=0.9
        )
        
        reply_text = response.choices[0].message.content
        
        # [HYPER LOGIC] Fail-safe editing to handle Telegram formatting issues
        try:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=sent_msg.message_id,
                text=reply_text,
                parse_mode='HTML'
            )
        except telebot.apihelper.ApiTelegramException as e:
            if 'parse entities' in str(e):
                # AI gave invalid HTML. Let's escape it and send it safely inside a <pre> tag!
                safe_text = html.escape(reply_text)
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_msg.message_id,
                    text=f"<b>[Formatting Fixed]</b>\n<pre>{safe_text}</pre>",
                    parse_mode='HTML'
                )
            else:
                raise e # Throw other Telegram errors to the main exception block
            
    except Exception as e:
        error_msg = fancy_text("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ɢᴇɴᴇʀᴀᴛɪɴɢ ʀᴇsᴘᴏɴsᴇ.")
        # Catch tokenization or API errors nicely
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=sent_msg.message_id,
            text=f"<b>{error_msg}</b>\n\n<pre>Error Details:\n{html.escape(str(e))}</pre>",
            parse_mode='HTML'
        )

# ================= Main Execution ================= #
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    
    print(fancy_text("[ ɪɴғᴏ ] ᴅx-sɪᴍᴜ ʙᴏᴛ ɪs sᴛᴀʀᴛɪɴɢ..."))
    bot.infinity_polling(skip_pending=True)
