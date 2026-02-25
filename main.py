import telebot
import re
import time

BOT_TOKEN = "8773837287:AAFZDqWyq1kac9tSAGehIDxSSDzLECU0fHg"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

OWNER_ID = [6703335929, 5136260272, 6757495567, 5838295041]

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

def is_owner(uid):
    return uid in OWNER_ID

def advanced_styler(text):
    clean_text = re.sub(r'[_.]', ' ', text).strip()
    words = re.split(r'[- ]+', clean_text)
    normalized = "-".join([w.capitalize() for w in words if w])
    
    styled = "".join([CHAR_MAP.get(c, c) for c in normalized])
    
    return f"「𖣂」{styled}ايڪـͬــͤــᷜــͨــͣــͪـي"

@bot.message_handler(commands=['start'])
def welcome_dashboard(message):
    if not is_owner(message.from_user.id): return
    
    bot.send_chat_action(message.chat.id, 'typing')
    msg = (
        f"<b>┏━━「 ᴅᴀsʜʙᴏᴀʀᴅ 」━━┓\n"
        f"┃ ┏─「 ᴜsᴇʀ ᴘʀᴏғɪʟᴇ 」\n"
        f"┃ ┃ 👤 ɴᴀᴍᴇ: .𖥔 ݁ ˖⋆ ˚❆ <b>{message.from_user.first_name}</b>\n"
        f"┃ ┃ 🆔 ɪᴅ: <code>{message.from_user.id}</code>\n"
        f"┃ ┗───────────╼\n"
        f"┃ ┏─「 ʙᴏᴛ ғᴇᴀᴛᴜʀᴇs 」\n"
        f"┃ ┃ ✅ ᴀɪ ᴘᴏᴡᴇʀᴇᴅ ꜱᴛʏʟɪɴɢ\n"
        f"┃ ┃ ✅ ᴅʏɴᴀᴍɪᴄ ꜱᴜᴅᴏ ʟɪꜱᴛ\n"
        f"┃ ┃ ✅ ꜱᴇᴄᴜʀᴇ ᴀᴄᴄᴇꜱꜱ\n"
        f"┃ ┗───────────╼\n"
        f"┃ ┏─「 ʜᴏᴡ ᴛᴏ ᴏᴘᴇʀᴀᴛᴇ 」\n"
        f"┃ ┃ 1️⃣ ꜱᴇɴᴅ ᴀɴʏ ɴᴀᴍᴇ (ᴇ.ɢ. ᴅᴀʀᴋ ɢᴀɴɢ)\n"
        f"┃ ┃ 2️⃣ ᴜꜱᴇ /sudo ᴛᴏ ᴍᴀɴᴀɢᴇ ᴏᴡɴᴇʀꜱ\n"
        f"┃ ┗───────────╼\n"
        f"┃ ┏─「 sʏsᴛᴇᴍ ɪɴғᴏ 」\n"
        f"┃ ┃ 👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: <b>DX-CODEX</b>\n"
        f"┃ ┗───────────╼\n"
        f"┗━━━━━━━━━━┛</b>"
    ).format(message=message)
    bot.reply_to(message, msg)

@bot.message_handler(commands=['sudo'])
def handle_sudo(message):
    if not is_owner(message.from_user.id): return
    
    bot.send_chat_action(message.chat.id, 'typing')
    args = message.text.split()
    
    if len(args) == 1:
        id_list = "\n".join([f"┃ ┃ ⚡ <code>{uid}</code>" for uid in OWNER_ID])
        msg = (
            f"<b>┏━━「 ꜱᴜᴅᴏ ʟɪꜱᴛ 」━━┓\n"
            f"┃ ┏─「 ᴀᴄᴛɪᴠᴇ ᴏᴡɴᴇʀꜱ 」\n"
            f"{id_list}\n"
            f"┃ ┗───────────╼\n"
            f"┗━━━━━━━━━━━━┛</b>"
        )
        return bot.reply_to(message, msg)

    new_id = args[1]
    if new_id.isdigit():
        new_id = int(new_id)
        if new_id not in OWNER_ID:
            OWNER_ID.append(new_id)
            bot.reply_to(message, f"✅ <b>ɪᴅ</b> <code>{new_id}</code> <b>ʜᴀꜱ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ꜱᴜᴅᴏ!</b>")
        else:
            bot.reply_to(message, "⚠️ <b>ᴛʜɪꜱ ɪᴅ ɪꜱ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴛʜᴇ ʟɪꜱᴛ.</b>")
    else:
        bot.reply_to(message, "❌ <b>ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍᴇʀɪᴄ ɪᴅ.</b>")

@bot.message_handler(commands=['rm'])
def handle_remove(message):
    if not is_owner(message.from_user.id): return
    
    bot.send_chat_action(message.chat.id, 'typing')
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        target_id = int(args[1])
        if target_id in OWNER_ID:
            OWNER_ID.remove(target_id)
            bot.reply_to(message, f"🗑️ <b>ɪᴅ</b> <code>{target_id}</code> <b>ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ.</b>")
        else:
            bot.reply_to(message, "⚠️ <b>ɪᴅ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ꜱᴜᴅᴏ ʟɪꜱᴛ.</b>")
    else:
        bot.reply_to(message, "❌ <b>ᴜꜱᴀɢᴇ:</b> <code>/rm [ɪᴅ]</code>")

@bot.message_handler(func=lambda message: True)
def process_style(message):
    if not is_owner(message.from_user.id): return
    
    bot.send_chat_action(message.chat.id, 'typing')
    styled_name = advanced_styler(message.text)
    
    response = (
        f"<b>┏━━━━「 ɢᴇɴᴇʀᴀᴛᴇᴅ 」━━━━┓\n"
        f"┃\n"
        f"┃ ✨</b> <code>{styled_name}</code>\n"
        f"<b>┃\n"
        f"┗━━━━━━━━━━━━━━━━┛</b>"
    )
    bot.reply_to(message, response)

if __name__ == "__main__":
    print(">> Bot is Online and Secured.")
    bot.infinity_polling()
