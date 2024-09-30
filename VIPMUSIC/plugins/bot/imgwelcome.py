import os
import time
from datetime import datetime
from PIL import ImageDraw, Image, ImageChops
from pyrogram import *
from pyrogram.types import *
from logging import getLogger
from VIPMUSIC import app
from VIPMUSIC.mongo.imgwelcomedb import add_wlcm, rm_wlcm, wlcm

LOG_CHANNEL_ID = (-1002009280180)

LOGGER = getLogger(__name__)

class temp:
    ME = None
    CURRENT = 2
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    WELCOME_ENABLED = {}  # Dictionary to keep track of special welcome status

def circle(pfp, size=(259, 259)):
    pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp

def welcomepic(pic, user, chat, id, uname):
    background = Image.open("assets/hasnainkk.png")
    pfp = Image.open(pic).convert("RGBA")
    pfp = circle(pfp)
    pfp = pfp.resize((259, 259))
    pfp_x = 55
    pfp_y = (background.size[1] - pfp.size[1]) // 2 + 38
    draw = ImageDraw.Draw(background)
    pfp_position = (770, 140)
    background.paste(pfp, (pfp_x, pfp_y), pfp)
    background.save(f"downloads/welcome#{id}.png")
    return f"downloads/welcome#{id}.png"

@app.on_chat_member_updated(filters.group, group=-3)
async def greet_group(_, member: ChatMemberUpdated):
    chat_id = member.chat.id
    if (
        not member.new_chat_member
        or member.new_chat_member.status in {"banned", "left", "restricted"}
        or member.old_chat_member
    ):
        return
    user = member.new_chat_member.user if member.new_chat_member else member.from_user
    
    if not temp.WELCOME_ENABLED.get(chat_id, True):  # Check if welcome messages are enabled
        return

    try:
        pic = await app.download_media(
            user.photo.big_file_id, file_name=f"pp{user.id}.png"
        )
    except AttributeError:
        pic = "assets/profilepic.jpg"
    
    if (temp.MELCOW).get(f"welcome-{chat_id}") is not None:
        try:
            await temp.MELCOW[f"welcome-{chat_id}"].delete()
        except Exception as e:
            LOGGER.error(e)
    
    try:
        welcomeimg = welcomepic(
            pic, user.first_name, member.chat.title, user.id, user.username
        )
        mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
        joined_date = datetime.fromtimestamp(time.time()).strftime("%Y.%m. %d %H:%M:%S")
        first_name = (
            f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        )
        temp.MELCOW[f"welcome-{chat_id}"] = await app.send_photo(
            member.chat.id,
            photo=welcomeimg,
            caption=f"""ʜᴇʟʟᴏ {mention}, ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {member.chat.title} ɢʀᴏᴜᴘ.\n
    ┏━━━━━━━♛━━━━━━━┓
⍟ ɴᴀᴍᴇ : {first_name}
⍟ ɪᴅ : {user.id}
⍟ ᴅᴀᴛᴇ ᴊᴏɪɴᴇᴅ : {joined_date}
┗━━━━━━━♛━━━━━━━┛
""",
        )
    except Exception as e:
        LOGGER.error(e)
    
    try:
        os.remove(f"downloads/welcome#{user.id}.png")
        os.remove(f"downloads/pp{user.id}.png")
    except Exception as e:
        pass

@app.on_message(filters.new_chat_members & filters.group, group=-1)
async def bot_wel(_, message):
    for u in message.new_chat_members:
        if u.id == app.me.id:
            await app.send_message(
                LOG_CHANNEL_ID,
                f"""
#NEW_GROUP
┏━━━━━━━━━━━━━━━┓
➢ 𝖦𝗋𝗈𝗎𝗉 𝖭𝖺𝗆𝖾: {message.chat.title}
➢ 𝖦𝗋𝗈𝗎𝗉 𝖨𝖣: {message.chat.id}
➢ 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾: @{message.chat.username}
┗━━━━━━━━━━━━━━━┛
""",
            )

@app.on_message(filters.new_chat_members)
async def auto_enable_welcome(_, message):
    chat_id = message.chat.id
    await add_wlcm(chat_id)
    LOGGER.info(f"Enabled special welcome in {message.chat.title}")

@app.on_message(filters.command(["swelcome", "swelcome on", "swelcome off"]) & filters.group)
async def toggle_welcome(_, message):
    command = message.command[0]
    chat_id = message.chat.id
    if command == "swelcome on":
        temp.WELCOME_ENABLED[chat_id] = True
        await message.reply("Special welcome messages are enabled for this group.")
    elif command == "swelcome off":
        temp.WELCOME_ENABLED[chat_id] = False
        await message.reply("Special welcome messages are disabled for this group.")

@app.on_message(filters.new_chat_members)
async def handle_welcome(_, message):
    chat_id = message.chat.id
    if temp.WELCOME_ENABLED.get(chat_id, True):
        # Ensure that welcome messages are enabled before processing
        await auto_enable_welcome(_, message)
