import os
from pyrogram import Client, filters
from flask import Flask
from threading import Thread

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = 8357928315

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Alive!"

def run_server():
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

app = Client("stealth_broadcaster", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.new_chat_members)
async def welcome_and_save(client, message):
    for member in message.new_chat_members:
        if member.id == client.me.id:
            chat_id = message.chat.id
            with open("groups.txt", "a+") as f:
                f.seek(0)
                if str(chat_id) not in f.read():
                    f.write(f"{chat_id}\n")
            await client.send_message(ADMIN_ID, f"✅ Bot Added!\n\nName: {message.chat.title}\nID: `{chat_id}`")

@app.on_message(filters.command("bcast") & filters.user(ADMIN_ID))
async def broadcast_message(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a message with /bcast")
    
    success = 0
    failed = 0
    
    try:
        with open("groups.txt", "r") as f:
            groups = f.readlines()
    except FileNotFoundError:
        return await message.reply_text("❌ No groups found!")

    status_msg = await message.reply_text(f"🚀 Broadcasting to {len(groups)} groups...")

    for group_id in groups:
        try:
            chat_id = int(group_id.strip())
            await message.reply_to_message.copy(chat_id)
            success += 1
        except Exception:
            failed += 1
    
    await status_msg.edit_text(f"✅ Broadcast Complete!\n\n🎯 Success: `{success}`\n❌ Failed: `{failed}`")

if __name__ == "__main__":
    Thread(target=run_server).start()
    app.run()
