import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# 🔥 temporary storage (user wise)
user_data_store = {}


# =========================
# FLAG PARSER
# =========================
def parse_flags(text):
    lines = text.splitlines()

    added, removed, updated = [], [], []
    mode = None

    for line in lines:
        line = line.strip()

        if "Added" in line:
            mode = "added"
            continue
        elif "Removed" in line:
            mode = "removed"
            continue
        elif "Updated" in line:
            mode = "updated"
            continue

        match = re.match(r"(\d+)\s*-\s*(.+)", line)
        if match:
            fid = match.group(1)
            name = match.group(2)

            if mode == "added":
                added.append((fid, name))
            elif mode == "removed":
                removed.append((fid, name))
            elif mode == "updated":
                updated.append((fid, name))

    return added, removed, updated


# =========================
# FORMATTER
# =========================
def format_output(version, added, removed, updated):
    result = f"Version {version}\n"

    if added:
        result += " ✅ Added:\n"
        for fid, name in added:
            result += f"• {name.strip()} ({fid})\n"

    if removed:
        result += "\n ❌ Removed:\n"
        for fid, name in removed:
            result += f"• {name.strip()} ({fid})\n"

    if updated:
        result += "\n ✏️ Updated:\n"
        for fid, name in updated:
            if "➜" in name:
                name = name.split("➜")[-1].strip()
            result += f"• {name} ({fid})\n"

    return result


# =========================
# FILE HANDLE
# =========================
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    content = await file.download_as_bytearray()

    text = content.decode("utf-8", errors="ignore")

    added, removed, updated = parse_flags(text)

    user_id = update.message.from_user.id

    # store data
    user_data_store[user_id] = (added, removed, updated)

    await update.message.reply_text("📌 Send version name (example: 427.0.0.0.71)")


# =========================
# TEXT HANDLE (version input)
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id not in user_data_store:
        await update.message.reply_text("❌ Pehle file bhej")
        return

    added, removed, updated = user_data_store[user_id]

    result = format_output(text, added, removed, updated)

    # clear data
    del user_data_store[user_id]

    # send
    for i in range(0, len(result), 4000):
        await update.message.reply_text(result[i:i+4000])


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Bot running...")
    app.run_polling()
