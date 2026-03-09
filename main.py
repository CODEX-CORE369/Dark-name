import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import time
from pymongo import MongoClient
import os
import requests
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running on Render!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    port = int(os.environ.get('PORT', 8080))
    URL = os.environ.get('RENDER_EXTERNAL_URL', f"http://localhost:{port}")
    while True:
        time.sleep(10)
        try:
            requests.get(URL)
            print(f"[PING] Pinging server ({URL}) to stay awake...")
        except Exception as e:
            print(f"[PING] Ping failed: {e}")
        time.sleep(300)

BOT_TOKEN = "8773837287:AAFZDqWyq1kac9tSAGehIDxSSDzLECU0fHg"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

MONGO_URI = "mongodb+srv://dxsimu:mnbvcxzdx@dxsimu.0qrxmsr.mongodb.net/?appName=dxsimu"
client = MongoClient(MONGO_URI)
db = client["DARK-NAMEX"]
sudo_db = db["sudo_users"]

OWNER_ID = [6703335929, 5136260272, 6737589257, 7819700191]
SPECIAL_OWNERS = [6703335929, 5136260272]

USER_MODES = {6703335929: 1, 5136260272: 1}

CHAR_MAP = {
    'a': 'ａ', 'b': 'ｂ', 'c': 'ｃ', 'd': 'ｄ', 'e': 'ｅ', 'f': 'ｆ', 'g': 'ｇ', 'h': 'ｈ', 'i': 'ｉ', 
    'j': 'ｊ', 'k': 'ｋ', 'l': 'ｌ', 'm': 'ｍ', 'n': 'ｎ', 'o': 'ｏ', 'p': 'ｐ', 'q': 'ｑ', 'r': 'ｒ', 
    's': 'ｓ', 't': 'ｔ', 'u': 'ｕ', 'v': 'ｖ', 'w': 'ｗ', 'x': 'ｘ', 'y': 'ｙ', 'z': 'ｚ',
    'A': 'Ａ', 'B': 'Ｂ', 'C': 'Ｃ', 'D': 'Ｄ', 'E': 'Ｅ', 'F': 'Ｆ', 'G': 'Ｇ', 'H': 'Ｈ', 'I': 'Ｉ', 
    'J': 'Ｊ', 'K': 'Ｋ', 'L': 'Ｌ', 'M': 'Ｍ', 'N': 'Ｎ', 'O': 'Ｏ', 'P': 'Ｐ', 'Q': 'Ｑ', 'R': 'Ｒ', 
    'S': 'Ｓ', 'T': 'Ｔ', 'U': 'Ｕ', 'V': 'Ｖ', 'W': 'Ｗ', 'X': 'Ｘ', 'Y': 'Ｙ', 'Z': 'Ｚ',
    '0': '０', '1': '１', '2': '２', '3': '３', '4': '４', '5': '５', '6': '６', '7': '৭', '8': '৮', '9': '৯',
    '-': '－', '&': '＆', '=': '＝', '/': '／', '$': '＄', '%': '％', '?': '？', ',': '，', ';': '；', 
    ':': '：', '"': '＂', "'": '＇', '!': '！', '@': '＠', '#': '＃', '.': '．', ' ': '－'
}

FONT_MAP = {
    'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ғ','g':'ɢ','h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ',
    'n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ','s':'s','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ',
    'A':'ᴀ','B':'ʙ','C':'ᴄ','D':'ᴅ','E':'ᴇ','F':'ғ','G':'ɢ','H':'ʜ','I':'ɪ','J':'ᴊ','K':'ᴋ','L':'ʟ','M':'ᴍ',
    'N':'ɴ','O':'ᴏ','P':'ᴘ','Q':'ǫ','R':'ʀ','S':'s','T':'ᴛ','U':'ᴜ','V':'ᴠ','W':'ᴡ','X':'x','Y':'ʏ','Z':'ᴢ'
}

BORDERS = {
    'short': [
        "┏━━━━━━━━━━━━━━━┓\n┣ \n┗━━━━━━━━━━━━━━━┛",
        "╭─── •✧✧• ───╮\n│ \n╰─── •✧✧• ───╯",
        "╔════ ≪ °❈° ≫ ════╗\n║ \n╚════ ≪ °❈° ≫ ════╝",
        "┌──❀*̥˚─────❀*̥˚─┐\n│ \n└───────❀*̥˚───┘",
        "╭─✰───────────╮\n│ \n╰───────────✰─╯",
        "┏━✦ ━━━━━━━━━ ✦━┓\n┣ \n┗━✦ ━━━━━━━━━ ✦━┛",
        "╒═══════✰°\n│ \n°✰═══════╛",
        "╭┈─────── ೄྀ࿐ ˊˎ-\n╰┈➤ \n╰─────────────➤",
        "┏━°⌜ 赤 ⌟°━┓\n┣ \n┗━°⌜ 赤 ⌟°━┛",
        "┌─── ･ ｡ﾟ☆: *.☽ .* :☆ﾟ. ───┐\n│ \n└─── ･ ｡ﾟ☆: *.☽ .* :☆ﾟ. ───┘",
        "┏━「  」\n┣ \n┗━╼"
    ],
    'dashboard': [
        "┏━━「 ᴅᴀsʜʙᴏᴀʀᴅ 」━━┓\n┃ ┏─「 ᴜsᴇʀ ᴘʀᴏғɪʟᴇ 」\n┃ ┃ 👤 ɴᴀᴍᴇ: \n┃ ┃ 🆔 ɪᴅ: \n┃ ┗───────────╼\n┃ ┏─「 ʙᴏᴛ ғᴇᴀᴛᴜʀᴇs 」\n┃ ┃ ✅ \n┃ ┃ ✅ \n┃ ┃ ✅ \n┃ ┃ ✅ \n┃ ┗───────────╼\n┃ ┏─「 ʜᴏᴡ ᴛᴏ ᴏᴘᴇʀᴀᴛᴇ 」\n┃ ┃ 1️⃣ \n┃ ┃ 2️⃣ \n┃ ┃ 3️⃣ \n┃ ┃ 4️⃣ \n┃ ┗───────────╼\n┃ ┏─「 sʏsᴛᴇᴍ ɪɴғᴏ 」\n┃ ┃ 👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: Ｄｘ－Ｓｉｍｕ\n┃ ┗───────────╼\n┗━━━━━━━━━━┛",
        "┏━━「 ᴅᴀsʜʙᴏᴀʀᴅ 」━━┓\n┃ ┏─「 ᴜsᴇʀ ᴘʀᴏғɪʟᴇ 」\n┃ ┃ 👤 ɴᴀᴍᴇ: \n┃ ┃ 🆔 ɪᴅ: \n┃ ┗───────────╼\n┃ \n┃ ┏─「 ʙᴏᴛ ғᴇᴀᴛᴜʀᴇs 」\n┃ ┃ 🗑 \n┃ ┃ 📌 \n┃ ┃ 🔊 \n┃ ┃ 🚀 \n┃ ┗───────────╼\n┗━━━━━━━━━━┛",
        "╭─── ⋆⋅☆⋅⋆ ───╮\n│ 👤 ᴜsᴇʀ: \n│ 🆔 ɪᴅ: \n│ 🛡️ ʀᴏʟᴇ: \n╰─── ⋆⋅☆⋅⋆ ───╯",
        "┏━✦ ᴘʀᴏғɪʟᴇ ✦━┓\n┣ ɴᴀᴍᴇ: \n┣ ᴀɢᴇ: \n┗━✦ ━━━━━━ ✦━┛",
        "╔═════ ≪ ᴘᴀɴᴇʟ ≫ ═════╗\n║ ➣ ᴏᴘᴛɪᴏɴ 𝟷\n║ ➣ ᴏᴘᴛɪᴏɴ 𝟸\n╚══════════════════╝"
    ],
    'music': [
        "┏━♬ ɴᴏᴡ ᴘʟᴀʏɪɴɢ ♬━┓\n┣ 🎵 ᴛʀᴀᴄᴋ: \n┣ 🎤 ᴀʀᴛɪsᴛ: \n┣ ⏳ 0:00 ───|────── 3:14\n┣ ↻ ◁ II ▷ ↺\n┗━━━━━━━━━━━━━━━┛",
        "╭─── 🎧 sᴏɴɢ ɪɴғᴏ ───╮\n│ 💿 ᴀʟʙᴜᴍ: \n│ 🎶 ɢᴇɴʀᴇ: \n╰──────────────────╯",
        "╔═════ ≪ ᴍᴜsɪᴄ ≫ ═════╗\n║ 🔊 ᴠᴏʟᴜᴍᴇ: ▮▮▮▮▮▯▯\n║ ▶ ᴘʟᴀʏɪɴɢ: \n╚══════════════════╝"
    ],
    'warning': [
        "┏━⚠️ ᴡᴀʀɴɪɴɢ ⚠️━┓\n┣ 🚫 ᴇʀʀᴏʀ: \n┣ 🛑 sᴛᴀᴛᴜs: \n┗━━━━━━━━━━━━━━┛",
        "╭─── ☠️ ᴀʟᴇʀᴛ ☠️ ───╮\n│ ⚠️ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ\n╰─────────────────╯",
        "╔════ ≪ ᴄʀɪᴛɪᴄᴀʟ ≫ ════╗\n║ ❌ ғᴀɪʟᴇᴅ ᴛᴏ ʟᴏᴀᴅ\n╚══════════════════╝"
    ],
    'info': [
        "┏━━「 ✅ ᴄʟᴀɪᴍᴇᴅ 」━━┓\n┃ 👤 ᴜsᴇʀ: \n┃ 💰 ʀᴇᴡᴀʀᴅ: +1 ᴄᴏɪɴ\n┗━━━━━━━━━━━━━━┛",
        "┏━━「 sᴛᴀᴛs 」━━┓\n┃ 📊 sʏsᴛᴇᴍ sᴛᴀᴛɪsᴛɪᴄs\n┗───────────╼\n┃ 👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: \n┃ 🔗 ᴀᴄᴛɪᴠᴇ ʟɪɴks: \n┃ 🚫 ʙᴀɴɴᴇᴅ ᴜsᴇʀs: \n┗━━━━━━━━━━┛",
        "╭─ ✧ sʏsᴛᴇᴍ ɪɴғᴏ ✧ ─╮\n│ 💻 ᴄᴘᴜ: \n│ 💾 ʀᴀᴍ: \n│ ⏱️ ᴜᴘᴛɪᴍᴇ: \n╰──────────────────╯",
        "┌──< sᴇᴛᴛɪɴɢs >──┐\n│ ⚙️ ᴍᴏᴅᴇ: \n│ 🔔 ᴀʟᴇʀᴛs: \n└────────────┘",
        "╭━━━━〔 ɪɴᴅᴇx 〕━━━━╮\n┃ 📑 ᴘᴀɢᴇ: \n┃ 📌 sᴛᴀᴛᴜs: \n╰━━━━━━━━━━━━━━━╯"
    ]
}

def get_sudo_list():
    return list(sudo_db.find())

def is_owner(uid):
    return uid in OWNER_ID

def is_authorized(uid):
    return is_owner(uid) or sudo_db.find_one({"_id": uid}) is not None

def sync_user(user):
    if is_authorized(user.id) and not is_owner(user.id):
        full_name = f"{user.first_name} {user.last_name or ''}".strip()
        sudo_db.update_one({"_id": user.id}, {"$set": {"name": full_name}}, upsert=True)

@bot.message_handler(commands=['start'])
def welcome_dashboard(message):
    sync_user(message.from_user)
    uid = message.from_user.id
    if not is_authorized(uid): return

    codex = '<a href="https://t.me/Dxcodexbot">Ｄｘ－Ｓｉｍｕ</a>'  
    role = "👑 ᴏᴡɴᴇʀ" if is_owner(uid) else "⚡ ꜱᴜᴅᴏ"
    
    msg = (
        f"<b>┏━「 ᴅᴀsʜʙᴏᴀʀᴅ 」\n"
        f"┣ 👤 ɴᴀᴍᴇ: {message.from_user.first_name}\n"
        f"┣ 🆔 ɪᴅ: <code>{message.from_user.id}</code>\n"
        f"┣ 🛡️ ʀᴏʟᴇ: {role}\n"
        f"┗━➾ 👨‍💻 ᴅᴇᴠ: {codex}</b>"
    )
    
    markup = None
    if uid in SPECIAL_OWNERS:
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("✨ ᴍᴏᴅᴇ 𝟷 (ᴏʀɪɢɪɴᴀʟ)", callback_data="set_mode_1"))
        markup.row(InlineKeyboardButton("🔠 ᴍᴏᴅᴇ 𝟸 (sᴍᴀʟʟ ᴄᴀᴘs)", callback_data="set_mode_2"))
    
    bot.reply_to(message, msg, disable_web_page_preview=True, reply_markup=markup)

@bot.message_handler(commands=['sudo'])
def handle_sudo(message):
    uid = message.from_user.id
    if not is_authorized(uid): return
    
    args = message.text.split()
    
    if len(args) == 1:
        bot.send_chat_action(message.chat.id, 'typing')
        sudo_users = get_sudo_list()
        if not sudo_users:
            return bot.reply_to(message, "<b>┏━「 ꜱᴜᴅᴏ ʟɪꜱᴛ 」\n┗ ➾ 🚫 ɴᴏ ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ.</b>")
        
        id_list = ""
        for user in sudo_users:
            s_id = user["_id"]
            s_name = user.get("name", "ᴜɴᴋɴᴏᴡɴ (ɴᴏᴛ sᴛᴀʀᴛᴇᴅ)")
            mention = f"<a href='tg://user?id={s_id}'>{s_name}</a>"
            id_list += f"┣ 🆔 <code>{s_id}</code>\n┃ ┗ 👤 {mention}\n"
            
        msg = f"<b>┏━「 ꜱᴜᴅᴏ ʟɪꜱᴛ 」\n{id_list}┗━➾ ᴛᴏᴛᴀʟ: {len(sudo_users)}</b>"
        return bot.reply_to(message, msg, disable_web_page_preview=True)

    if is_owner(uid):
        new_id = args[1]
        if new_id.isdigit():
            new_id = int(new_id)
            if new_id in OWNER_ID or sudo_db.find_one({"_id": new_id}):
                return bot.reply_to(message, "⚠️ <b>ᴀʟʀᴇᴀᴅʏ ɪɴ ʟɪꜱᴛ.</b>")
            
            try:
                u_info = bot.get_chat(new_id)
                u_name = f"{u_info.first_name} {u_info.last_name or ''}".strip()
            except:
                u_name = "Not Started Yet"
                
            sudo_db.insert_one({"_id": new_id, "name": u_name})
            bot.reply_to(message, f"<b>┏━「 ꜱᴜᴅᴏ ᴀᴅᴅᴇᴅ 」\n┗ ➾ ✅ ɪᴅ: <code>{new_id}</code></b>")
        else:
            bot.reply_to(message, "❌ <b>ᴠᴀʟɪᴅ ɪᴅ ᴘʟᴇᴀsᴇ.</b>")

@bot.message_handler(commands=['rm'])
def handle_remove(message):
    if not is_owner(message.from_user.id): return
    
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        target_id = int(args[1])
        if sudo_db.find_one({"_id": target_id}):
            sudo_db.delete_one({"_id": target_id})
            bot.reply_to(message, f"<b>┏━「 ꜱᴜᴅᴏ ʀᴇᴍᴏᴠᴇᴅ 」\n┗ ➾ 🗑️ ɪᴅ: <code>{target_id}</code></b>")
        else:
            bot.reply_to(message, "⚠️ <b>ɴᴏᴛ ꜰᴏᴜɴᴅ.</b>")

@bot.message_handler(commands=['border'])
def border_handler(message):
    uid = message.from_user.id
    if uid not in SPECIAL_OWNERS: return
    
    args = message.text.split()
    if len(args) == 1:
        send_border_page(message.chat.id, "short", 0)
    else:
        category = args[1].lower()
        if category == "list":
            cats = list(BORDERS.keys())
            cat_text = "<b>┏━「 ʙᴏʀᴅᴇʀ ᴄᴀᴛᴇɢᴏʀɪᴇs 」</b>\n"
            for c in cats:
                cat_text += f"┣ ✧ <code>/border {c}</code>\n"
            cat_text += "<b>┗━╼</b>"
            bot.reply_to(message, cat_text, parse_mode='HTML')
        elif category in BORDERS:
            send_border_page(message.chat.id, category, 0)
        else:
            bot.reply_to(message, "⚠️ <b>ᴄᴀᴛᴇɢᴏʀʏ ɴᴏᴛ ғᴏᴜɴᴅ. ᴜsᴇ /border list</b>", parse_mode='HTML')

def send_border_page(chat_id, category, page_idx, message_id=None):
    items = BORDERS.get(category)
    if not items: return
    
    total = len(items)
    page_idx = page_idx % total
    
    border_text = f"<b>┏━「 {category.upper()} ʙᴏʀᴅᴇʀ ({page_idx+1}/{total}) 」</b>\n<code>{items[page_idx]}</code>"
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("⬅️ ᴘᴇᴠ", callback_data=f"bdr_{category}_{page_idx-1}"),
        InlineKeyboardButton("📋 ᴄᴏᴘʏ", callback_data="copy_hint"),
        InlineKeyboardButton("ɴᴇxᴛ ➡️", callback_data=f"bdr_{category}_{page_idx+1}")
    )
    
    if message_id:
        bot.edit_message_text(border_text, chat_id, message_id, reply_markup=markup, parse_mode='HTML')
    else:
        bot.send_message(chat_id, border_text, reply_markup=markup, parse_mode='HTML')

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def process_style(message):
    uid = message.from_user.id
    if not is_authorized(uid): return
    sync_user(message.from_user)
    bot.send_chat_action(message.chat.id, 'typing')
    
    mode = USER_MODES.get(uid, 1)
    
    if uid in SPECIAL_OWNERS and mode == 2:
        styled_text = "".join([FONT_MAP.get(c, c) for c in message.text])
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📝 ᴄᴏᴘʏ", callback_data="copy_hint"))
        
        msg = f"<code>{styled_text}</code>"
        bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode='HTML')
        
    else:
        clean_text = re.sub(r'[_.]', ' ', message.text).strip()
        words = re.split(r'[- ]+', clean_text)
        normalized = "-".join([w.capitalize() for w in words if w])
        styled_base = "".join([CHAR_MAP.get(c, c) for c in normalized])
        
        style1 = f"「𖣂」{styled_base}ايڪـͬــͤــᷜــͨــͣــͪـي"
        style2 = styled_base
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📝 ᴄᴏᴘʏ", callback_data="copy_hint"))
        
        msg1 = f"<b>┏━「 sᴛʏʟᴇ 𝟷 」</b>\n┣ <code>{style1}</code>\n<b>┗━╼</b>"
        bot.send_message(message.chat.id, msg1, reply_markup=markup)
        
        msg2 = f"<b>┏━「 sᴛʏʟᴇ 𝟸 」</b>\n┣ <code>{style2}</code>\n<b>┗━╼</b>"
        bot.send_message(message.chat.id, msg2, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    data = call.data
    
    if data == "copy_hint":
        bot.answer_callback_query(call.id, "👆 ᴛᴇxᴛ-ᴇ ᴄʟɪᴄᴋ ᴋᴏʀᴜɴ ᴄᴏᴘʏ ʜᴏʏᴇ ᴊᴀʙᴇ!", show_alert=True)
        
    elif data.startswith("set_mode_"):
        if uid not in SPECIAL_OWNERS:
            return bot.answer_callback_query(call.id, "❌ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ!", show_alert=True)
        mode = int(data.split("_")[2])
        USER_MODES[uid] = mode
        bot.answer_callback_query(call.id, f"✅ sᴛʏʟᴇ ᴍᴏᴅᴇ {mode} ᴀᴄᴛɪᴠᴀᴛᴇᴅ!", show_alert=True)
        
    elif data.startswith("bdr_"):
        if uid not in SPECIAL_OWNERS: return
        _, category, page = data.split("_")
        send_border_page(call.message.chat.id, category, int(page), call.message.message_id)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    
    print(">> NIKO is Online. System Secured by DX-CODEX.")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
