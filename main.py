import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import time
from pymongo import MongoClient

# --- CONFIGURATION ---
BOT_TOKEN = "8773837287:AAFZDqWyq1kac9tSAGehIDxSSDzLECU0fHg"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# MongoDB Connection
MONGO_URI = "mongodb+srv://dxsimu:mnbvcxzdx@dxsimu.0qrxmsr.mongodb.net/?appName=dxsimu"
client = MongoClient(MONGO_URI)
db = client["DARK-NAMEX"]
sudo_db = db["sudo_users"]

# Constant Owners
OWNER_ID = [6703335929, 5136260272, 6737589257, 7819700191]
SPECIAL_OWNERS = [6703335929, 5136260272]

# Active Modes for Special Owners (Default is 1)
USER_MODES = {6703335929: 1, 5136260272: 1}

# Character Map for Styling (Mode 1)
CHAR_MAP = {
    'a': 'ａ', 'b': 'ｂ', 'c': 'ｃ', 'd': 'ｄ', 'e': 'ｅ', 'f': 'ｆ', 'g': 'ｇ', 'h': 'ｈ', 'i': 'ｉ', 
    'j': 'ｊ', 'k': 'ｋ', 'l': 'ｌ', 'm': 'ｍ', 'n': 'ｎ', 'o': 'ｏ', 'p': 'ｐ', 'q': 'ｑ', 'r': 'ｒ', 
    's': 'ｓ', 't': 'ｔ', 'u': 'ｕ', 'v': 'ｖ', 'w': 'ｗ', 'x': 'ｘ', 'y': 'ｙ', 'z': 'ｚ',
    'A': 'Ａ', 'B': 'Ｂ', 'C': 'Ｃ', 'D': 'Ｄ', 'E': 'Ｅ', 'F': 'Ｆ', 'G': 'Ｇ', 'H': 'Ｈ', 'I': 'Ｉ', 
    'J': 'Ｊ', 'K': 'Ｋ', 'L': 'Ｌ', 'M': 'Ｍ', 'N': 'Ｎ', 'O': 'Ｏ', 'P': 'Ｐ', 'Q': 'Ｑ', 'R': 'Ｒ', 
    'S': 'Ｓ', 'T': 'Ｔ', 'U': 'Ｕ', 'V': 'Ｖ', 'W': 'Ｗ', 'X': 'Ｘ', 'Y': 'Ｙ', 'Z': 'Ｚ',
    '0': '０', '1': '１', '2': '２', '3': '３', '4': '４', '5': '５', '6': '６', '7': '７', '8': '８', '9': '９',
    '-': '－', '&': '＆', '=': '＝', '/': '／', '$': '＄', '%': '％', '?': '？', ',': '，', ';': '；', 
    ':': '：', '"': '＂', "'": '＇', '!': '！', '@': '＠', '#': '＃', '.': '．', ' ': '－'
}

# Font Map for Mode 2
FONT_MAP = {
    'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ғ','g':'ɢ','h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ',
    'n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ','s':'s','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ',
    'A':'ᴀ','B':'ʙ','C':'ᴄ','D':'ᴅ','E':'ᴇ','F':'ғ','G':'ɢ','H':'ʜ','I':'ɪ','J':'ᴊ','K':'ᴋ','L':'ʟ','M':'ᴍ',
    'N':'ɴ','O':'ᴏ','P':'ᴘ','Q':'ǫ','R':'ʀ','S':'s','T':'ᴛ','U':'ᴜ','V':'ᴠ','W':'ᴡ','X':'x','Y':'ʏ','Z':'ᴢ'
}

# Borders Dictionary
BORDERS = {
    'short': [
        "┏━「  」\n┣ \n┗━╼",
        "┌──「  」──┐\n│ \n└────────┘",
        "╭──「  」──╮\n│ \n╰────────╯",
        "╔══「  」══╗\n║ \n╚════════╝",
        "┏━⊳ \n┣ \n┗━⊳",
        "╒══「  」══╕\n│ \n╘════════╛",
        "┏━•\n┣ •\n┗━•",
        "┌─[  ]\n├─ \n└─",
        "╭─[  ]\n├─ \n╰─",
        "╔═[  ]\n╠═ \n╚═",
        "┏━━『 』━━┓\n┣ ➾ \n┗━━━━━━━┛",
        "╭━〔 〕━╮\n┃ ➢ \n╰━━━━━━╯"
    ],
    'dashboard': [
        "┏━「 ᴅᴀsʜʙᴏᴀʀᴅ 」\n┣ 👤 ɴᴀᴍᴇ: \n┣ 🆔 ɪᴅ: \n┣ 🛡️ ʀᴏʟᴇ: \n┗━➾ 👨‍💻 ᴅᴇᴠ: Ｄｘ－Ｓｉｍｕ",
        "┏━━「 ᴅᴀsʜʙᴏᴀʀᴅ 」━━┓\n┃ ┏─「 ᴜsᴇʀ ᴘʀᴏғɪʟᴇ 」\n┃ ┃ 👤 ɴᴀᴍᴇ: \n┃ ┃ 🆔 ɪᴅ: \n┃ ┗───────────╼\n┃ ┏─「 ʙᴏᴛ ғᴇᴀᴛᴜʀᴇs 」\n┃ ┃ ✅ \n┃ ┃ ✅ \n┃ ┃ ✅ \n┃ ┃ ✅ \n┃ ┗───────────╼\n┃ ┏─「 ʜᴏᴡ ᴛᴏ ᴏᴘᴇʀᴀᴛᴇ 」\n┃ ┃ 1️⃣ \n┃ ┃ 2️⃣ \n┃ ┃ 3️⃣ \n┃ ┃ 4️⃣ \n┃ ┗───────────╼\n┃ ┏─「 sʏsᴛᴇᴍ ɪɴғᴏ 」\n┃ ┃ 👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: Ｄｘ－Ｓｉｍｕ\n┃ ┗───────────╼\n┗━━━━━━━━━━┛",
        "┏━━「 ᴅᴀsʜʙᴏᴀʀᴅ 」━━┓\n┃ ┏─「 ᴜsᴇʀ ᴘʀᴏғɪʟᴇ 」\n┃ ┃ 👤 ɴᴀᴍᴇ: \n┃ ┃ 🆔 ɪᴅ: \n┃ ┗───────────╼\n┃ \n┃ ┏─「 ʙᴏᴛ ғᴇᴀᴛᴜʀᴇs 」\n┃ ┃ 🗑 \n┃ ┃ 📌 \n┃ ┃ 🔊 \n┃ ┃ 🚀 \n┃ ┗───────────╼\n┗━━━━━━━━━━┛",
        "┏━━「 ✅ ᴄʟᴀɪᴍᴇᴅ 」━━┓\n┃ 👤 ᴜsᴇʀ: \n┃ 💰 ʀᴇᴡᴀʀᴅ: +1 ᴄᴏɪɴ\n┗━━━━━━━━━━━━━━┛",
        "┏━━「 sᴛᴀᴛs 」━━┓\n┃ 📊 sʏsᴛᴇᴍ sᴛᴀᴛɪsᴛɪᴄs\n┗───────────╼\n┃ 👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: \n┃ 🔗 ᴀᴄᴛɪᴠᴇ ʟɪɴks: \n┃ 🚫 ʙᴀɴɴᴇᴅ ᴜsᴇʀs: \n┗━━━━━━━━━━┛",
        "╭━━「 ɪɴғᴏ 」━━╮\n│ 👤 ᴜsᴇʀ: \n│ 🆔 ɪᴅ: \n╰━━━━━━━━━━╯",
        "╔══「 sʏsᴛᴇᴍ 」══╗\n╠ ᴄᴘᴜ: \n╠ ʀᴀᴍ: \n╚═══════════╝",
        "┏━[ ᴘʀᴏғɪʟᴇ ]━┓\n┣ ɴᴀᴍᴇ: \n┣ ᴀɢᴇ: \n┗━━━━━━━━━┛",
        "┌──< sᴇᴛᴛɪɴɢs >──┐\n│ ⚙️ ᴍᴏᴅᴇ: \n│ 🔔 ᴀʟᴇʀᴛs: \n└────────────┘",
        "╭─{ ᴀᴄᴄᴏᴜɴᴛ }─╮\n│ 💳 ʙᴀʟᴀɴᴄᴇ: \n│ 🪙 ᴄᴏɪɴs: \n╰───────────╯",
        "┏━━「 ᴘᴀɴᴇʟ 」━━┓\n┣ ⚙️ ᴄᴏɴғɪɢ\n┣ 🔧 ᴛᴏᴏʟs\n┗━━━━━━━━━━┛",
        "╔════『 ᴍᴇɴᴜ 』════╗\n║ ➣ ᴏᴘᴛɪᴏɴ 𝟷\n║ ➣ ᴏᴘᴛɪᴏɴ 𝟸\n╚══════════════╝",
        "╭━━━━〔 ɪɴᴅᴇx 〕━━━━╮\n┃ 📑 ᴘᴀɢᴇ: \n┃ 📌 sᴛᴀᴛᴜs: \n╰━━━━━━━━━━━━━━━╯"
    ]
}

# --- DATABASE HELPERS ---
def get_sudo_list():
    return list(sudo_db.find())

def is_owner(uid):
    return uid in OWNER_ID

def is_authorized(uid):
    return is_owner(uid) or sudo_db.find_one({"_id": uid}) is not None

def sync_user(user):
    """Updates user name in DB whenever they interact with the bot."""
    if is_authorized(user.id) and not is_owner(user.id):
        full_name = f"{user.first_name} {user.last_name or ''}".strip()
        sudo_db.update_one({"_id": user.id}, {"$set": {"name": full_name}}, upsert=True)

# --- COMMAND HANDLERS ---

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

# --- BORDER SYSTEM ---
@bot.message_handler(commands=['border'])
def border_handler(message):
    uid = message.from_user.id
    if uid not in SPECIAL_OWNERS: return
    
    args = message.text.split()
    category = "short"
    if len(args) > 1:
        cat_arg = args[1].lower()
        if cat_arg in ["dashboard", "list"]:
            category = "all" if cat_arg == "list" else "dashboard"

    send_border_page(message.chat.id, category, 0)

def send_border_page(chat_id, category, page_idx, message_id=None):
    if category == "all":
        items = BORDERS['short'] + BORDERS['dashboard']
    else:
        items = BORDERS.get(category, BORDERS['short'])
        
    if not items: return
    
    total = len(items)
    page_idx = page_idx % total
    
    border_text = f"<b>┏━「 ʙᴏʀᴅᴇʀ ({page_idx+1}/{total}) 」</b>\n<code>{items[page_idx]}</code>"
    
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

# --- STYLING ENGINE ---

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def process_style(message):
    uid = message.from_user.id
    if not is_authorized(uid): return
    sync_user(message.from_user)
    bot.send_chat_action(message.chat.id, 'typing')
    
    mode = USER_MODES.get(uid, 1)
    
    if uid in SPECIAL_OWNERS and mode == 2:
        # Mode 2 logic: Keep structure, convert using FONT_MAP
        styled_text = "".join([FONT_MAP.get(c, c) for c in message.text])
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📝 ᴄᴏᴘʏ", callback_data="copy_hint"))
        
        msg = f"<b>┏━「 sᴛʏʟᴇ ᴍᴏᴅᴇ 𝟸 」</b>\n┣ <code>{styled_text}</code>\n<b>┗━╼</b>"
        bot.send_message(message.chat.id, msg, reply_markup=markup)
        
    else:
        # Mode 1 logic (Original)
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

# --- CALLBACK HANDLERS ---
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
    print(">> NIKO is Online. System Secured by DX-CODEX.")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
