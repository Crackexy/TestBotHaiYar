import io
import textwrap
from PIL import Image, ImageDraw, ImageFont
from haruka.events import register
import random
from haruka import LOGGER, tbot
from telethon import types
from telethon.tl import functions

async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (await tbot(functions.channels.GetParticipantRequest(chat, user))).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator)
        )
    elif isinstance(chat, types.InputPeerChat):

        ui = await tbot.get_peer_id(user)
        ps = (await tbot(functions.messages.GetFullChatRequest(chat.chat_id))) \
            .full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator)
        )
    else:
        return None

@register(pattern="^/sticklet (.*)")
async def sticklet(event):
    if event.is_group:
     if not (await is_register_admin(event.input_chat, event.message.sender_id)):
       await event.reply("I only respond to admins so go get some permissions !")
       return
    sticktext = event.pattern_match.group(1)
    if not sticktext:
    	get = await event.get_reply_message()
    	sticktext = get.text
    if not sticktext:
    	await event.reply("`I need text to make sticker !`")
    	return
    sticktext = textwrap.wrap(sticktext, width=10)
    sticktext = '\n'.join(sticktext)
    image = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    fontsize = 230
    font = ImageFont.truetype("/root/haruka/haruka/DejaVuSansMono.ttf", size=fontsize)
    while draw.multiline_textsize(sticktext, font=font) > (512, 512):
        fontsize -= 3
        font = ImageFont.truetype("./haruka/DejaVuSansMono.ttf", size=fontsize)
    width, height = draw.multiline_textsize(sticktext, font=font)
    gg = ["red", "blue", "green", "yellow", "orange", "violet", "indigo"]
    hh = random.choice(gg)
    range = f"{hh}"
    draw.multiline_text(((512-width)/2,(512-height)/2), sticktext, font=font, fill=range)
    image_stream = io.BytesIO()
    image_stream.name = "sticker.webp"
    image.save(image_stream, "WebP")
    image_stream.seek(0)
    await event.client.send_file(event.chat_id, image_stream)


__help__ = """
 - /sticklet <text>: Turn a text into a sticker, you'll get a random colour from a rainbow(out of 7 colours) !
"""
__mod_name__ = "Sticklet"
