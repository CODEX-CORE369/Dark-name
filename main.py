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

# Character Map for Styling
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
    if not is_authorized(message.from_user.id): return
    
    role = "👑 ᴏᴡɴᴇʀ" if is_owner(message.from_user.id) else "⚡ ꜱᴜᴅᴏ"
    msg = (
        f"<b>┏━「 ᴅᴀsʜʙᴏᴀʀᴅ 」\n"
        f"┣ 👤 ɴᴀᴍᴇ: {message.from_user.first_name}\n"
        f"┣ 🆔 ɪᴅ: <code>{message.from_user.id}</code>\n"
        f"┣ 🛡️ ʀᴏʟᴇ: {role}\n"
        f"┗━➾ 👨‍💻 ᴅᴇᴠ: DX-CODEX</b>"
    )
    bot.reply_to(message, msg)

@bot.message_handler(commands=['sudo'])
def handle_sudo(message):
    uid = message.from_user.id
    if not is_authorized(uid): return
    
    args = message.text.split()
    
    # Show Sudo List
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

    # Add Sudo (Only Owner)
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

# --- STYLING ENGINE ---

@bot.message_handler(func=lambda message: True)
def process_style(message):
    if not is_authorized(message.from_user.id): return
    sync_user(message.from_user)
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Text Normalization
    clean_text = re.sub(r'[_.]', ' ', message.text).strip()
    words = re.split(r'[- ]+', clean_text)
    normalized = "-".join([w.capitalize() for w in words if w])
    styled_base = "".join([CHAR_MAP.get(c, c) for c in normalized])
    
    # Styles
    style1 = f"「𖣂」{styled_base}ايڪـͬــͤــᷜــͨــͣــͪـي"
    style2 = styled_base
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📝 ᴄᴏᴘʏ", callback_data="copy_hint"))
    
    # Sending Messages
    msg1 = f"<b>┏━「 sᴛʏʟᴇ 𝟷 」</b>\n┣ <code>{style1}</code>\n<b>┗━╼</b>"
    bot.send_message(message.chat.id, msg1, reply_markup=markup)
    
    msg2 = f"<b>┏━「 sᴛʏʟᴇ 𝟸 」</b>\n┣ <code>{style2}</code>\n<b>┗━╼</b>"
    bot.send_message(message.chat.id, msg2, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "copy_hint")
def copy_callback(call):
    bot.answer_callback_query(call.id, "👆 ᴛᴇxᴛ-ᴇ ᴄʟɪᴄᴋ ᴋᴏʀᴜɴ ᴄᴏᴘʏ ʜᴏʏᴇ ᴊᴀʙᴇ!", show_alert=True)

if __name__ == "__main__":
    print(">> NIKO is Online. System Secured by DX-CODEX.")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
