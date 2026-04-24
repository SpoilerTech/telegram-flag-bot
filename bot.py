import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")


# ✅ Markdown safe escape
def escape(text):
    return re.sub(r'([_\*\[\]()~`>#+\-=|{}.!])', r'\\\1', str(text))


# ✅ Flag parser
def parse_flags(text):
    lines = text.splitlines()

    added = []
    removed = []
    updated = []

    mode = None

    for line in lines:
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


# ✅ Message handler
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    added, removed, updated = parse_flags(text)

    result = ""

    # ✅ Added
    if added:
        result += "🆕 Added:\n"
        for fid, name in added:
            result += f"`{fid}` - `{name}`\n"

    # ❌ Removed
    if removed:
        result += "\n❌ Removed:\n"
        for fid, name in removed:
            result += f"`{fid}` - `{name}`\n"

    # 🔄 Updated
    if updated:
        result += "\n🔄 Updated:\n"
        for fid, name in updated:
            result += f"`{fid}` - `{name}`\n"

    # fallback
    if not result:
        result = "❌ No flags detected"

    # send safely (NO markdown error)
    for i in range(0, len(result), 4000):
        await update.message.reply_text(result[i:i+4000])


# ✅ Main run
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🤖 Bot running...")
    app.run_polling()
