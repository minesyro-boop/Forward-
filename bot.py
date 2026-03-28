from telethon import TelegramClient, events
import os
import re
import asyncio

# 1. API details ko fallback values ke sath load karna
api_id = int(os.environ.get("API_ID", 0))
api_hash = os.environ.get("API_HASH", "")

# 2. Private Channel IDs (-100...) ko Integer mein convert karne ka function
def get_id(id_str):
    if not id_str: return None
    if id_str.startswith("-100") or id_str.isdigit():
        return int(id_str)
    return id_str

SOURCE = get_id(os.environ.get("SOURCE"))
DEST1 = get_id(os.environ.get("DEST1"))
DEST2 = get_id(os.environ.get("DEST2"))

client = TelegramClient("session", api_id, api_hash)

def fix_caption(text):
    if not text:
        return ""
    if "tvshowhub" in text.lower():
        return text
    # S47E4654 -> Ep 4654
    text = re.sub(r"S\d+E(\d+)", r"Ep \1", text, flags=re.IGNORECASE)
    return text

@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    msg = event.message
    try:
        # 3. msg.file ki jagah msg.media check karna (Zyada reliable hai)
        if not msg.media:
            return

        filename = ""
        if msg.file and msg.file.name:
            filename = msg.file.name.lower()
            
        caption = (msg.text or filename or "").lower()

        # Quality filter
        qualities = ["240", "360", "540", "720", "1080"]
        if not any(q in filename for q in qualities) and not any(q in caption for q in qualities):
            return

        # TMKOC filter
        if "taarak" not in caption and "taarak" not in filename:
            return

        new_caption = fix_caption(msg.text or filename)

        # 4. msg.file ki jagah msg.media send karna (Direct Forwarding bina download kiye)
        if DEST1:
            await client.send_file(DEST1, msg.media, caption=new_caption)
        if DEST2:
            await client.send_file(DEST2, msg.media, caption=new_caption)

        print(f"Forwarded: {new_caption}")

    except Exception as e:
        print(f"Error: {e}")

# 5. Entity Error Fix: Client start hone ke baad dialogs load karna
async def main():
    print("Bot login ho raha hai...")
    await client.start()
    
    print("Saare chats scan ho rahe hain (Entity fix ke liye)...")
    await client.get_dialogs() 
    
    print("Bot active hai. Messages ka wait kar raha hoon...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
