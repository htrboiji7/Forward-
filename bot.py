import os
import pymongo
import asyncio
from pyrogram import Client, filters
from flask import Flask
from threading import Thread

# --- ENVIRONMENT VARIABLES ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URL = os.environ.get("MONGO_URL", "")

# 👇 DONO ADMINS KI ID YAHAN SET HAI
ADMIN_IDS = [8357928315, 1849178309]

# --- MONGODB SETUP ---
mongo_client = pymongo.MongoClient(MONGO_URL)
db = mongo_client["EliteDropBot"]
groups_col = db["saved_groups"]

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Alive and DB is Connected! Multi-Admin is Active."

def run_server():
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

app = Client("stealth_broadcaster", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 1. NEW GROUP ME ADD HONE PAR DB MEIN SAVE KAREGA
@app.on_message(filters.new_chat_members)
async def welcome_and_save(client, message):
    for member in message.new_chat_members:
        if member.id == client.me.id:
            chat_id = message.chat.id
            
            # MongoDB Insert (Agar pehle se nahi hai toh)
            if not groups_col.find_one({"chat_id": chat_id}):
                groups_col.insert_one({"chat_id": chat_id})
                
            # Notification sirf tere Main Account (8357928315) pe aayegi taaki spam na ho
            await client.send_message(ADMIN_IDS[0], f"✅ Bot Added & Saved to DB!\n\nName: {message.chat.title}\nID: `{chat_id}`")

# 2. EMERGENCY WAKEUP COMMAND (Dono admin use kar sakte hain)
@app.on_message(filters.command("wake") & filters.user(ADMIN_IDS))
async def wake_up(client, message):
    chat_id = message.chat.id
    if not groups_col.find_one({"chat_id": chat_id}):
        groups_col.insert_one({"chat_id": chat_id})
        msg = await message.reply_text("✅ ID permanently saved to MongoDB!")
    else:
        msg = await message.reply_text("⚠️ Already in Database.")
    
    # 3 second baad message delete taaki kisi group admin ko shak na ho
    await asyncio.sleep(3)
    await msg.delete()
    await message.delete()

# 3. THE BROADCASTER (Dono admin use kar sakte hain)
@app.on_message(filters.command("bcast") & filters.user(ADMIN_IDS))
async def broadcast_message(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a message with /bcast")
    
    # MongoDB Fetch
    groups = list(groups_col.find({}))
    
    if not groups:
        return await message.reply_text("❌ No groups found in Database! Pehle /wake command use karo.")

    status_msg = await message.reply_text(f"🚀 Broadcasting to {len(groups)} groups...")

    success = 0
    failed = 0

    for doc in groups:
        try:
            chat_id = doc["chat_id"]
            await message.reply_to_message.copy(chat_id)
            success += 1
        except Exception:
            failed += 1
    
    await status_msg.edit_text(f"✅ Broadcast Complete!\n\n🎯 Success: `{success}`\n❌ Failed: `{failed}`")

if __name__ == "__main__":
    Thread(target=run_server).start()
    app.run()
    
