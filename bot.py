import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")


# ✅ Escape safe (optional)
def escape(text):
    return re.sub(r'([_\*\[\]()~`>#+\-=|{}.!])', r'\\\1', str(text))


# ✅ Flag parser
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


# ✅ Common formatter
def format_output(added, removed, updated):
    result = ""

    if added:
        result += "🆕 Added:\n"
        for fid, name in added:
            result += f"`{fid}` - `{name.strip()}`\n"

    if removed:
        result += "\n❌ Removed:\n"
        for fid, name in removed:
            result += f"`{fid}` - `{name.strip()}`\n"

    if updated:
        result += "\n🔄 Updated:\n"
        for fid, name in updated:
            # split arrow ➜
            if "➜" in name:
                name = name.split("➜")[-1].strip()

            result += f"`{fid}` - `{name}`\n"

    if not result:
        result = "❌ No flags detected"

    return result


# ✅ TEXT handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    added, removed, updated = parse_flags(text)
    result = format_output(added, removed, updated)

    for i in range(0, len(result), 4000):
        await update.message.reply_text(result[i:i+4000])


# ✅ FILE handler (IMPORTANT)
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    content = await file.download_as_bytearray()

    text = content.decode("utf-8", errors="ignore")

    added, removed, updated = parse_flags(text)
    result = format_output(added, removed, updated)

    for i in range(0, len(result), 4000):
        await update.message.reply_text(result[i:i+4000])


# ✅ MAIN
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # TEXT + FILE BOTH
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("🤖 Bot running...")
    app.run_polling()
