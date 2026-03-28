from telethon import TelegramClient, events
import os
import re

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")

SOURCE = os.environ.get("SOURCE")
DEST1 = os.environ.get("DEST1")
DEST2 = os.environ.get("DEST2")

client = TelegramClient("session", api_id, api_hash)


# 🎯 Caption Clean Function
def clean_caption(text):
    if not text:
        return None

    text = text.replace(".", " ")

    # SxxExxxx → Ep xxxx
    match = re.search(r"S\d+E(\d+)", text, re.IGNORECASE)
    if match:
        ep_num = match.group(1)
        text = re.sub(r"S\d+E\d+", f"Ep {ep_num}", text, flags=re.IGNORECASE)

    # Ensure "Ep xxxx" exists
    if "ep" not in text.lower():
        match2 = re.search(r"ep\s*(\d+)", text, re.IGNORECASE)
        if match2:
            text = f"Taarak Mehta Ka Ooltah Chashmah Ep {match2.group(1)}"
    
    return text.strip()


@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    msg = event.message

    try:
        if msg.file:
            filename = msg.file.name or ""

            # 🎯 Quality filter
            if not any(q in filename for q in ["240", "360", "540", "720", "1080"]):
                return

            caption = msg.text or filename
            caption_lower = caption.lower()

            # 🎯 Only TMKOC filter
            if "taarak" not in caption_lower:
                return

            new_caption = clean_caption(caption)

            # 🚀 Send to both channels
            await client.send_file(
                DEST1,
                msg.file,
                caption=new_caption
            )

            await client.send_file(
                DEST2,
                msg.file,
                caption=new_caption
            )

            print("✅ Forwarded:", new_caption)

    except Exception as e:
        print("❌ Error:", e)


client.start()
client.run_until_disconnected()