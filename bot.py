import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)


def get_group_file(chat_id):
    return os.path.join(DATA_FOLDER, f"{chat_id}.txt")


def parse_file(path):
    data = {}

    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

        try:
            json_data = json.loads(content)

            if isinstance(json_data, list):
                for item in json_data:
                    clean = str(item).replace('"', '').replace('[', '').replace(']', '')
                    parts = clean.split(":")
                    if len(parts) >= 2:
                        data[parts[0]] = clean

            elif isinstance(json_data, dict):
                for value in json_data.values():
                    clean = str(value).replace('"', '').replace('[', '').replace(']', '')
                    parts = clean.split(":")
                    if len(parts) >= 2:
                        data[parts[0]] = clean

        except:
            for line in content.splitlines():
                clean = line.replace('"', '').replace('[', '').replace(']', '')
                parts = clean.split(":")
                if len(parts) >= 2:
                    data[parts[0]] = clean

    return data


def compare(old_path, new_path):
    old = parse_file(old_path)
    new = parse_file(new_path)

    added, removed, updated = [], [], []

    for id_, full in new.items():
        if id_ not in old:
            name = full.split(":")[1]
            added.append((id_, name))

        elif old[id_] != full:
            old_name = old[id_].split(":")[1]
            new_name = full.split(":")[1]
            updated.append((id_, old_name, new_name))

    for id_, full in old.items():
        if id_ not in new:
            name = full.split(":")[1]
            removed.append((id_, name))

    text = "📊 FLAG CHANGELOG\n\n"

    text += f"🆕 Added ({len(added)}):\n"
    for id_, name in added[:50]:
        text += f"{id_} - {name}\n"

    text += f"\n❌ Removed ({len(removed)}):\n"
    for id_, name in removed[:50]:
        text += f"{id_} - {name}\n"

    text += f"\n🔄 Updated ({len(updated)}):\n"
    for id_, old_n, new_n in updated[:50]:
        text += f"{id_} - {old_n} ➜ {new_n}\n"

    if not added and not removed and not updated:
        text += "\nNo changes found."

    text += "\n\n✨ Updated by @Real_Aman"

    return text


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    new_file_path = os.path.join(DATA_FOLDER, f"{chat_id}_new.txt")
    last_file_path = get_group_file(chat_id)

    file = await update.message.document.get_file()
    await file.download_to_drive(new_file_path)

    if not os.path.exists(last_file_path):
        os.rename(new_file_path, last_file_path)
        await update.message.reply_text("✅ First file saved.\nNext file will generate changelog.")
        return

    result = compare(last_file_path, new_file_path)

    # split large message safely
    for i in range(0, len(result), 4000):
        await update.message.reply_text(result[i:i+4000])

    os.replace(new_file_path, last_file_path)


# 🔑 ENV TOKEN (Railway use karega)
TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

print("🤖 Bot running on Railway...")
app.run_polling(drop_pending_updates=True)
