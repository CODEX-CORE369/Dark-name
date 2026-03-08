#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════╗
║          DX-SIMU AI TELEGRAM BOT                 ║
║          Developer  : DX-CODEX                   ║
║          AI Model   : niko 1.0                   ║
║          Host       : Render                     ║
╚══════════════════════════════════════════════════╝
"""

import os
import html
import re
import time
import asyncio
import threading
import requests
from flask import Flask
from pymongo import MongoClient
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode, ChatAction

# ═══════════════════════════════════════════════════
#                    CONFIGURATION
# ═══════════════════════════════════════════════════
BOT_TOKEN = "8116940440:AAEAuKJosg2T0cgWPuoZ744rwcGu1klJ8wA"
OWNER_IDS = [6703335929, 5136260272]
MONGO_URI = "mongodb+srv://dxsimu:mnbvcxzdx@dxsimu.0qrxmsr.mongodb.net/?appName=dxsimu"
API_KEY   = "057d42ba-2ab5-4afa-a35b-78446a8ed165"

AI_NAME  = "Dx-Simu"
AI_MODEL = "niko 1.0"
AI_DEV   = "DX-CODEX"
SAMBA_MODEL = "ALLaM-7B-Instruct-preview"

# ═══════════════════════════════════════════════════
#                    MONGODB SETUP
# ═══════════════════════════════════════════════════
mongo_client = MongoClient(MONGO_URI)
db           = mongo_client["CODE-AI"]        # database name
sudo_col     = db["sudo_users"]               # collection

# ═══════════════════════════════════════════════════
#                    AI CLIENT
# ═══════════════════════════════════════════════════
ai_client = OpenAI(
    api_key  = API_KEY,
    base_url = "https://api.sambanova.ai/v1",
)

# ═══════════════════════════════════════════════════
#                    FLASK KEEP-ALIVE SERVER
# ═══════════════════════════════════════════════════
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return f"<h2>🤖 {AI_NAME} — Online ✅</h2>", 200

@flask_app.route("/health")
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port, use_reloader=False)

def keep_alive():
    B = "INFO"
    port = int(os.environ.get("PORT", 8080))
    URL  = os.environ.get("RENDER_EXTERNAL_URL", f"http://localhost:{port}")
    while True:
        try:
            requests.get(URL, timeout=10)
            print(f"[{B}] Pinging server ({URL}) to stay awake...")
        except Exception as e:
            print(f"[{B}] Ping failed: {e}")
        time.sleep(300)

# ═══════════════════════════════════════════════════
#                    CONVERSATION STORE  (in-memory)
# ═══════════════════════════════════════════════════
chat_history: dict[int, list] = {}

SYSTEM_PROMPT = (
    f"You are {AI_NAME}, an advanced AI assistant developed by {AI_DEV}. "
    f"Your model version is {AI_MODEL}.\n\n"
    "Formatting rules (strictly follow):\n"
    "- Wrap ALL code in fenced code blocks with a language tag: ```python\\n...```\n"
    "- Use **bold** for headings, key terms, and important points.\n"
    "- Use > blockquote for notes, warnings, tips, or highlights.\n"
    "- Use `inline code` for filenames, variables, commands, paths.\n"
    "- Be friendly, helpful, concise but thorough."
)

# ═══════════════════════════════════════════════════
#                    DB HELPERS
# ═══════════════════════════════════════════════════
def get_sudo_ids() -> list[int]:
    return [d["user_id"] for d in sudo_col.find({}, {"user_id": 1, "_id": 0})]

def is_allowed(uid: int) -> bool:
    return uid in OWNER_IDS or uid in get_sudo_ids()

def sudo_add(uid: int) -> bool:
    if sudo_col.find_one({"user_id": uid}):
        return False
    sudo_col.insert_one({"user_id": uid})
    return True

def sudo_remove(uid: int) -> bool:
    result = sudo_col.delete_one({"user_id": uid})
    return result.deleted_count > 0

# ═══════════════════════════════════════════════════
#           MARKDOWN → TELEGRAM HTML FORMATTER
# ═══════════════════════════════════════════════════
def md_to_tg_html(text: str) -> str:
    """
    Convert AI markdown → Telegram-safe HTML.
    Preserves code blocks, applies bold / blockquote /
    inline-code / header conversions in plain text areas.
    """
    segments: list[tuple] = []
    last = 0

    # ── Step 1: extract fenced code blocks ──────────────
    fence_re = re.compile(r"```([a-zA-Z0-9_+\-.]*)\n?([\s\S]*?)```", re.DOTALL)
    for m in fence_re.finditer(text):
        segments.append(("text", text[last : m.start()]))
        segments.append(("code", m.group(1).strip(), m.group(2).strip()))
        last = m.end()
    segments.append(("text", text[last:]))

    out: list[str] = []

    for seg in segments:
        # ── Fenced code block ─────────────────────────────
        if seg[0] == "code":
            lang        = seg[1]
            escaped_code = html.escape(seg[2])
            if lang:
                out.append(
                    f'<b>📄 {html.escape(lang)}</b>\n'
                    f'<pre><code class="language-{html.escape(lang)}">'
                    f"{escaped_code}"
                    f"</code></pre>"
                )
            else:
                out.append(f"<pre><code>{escaped_code}</code></pre>")
            continue

        # ── Plain text: handle inline code first ─────────
        raw = seg[1]
        inline_segs: list[tuple] = []
        il_last = 0
        for m2 in re.finditer(r"`([^`\n]+)`", raw):
            inline_segs.append(("text",  raw[il_last : m2.start()]))
            inline_segs.append(("icode", m2.group(1)))
            il_last = m2.end()
        inline_segs.append(("text", raw[il_last:]))

        buf: list[str] = []
        for iseg in inline_segs:
            if iseg[0] == "icode":
                buf.append(f"<code>{html.escape(iseg[1])}</code>")
            else:
                s = html.escape(iseg[1])          # escape FIRST
                # **bold**
                s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s, flags=re.DOTALL)
                # ### heading → bold
                s = re.sub(r"(?m)^#{1,3}\s+(.+)$", r"<b>\1</b>", s)
                # > blockquote  (html-escaped '>' becomes '&gt;')
                lines    = s.split("\n")
                new_lines = []
                for line in lines:
                    if line.startswith("&gt; "):
                        new_lines.append(f"<blockquote>{line[5:]}</blockquote>")
                    elif line.rstrip() == "&gt;":
                        new_lines.append("<blockquote> </blockquote>")
                    else:
                        new_lines.append(line)
                s = "\n".join(new_lines)
                buf.append(s)

        out.append("".join(buf))

    return "".join(out)

# ═══════════════════════════════════════════════════
#                    ANIMATION FRAMES
# ═══════════════════════════════════════════════════
FRAMES = [
    "⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  <b>0%</b>",
    "🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛  <b>10%</b>",
    "🟦🟦⬛⬛⬛⬛⬛⬛⬛⬛  <b>20%</b>",
    "🟦🟦🟦⬛⬛⬛⬛⬛⬛⬛  <b>30%</b>",
    "🟦🟦🟦🟦⬛⬛⬛⬛⬛⬛  <b>40%</b>",
    "🟦🟦🟦🟦🟦⬛⬛⬛⬛⬛  <b>50%</b>",
    "🟦🟦🟦🟦🟦🟦⬛⬛⬛⬛  <b>60%</b>",
    "🟦🟦🟦🟦🟦🟦🟦⬛⬛⬛  <b>70%</b>",
    "🟦🟦🟦🟦🟦🟦🟦🟦⬛⬛  <b>80%</b>",
    "🟦🟦🟦🟦🟦🟦🟦🟦🟦⬛  <b>90%</b>",
    "🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦  ✅ <b>Done!</b>",
]

# ═══════════════════════════════════════════════════
#                    AI CALL
# ═══════════════════════════════════════════════════
async def ask_ai(uid: int, user_msg: str) -> str:
    if uid not in chat_history:
        chat_history[uid] = []

    chat_history[uid].append({"role": "user", "content": user_msg})

    # Keep last 20 turns to avoid token overflow
    if len(chat_history[uid]) > 20:
        chat_history[uid] = chat_history[uid][-20:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history[uid]

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: ai_client.chat.completions.create(
            model       = SAMBA_MODEL,
            messages    = messages,
            temperature = 0.7,
            top_p       = 0.9,
            max_tokens  = 2048,
        ),
    )

    reply = response.choices[0].message.content
    chat_history[uid].append({"role": "assistant", "content": reply})
    return reply

# ═══════════════════════════════════════════════════
#                    SPLIT LONG HTML MESSAGES
# ═══════════════════════════════════════════════════
def split_html(text: str, limit: int = 4000) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > limit:
            if current:
                chunks.append(current)
            current = line
        else:
            current += ("\n" if current else "") + line
    if current:
        chunks.append(current)
    return chunks if chunks else [text[:limit]]

# ═══════════════════════════════════════════════════
#                    /start
# ═══════════════════════════════════════════════════
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        return
    name = html.escape(update.effective_user.first_name or "ᴜsᴇʀ")
    text = (
        f"<b>🤖  {AI_NAME}  —  ᴀɪ  ᴀssɪsᴛᴀɴᴛ</b>\n"
        f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
        f"<blockquote>"
        f"🧠  ᴍᴏᴅᴇʟ      :  <b>{AI_MODEL}</b>\n"
        f"👨‍💻  ᴅᴇᴠᴇʟᴏᴘᴇʀ  :  <b>{AI_DEV}</b>"
        f"</blockquote>\n\n"
        f"ʜᴇʟʟᴏ,  <b>{name}</b>! 👋\n"
        f"ɪ ᴀᴍ <b>{AI_NAME}</b>.  sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴛᴏ sᴛᴀʀᴛ ᴄʜᴀᴛᴛɪɴɢ!\n\n"
        f"<b>📌  ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        f"<code>/start</code>      —  ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ\n"
        f"<code>/clear</code>      —  ᴄʟᴇᴀʀ ᴄʜᴀᴛ ʜɪsᴛᴏʀʏ\n"
        f"<code>/sudo [id]</code>  —  ᴀᴅᴅ / ʟɪsᴛ sᴜᴅᴏ ᴜsᴇʀ\n"
        f"<code>/rm [id]</code>    —  ʀᴇᴍᴏᴠᴇ sᴜᴅᴏ ᴜsᴇʀ\n\n"
        f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        f"sᴇɴᴛ  ʙʏ  <b>{AI_NAME}</b> 🚀"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

# ═══════════════════════════════════════════════════
#                    /clear
# ═══════════════════════════════════════════════════
async def cmd_clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        return
    chat_history.pop(uid, None)
    await update.message.reply_text(
        f"<b>🗑️  ᴄʜᴀᴛ  ʜɪsᴛᴏʀʏ  ᴄʟᴇᴀʀᴇᴅ!</b>\n\n"
        f"sᴛᴀʀᴛ  ᴀ  ꜰʀᴇsʜ  ᴄᴏɴᴠᴇʀsᴀᴛɪᴏɴ  ᴀɴʏᴛɪᴍᴇ. ✨\n\n"
        f"sᴇɴᴛ  ʙʏ  <b>{AI_NAME}</b>",
        parse_mode=ParseMode.HTML,
    )

# ═══════════════════════════════════════════════════
#                    /sudo
# ═══════════════════════════════════════════════════
async def cmd_sudo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in OWNER_IDS:
        await update.message.reply_text(
            "<b>⛔  ᴀᴄᴄᴇss  ᴅᴇɴɪᴇᴅ</b>\n"
            "ᴏɴʟʏ  ᴏᴡɴᴇʀs  ᴄᴀɴ  ᴜsᴇ  ᴛʜɪs  ᴄᴏᴍᴍᴀɴᴅ.",
            parse_mode=ParseMode.HTML,
        )
        return

    args = ctx.args

    # ── No args → list sudo users ─────────────────────
    if not args:
        ids = get_sudo_ids()
        if not ids:
            body = "<i>ɴᴏ  sᴜᴅᴏ  ᴜsᴇʀs  ʏᴇᴛ.</i>"
        else:
            body = "\n".join(f"• <code>{i}</code>" for i in ids)
        await update.message.reply_text(
            f"<b>📋  sᴜᴅᴏ  ᴜsᴇʀ  ʟɪsᴛ</b>\n\n"
            f"<blockquote>{body}</blockquote>\n\n"
            f"ᴛᴏᴛᴀʟ:  <b>{len(ids)}</b>  ᴜsᴇʀ(s)\n\n"
            f"sᴇɴᴛ  ʙʏ  <b>{AI_NAME}</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    # ── Args → add sudo user ──────────────────────────
    try:
        tid = int(args[0])
    except ValueError:
        await update.message.reply_text(
            "<b>❌  ɪɴᴠᴀʟɪᴅ  ɪᴅ!</b>\n"
            "ᴜsᴀɢᴇ:  <code>/sudo [user_id]</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    if tid in OWNER_IDS:
        await update.message.reply_text(
            "<b>ℹ️</b>  ᴛʜᴀᴛ  ᴜsᴇʀ  ɪs  ᴀʟʀᴇᴀᴅʏ  ᴀɴ  ᴏᴡɴᴇʀ!",
            parse_mode=ParseMode.HTML,
        )
        return

    if sudo_add(tid):
        await update.message.reply_text(
            f"<b>✅  sᴜᴅᴏ  ɢʀᴀɴᴛᴇᴅ!</b>\n\n"
            f"ᴜsᴇʀ  <code>{tid}</code>  ᴄᴀɴ  ɴᴏᴡ  ᴜsᴇ  ᴛʜᴇ  ʙᴏᴛ.\n\n"
            f"sᴇɴᴛ  ʙʏ  <b>{AI_NAME}</b>",
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.message.reply_text(
            f"<b>ℹ️</b>  <code>{tid}</code>  ɪs  ᴀʟʀᴇᴀᴅʏ  ᴀ  sᴜᴅᴏ  ᴜsᴇʀ!",
            parse_mode=ParseMode.HTML,
        )

# ═══════════════════════════════════════════════════
#                    /rm
# ═══════════════════════════════════════════════════
async def cmd_rm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in OWNER_IDS:
        await update.message.reply_text(
            "<b>⛔  ᴀᴄᴄᴇss  ᴅᴇɴɪᴇᴅ</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    args = ctx.args
    if not args:
        await update.message.reply_text(
            "<b>❌  ᴜsᴀɢᴇ:</b>  <code>/rm [user_id]</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        tid = int(args[0])
    except ValueError:
        await update.message.reply_text(
            "<b>❌  ɪɴᴠᴀʟɪᴅ  ɪᴅ!</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    if sudo_remove(tid):
        await update.message.reply_text(
            f"<b>🗑️  sᴜᴅᴏ  ʀᴇᴍᴏᴠᴇᴅ!</b>\n\n"
            f"ᴜsᴇʀ  <code>{tid}</code>  ʜᴀs  ʙᴇᴇɴ  ʀᴇᴍᴏᴠᴇᴅ  ꜰʀᴏᴍ  ᴛʜᴇ  ʟɪsᴛ.\n\n"
            f"sᴇɴᴛ  ʙʏ  <b>{AI_NAME}</b>",
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.message.reply_text(
            f"<b>❌</b>  <code>{tid}</code>  ɪs  ɴᴏᴛ  ɪɴ  ᴛʜᴇ  sᴜᴅᴏ  ʟɪsᴛ!",
            parse_mode=ParseMode.HTML,
        )

# ═══════════════════════════════════════════════════
#                    MESSAGE HANDLER
# ═══════════════════════════════════════════════════
async def handle_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid       = update.effective_user.id
    user_text = (update.message.text or "").strip()

    if not is_allowed(uid) or not user_text:
        return

    # Send typing indicator
    await ctx.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)

    # ── Initial loading message ───────────────────────
    loading_msg = await update.message.reply_text(
        f"<b>🤖  {AI_NAME}</b>  ɪs  ᴛʜɪɴᴋɪɴɢ...\n\n{FRAMES[0]}",
        parse_mode=ParseMode.HTML,
    )

    # ── Animate progress bar while waiting for AI ─────
    stop_event = asyncio.Event()

    async def animate():
        for frame in FRAMES[1:]:
            if stop_event.is_set():
                break
            await asyncio.sleep(0.5)
            try:
                await loading_msg.edit_text(
                    f"<b>🤖  {AI_NAME}</b>  ɪs  ᴘʀᴏᴄᴇssɪɴɢ...\n\n{frame}",
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                pass  # ignore Telegram rate-limit / no-change errors

    anim_task = asyncio.create_task(animate())

    # ── Call AI ───────────────────────────────────────
    try:
        raw_reply = await ask_ai(uid, user_text)
    except Exception as e:
        stop_event.set()
        anim_task.cancel()
        await loading_msg.edit_text(
            f"<b>❌  ᴇʀʀᴏʀ  ᴏᴄᴄᴜʀʀᴇᴅ</b>\n\n"
            f"<blockquote>{html.escape(str(e))}</blockquote>\n\n"
            f"sᴇɴᴛ  ʙʏ  <b>{AI_NAME}</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    stop_event.set()
    anim_task.cancel()

    # ── Show completion flash ─────────────────────────
    try:
        await loading_msg.edit_text(
            f"<b>🤖  {AI_NAME}</b>  ᴄᴏᴍᴘʟᴇᴛᴇᴅ!\n\n{FRAMES[-1]}",
            parse_mode=ParseMode.HTML,
        )
        await asyncio.sleep(0.35)
    except Exception:
        pass

    # ── Build formatted response ──────────────────────
    formatted = md_to_tg_html(raw_reply)
    header = (
        f"<b>🤖  {AI_NAME}</b>\n"
        f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
    )
    footer = (
        f"\n\n<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        f"sᴇɴᴛ  ʙʏ  <b>{AI_NAME}</b>  •  <i>{AI_MODEL}</i>"
    )
    full_text = header + formatted + footer

    # ── Send (handle 4096-char Telegram limit) ────────
    chunks = split_html(full_text)
    if len(chunks) == 1:
        try:
            await loading_msg.edit_text(chunks[0], parse_mode=ParseMode.HTML)
        except Exception:
            await update.message.reply_text(chunks[0], parse_mode=ParseMode.HTML)
    else:
        try:
            await loading_msg.delete()
        except Exception:
            pass
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode=ParseMode.HTML)

# ═══════════════════════════════════════════════════
#                    MAIN ENTRY POINT
# ═══════════════════════════════════════════════════
def main():
    # Start Flask server in background (required for Render port binding)
    threading.Thread(target=run_flask, daemon=True).start()
    print("[INFO] Flask server started.")

    # Start keep-alive pinger in background
    threading.Thread(target=keep_alive, daemon=True).start()
    print("[INFO] Keep-alive thread started.")

    # Build and run Telegram bot
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("clear", cmd_clear))
    application.add_handler(CommandHandler("sudo",  cmd_sudo))
    application.add_handler(CommandHandler("rm",    cmd_rm))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg)
    )

    print(f"[INFO] {AI_NAME} bot is running... 🚀")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
