from pyrogram import Client, filters
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("thumb_caption_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    user = message.from_user.id
    user_data.setdefault(user, {"thumb": None, "caption": None})

    await message.reply_text("Send your thumbnail (photo), then send a video/file/document.")

# Thumbnail Commands
@app.on_message(filters.command("view_thumb"))
async def view_thumb_cmd(client, message):
    user = message.from_user.id
    if user_data.get(user, {}).get("thumb"):
        return await message.reply_photo(user_data[user]["thumb"], caption="Current Thumbnail")
    await message.reply_text("No thumbnail set yet!")

@app.on_message(filters.command("del_thumb"))
async def del_thumb_cmd(client, message):
    user = message.from_user.id
    if user_data.get(user, {}).get("thumb"):
        user_data[user]["thumb"] = None
        return await message.reply_text("Thumbnail deleted! Send new one.")
    await message.reply_text("No thumbnail set yet!")

@app.on_message(filters.photo)
async def thumb_handler(client, message):
    user = message.from_user.id
    user_data.setdefault(user, {"thumb": None, "caption": None})
    user_data[user]["thumb"] = message.photo.file_id
    await message.reply_text("Thumbnail Saved! Now send a file/video.")

@app.on_message(filters.video | filters.document | filters.audio)
async def file_handler(client, message):
    user = message.from_user.id
    if not user_data.get(user, {}).get("thumb"):
        return await message.reply_text("Please send a thumbnail first!")

    await message.reply_text("Send new caption or /skip to keep original caption.")
    user_data[user]["pending_file"] = message.id

@app.on_message(filters.command("skip"))
async def skip(client, message):
    await process(client, message, True)

@app.on_message(filters.text & ~filters.command(["start", "skip", "view_thumb", "del_thumb"]))
async def caption_handler(client, message):
    user = message.from_user.id
    if user in user_data and "pending_file" in user_data[user]:
        user_data[user]["caption"] = message.text
        await process(client, message)

async def process(client, message, skip=False):
    user = message.from_user.id
    data = user_data[user]
    msg_id = data.pop("pending_file")
    original = await client.get_messages(user, msg_id)
    caption = original.caption if skip else data["caption"]

    if original.video and "thumb" in data:
    await client.send_video(
        chat_id=user,
        video=original.video.file_id,
        caption=caption,
        thumb=data["thumb"]
    )
else:
    await original.copy(chat_id=user, caption=caption)
    await message.reply_text("Done! Instant updated file is here🔥")

print("Bot Started")
app.run()
