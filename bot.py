from telethon import TelegramClient, events
import os
import re

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")

SOURCE = os.environ.get("SOURCE")
DEST1 = os.environ.get("DEST1")
DEST2 = os.environ.get("DEST2")

client = TelegramClient("session", api_id, api_hash)


# Caption Fix
def fix_caption(text):
    if not text:
        return text

    # TvShowHub  no change
    if "tvshowhub" in text.lower():
        return text

    # S47E4654  Ep 4654
    text = re.sub(r"S\d+E(\d+)", r"Ep \1", text, flags=re.IGNORECASE)

    return text


@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    msg = event.message

    try:
        if not msg.file:
            return

        filename = msg.file.name or ""
        caption = msg.text or filename or ""

        # Quality filter
        if not any(q in filename for q in ["240", "360", "540", "720", "1080"]):
            return

        # Only TMKOC filter
        if "taarak" not in caption.lower():
            return

        new_caption = fix_caption(caption)

        await client.send_file(DEST1, msg.file, caption=new_caption)
        await client.send_file(DEST2, msg.file, caption=new_caption)

        print("Forwarded:", new_caption)

    except Exception as e:
        print("Error:", e)


client.start()
client.run_until_disconnected()