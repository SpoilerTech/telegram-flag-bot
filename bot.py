import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ BOT_TOKEN missing!")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Send your file")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_version"] = True
    await update.message.reply_text("📦 File received!\n\nअब version name भेज")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_version"):
        version = update.message.text

        msg = f"""🔥 Version {version}

✅ Added:
• Example Added

❌ Removed:
• Example Removed

✏️ Updated:
• Example Updated
"""
        await update.message.reply_text(msg)
        context.user_data["waiting_version"] = False

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
