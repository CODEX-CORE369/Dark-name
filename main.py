import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
from pymongo import MongoClient

BOT_TOKEN = "8773837287:AAFZDqWyq1kac9tSAGehIDxSSDzLECU0fHg"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# MongoDB Setup
MONGO_URI = "mongodb+srv://dxsimu:mnbvcxzdx@dxsimu.0qrxmsr.mongodb.net/?appName=dxsimu"
client = MongoClient(MONGO_URI)
db = client["DARK-NAMEX"]
sudo_db = db["sudo_users"]

OWNER_ID = [6703335929, 5136260272, 6737589257, 7819700191]

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

# Database Helpers
def get_sudo_list():
    return [user["_id"] for user in sudo_db.find()]

def is_owner(uid):
    return uid in OWNER_ID

def is_authorized(uid):
    return is_owner(uid) or uid in get_sudo_list()

@bot.message_handler(commands=['start'])
def welcome_dashboard(message):
    if not is_authorized(message.from_user.id): return
    bot.send_chat_action(message.chat.id, 'typing')
    
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
            return bot.reply_to(message, "<b>┏━「 ꜱᴜᴅᴏ ʟɪꜱᴛ 」\n┗ ➾ 🚫 ɴᴏ ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ ꜰᴏᴜɴᴅ.</b>")
        
        id_list = ""
        for s_id in sudo_users:
            try:
                user_info = bot.get_chat(s_id)
                name = user_info.first_name
                if user_info.last_name:
                    name += f" {user_info.last_name}"
                mention = f"<a href='tg://user?id={s_id}'>{name}</a>"
            except:
                mention = f"<a href='tg://user?id={s_id}'>ᴜɴᴋɴᴏᴡɴ ᴜꜱᴇʀ</a>"
                
            id_list += f"┣ 🆔 <code>{s_id}</code>\n┃ ┗ 👤 {mention}\n"
            
        msg = f"<b>┏━「 ꜱᴜᴅᴏ ʟɪꜱᴛ 」\n{id_list}┗━➾ ᴛᴏᴛᴀʟ: {len(sudo_users)}</b>"
        return bot.reply_to(message, msg, disable_web_page_preview=True)

    # Add Sudo (Only Owner)
    if is_owner(uid):
        new_id = args[1]
        if new_id.isdigit():
            new_id = int(new_id)
            if new_id in OWNER_ID:
                bot.reply_to(message, "⚠️ <b>ᴛʜɪꜱ ɪᴅ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴏᴡɴᴇʀ.</b>")
            elif new_id in get_sudo_list():
                bot.reply_to(message, "⚠️ <b>ᴛʜɪꜱ ɪᴅ ɪꜱ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴛʜᴇ ꜱᴜᴅᴏ ʟɪꜱᴛ.</b>")
            else:
                sudo_db.insert_one({"_id": new_id})
                bot.reply_to(message, f"<b>┏━「 ꜱᴜᴅᴏ ᴀᴅᴅᴇᴅ 」\n┗ ➾ ✅ ɪᴅ: <code>{new_id}</code></b>")
        else:
            bot.reply_to(message, "❌ <b>ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍᴇʀɪᴄ ɪᴅ.</b>")
    else:
        bot.reply_to(message, "🚫 <b>ᴏɴʟʏ ᴏᴡɴᴇʀꜱ ᴄᴀɴ ᴀᴅᴅ ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ.</b>")

@bot.message_handler(commands=['rm'])
def handle_remove(message):
    uid = message.from_user.id
    if not is_owner(uid): 
        if is_authorized(uid):
            bot.reply_to(message, "🚫 <b>ᴏɴʟʏ ᴏᴡɴᴇʀꜱ ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ.</b>")
        return
        
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        target_id = int(args[1])
        if sudo_db.find_one({"_id": target_id}):
            sudo_db.delete_one({"_id": target_id})
            bot.reply_to(message, f"<b>┏━「 ꜱᴜᴅᴏ ʀᴇᴍᴏᴠᴇᴅ 」\n┗ ➾ 🗑️ ɪᴅ: <code>{target_id}</code></b>")
        else:
            bot.reply_to(message, "⚠️ <b>ɪᴅ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ꜱᴜᴅᴏ ʟɪꜱᴛ.</b>")
    else:
        bot.reply_to(message, "❌ <b>ᴜꜱᴀɢᴇ:</b> <code>/rm [ɪᴅ]</code>")

@bot.message_handler(func=lambda message: True)
def process_style(message):
    if not is_authorized(message.from_user.id): return
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Core Styling Logic
    clean_text = re.sub(r'[_.]', ' ', message.text).strip()
    words = re.split(r'[- ]+', clean_text)
    normalized = "-".join([w.capitalize() for w in words if w])
    
    styled_base = "".join([CHAR_MAP.get(c, c) for c in normalized])
    
    style1 = f"「𖣂」{styled_base}ايڪـͬــͤــᷜــͨــͣــͪـي"
    style2 = styled_base
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📝 ᴄᴏᴘʏ", callback_data="copy_alert"))
    
    # Style 1 Message (With Symbols)
    msg1 = (
        f"<b>┏━「 sᴛʏʟᴇ 𝟷 」</b>\n"
        f"┣ <code>{style1}</code>\n"
        f"<b>┗━━━━━━━━━</b>"
    )
    bot.send_message(message.chat.id, msg1, reply_markup=markup)
    
    # Style 2 Message (Normal Font)
    msg2 = (
        f"<b>┏━「 sᴛʏʟᴇ 𝟸 」</b>\n"
        f"┣ <code>{style2}</code>\n"
        f"<b>┗━━━━━━━━━</b>"
    )
    bot.send_message(message.chat.id, msg2, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "copy_alert")
def copy_callback(call):
    bot.answer_callback_query(call.id, "👆 Text er upore click korun copy korar jonne!", show_alert=True)

if __name__ == "__main__":
    print(">> NIKO is Online. System Secured by DX-CODEX.")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
