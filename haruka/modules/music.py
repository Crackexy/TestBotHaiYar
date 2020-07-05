from telethon import events
import subprocess
from telethon.errors import MessageEmptyError, MessageTooLongError, MessageNotModifiedError
import io
import asyncio
import time
from haruka.events import register
import glob
import os
import spotdl, subprocess

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

@register(pattern="^/song (.*)")
async def _(event):
    if event.fwd_from:
        return
    if event.is_group:
     if not (await is_register_admin(event.input_chat, event.message.sender_id)):
       await event.reply("I only respond to admins so go get some permissions !")
       return
    cmd = event.pattern_match.group(1)
    cmnd = f'"{cmd}"'
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    subprocess.run(["spotdl", "--song", cmnd])
    subprocess.run('for f in *.opus; do      mv -- "$f" "${f%.opus}.mp3"; done', shell=True)
    l = glob.glob("*.mp3")
    loa = l[0]
    await event.reply("sending the song")
    await event.client.send_file(
                event.chat_id,
                loa,
                force_document=True,
                allow_cache=False,
                caption=cmd,
                reply_to=reply_to_id
            )
    subprocess.Popen("rm -rf *.mp3", shell=True)

__help__ = """
 - /song <name>: search download and return a song in the best format
"""
__mod_name__ = "Songs" 
