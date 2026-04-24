import os
import json
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

------------------ ESCAPE ------------------

def escape(text):
return re.sub(r'([_*()~`>#+-=|{}.!])', r'\\1', str(text))

------------------ FILE PATH ------------------

def get_group_file(chat_id):
return os.path.join(DATA_FOLDER, f"{chat_id}.json")

------------------ PARSE JSON ------------------

def parse_file(path):
with open(path, "r", encoding="utf-8") as f:
content = f.read().strip()

data = json.loads(content)

result = {}
for k, v in data.items():
    try:
        result[str(k)] = str(v)
    except:
        continue

return result

------------------ COMPARE ------------------

def compare(old, new):
added = []
removed = []
updated = []

for k in new:
    if k not in old:
        added.append({"id": k, "name": new[k]})
    elif old[k] != new[k]:
        updated.append({"id": k, "old": old[k], "name": new[k]})

for k in old:
    if k not in new:
        removed.append({"id": k, "name": old[k]})

return added, removed, updated

------------------ FORMAT ------------------

def format_flags(title, data):
if not data:
return f"{title} (0)\n\n"

text = f"{title} ({len(data)}):\n"
for item in data:
    text += f"`{escape(item['id'])}` - `{escape(item['name'])}`\n"
return text + "\n"

def format_updated(data):
if not data:
return "🔄 Updated (0)\n\n"

text = f"🔄 Updated ({len(data)}):\n"
for item in data:
    if item["old"] != item["name"]:
        text += f"`{escape(item['id'])}` - `{escape(item['old'])}` ➜ `{escape(item['name'])}`\n"
return text + "\n"

------------------ HANDLER ------------------

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not update.message.document:
return

file = await update.message.document.get_file()
chat_id = update.effective_chat.id
path = get_group_file(chat_id)

temp_path = path + "_new"

await file.download_to_drive(temp_path)

# first file save
if not os.path.exists(path):
    os.rename(temp_path, path)
    await update.message.reply_text("✅ First file saved.\nSend next file to compare.")
    return

try:
    old = parse_file(path)
    new = parse_file(temp_path)

    added, removed, updated = compare(old, new)

    result = "📊 FLAG CHANGELOG\n\n"
    result += format_flags("🆕 Added", added)
    result += format_flags("❌ Removed", removed)
    result += format_updated(updated)
    result += "✨ Updated by @Real_Aman"

    # split message (Telegram limit)
    for i in range(0, len(result), 4000):
        await update.message.reply_text(
            result[i:i+4000],
            parse_mode="MarkdownV2"
        )

    # replace old file
    os.remove(path)
    os.rename(temp_path, path)

except Exception as e:
    await update.message.reply_text(f"❌ Error: {e}")

------------------ MAIN ------------------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

print("🤖 Bot running on Railway...")

app.run_polling()
