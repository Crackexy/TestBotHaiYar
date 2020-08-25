#  This is made by @AyushChatterjee
#  If you kang this without credits I swear ur mom will die 

import html
import json
import html
import os
from typing import List, Optional

from telegram import Bot, Update, ParseMode, TelegramError
from telegram.ext import CommandHandler, run_async
from telegram.utils.helpers import mention_html
from telegram.ext import Filters
from alexa import dispatcher,  SUDO_USERS, OWNER_ID
from alexa.modules.helper_funcs.chat_status import user_can_change
from alexa.modules.helper_funcs.extraction import extract_user
from alexa.modules.log_channel import loggable
import alexa.modules.sql.approve_sql as sql


def check_user_id(user_id: int, bot: Bot) -> Optional[str]:
    if not user_id:
        reply = "That...is a chat!"

    elif user_id == bot.id:
        reply = "This does not work that way."

    else:
        reply = None
    return reply


@run_async
@user_can_change
@loggable
def approve(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    reason = ""
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""
    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""    
    sql.set_APPROVE(user_id, reason)
    update.effective_message.reply_text(
        rt + "\nSuccessfully approved user {}".format(user_member.first_name))
    log_message = (f"#APPROVE\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")
    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message
    return log_message

@run_async
@user_can_change
@loggable
def unapprove(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    reason = ""
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""
    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""    
    sql.rm_APPROVE(user_id, reason)
    update.effective_message.reply_text(
        rt + "\nSuccessfully unapproved user {}".format(user_member.first_name))
    log_message = (f"#UNAPPROVE\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")
    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message
    return log_message


APPROVE_HANDLER = CommandHandler("approve", approve, pass_args=True, filters=Filters.group)
UNAPPROVE_HANDLER = CommandHandler("unapprove", unapprove, pass_args=True, filters=Filters.group)

dispatcher.add_handler(APPROVE_HANDLER)
dispatcher.add_handler(UNAPPROVE_HANDLER)
