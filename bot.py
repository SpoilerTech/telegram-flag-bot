import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# simple start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Send your file")

# handle file
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    await file.download_to_drive("input.txt")

    await update.message.reply_text("📦 File received!\n\nNow send version name")

    context.user_data["waiting_version"] = True

# handle text
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_version"):
        version = update.message.text

        result = f"""
Version {version}

✅ Added:
• Example Added

❌ Removed:
• Example Removed

✏️ Updated:
• Example Updated
        """

        await update.message.reply_text(result)
        context.user_data["waiting_version"] = False

# main
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("Bot started...")
app.run_polling()
