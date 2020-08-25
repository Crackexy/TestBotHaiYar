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
from alexa.modules.log_channel import gloggable
import threading
from sqlalchemy import Column, UnicodeText, Boolean, Integer
from alexa.modules.sql import BASE, SESSION

class APPROVE(BASE):
    __tablename__ = "approved_users"

    user_id = Column(Integer, primary_key=True)
    is_approved = Column(Boolean)
    reason = Column(UnicodeText)

    def __init__(self, user_id, reason="", is_approved=True):
        self.user_id = user_id
        self.reason = reason
        self.is_approved = is_approved

    def __repr__(self):
        return "approved_status for {}".format(self.user_id)


APPROVE.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()

APPROVED_USERS = {}


def is_approved(user_id):
    return user_id in APPROVED_USERS


def check_APPROVE_status(user_id):
    try:
        return SESSION.query(APPROVE).get(user_id)
    finally:
        SESSION.close()


def set_APPROVE(user_id, reason=""):
    with INSERTION_LOCK:
        curr = SESSION.query(APPROVE.get(user_id)
        if not curr:
            curr = APPROVE(user_id, reason, True)
        else:
            curr.is_approved = True

        APPROVED_USERS[user_id] = reason

        SESSION.add(curr)
        SESSION.commit()


def rm_APPROVE(user_id):
    with INSERTION_LOCK:
        curr = SESSION.query(APPROVE).get(user_id)
        if curr:
            if user_id in APPROVED_USERS:  # sanity check
                del APPROVED_USERS[user_id]

            SESSION.delete(curr)
            SESSION.commit()
            return True

        SESSION.close()
        return False


def toggle_APPROVE(user_id, reason=""):
    with INSERTION_LOCK:
        curr = SESSION.query(APPROVE).get(user_id)
        if not curr:
            curr = APPROVE(user_id, reason, True)
        elif curr.is_approved:
            curr.is_approved = False
        elif not curr.is_approved:
            curr.is_approved = True
        SESSION.add(curr)
        SESSION.commit()


def __load_APPROVE_users():
    global APPROVED_USERS
    try:
        all_APPROVE = SESSION.query(APPROVE).all()
        APPROVED_USERS = {user.user_id: user.reason for user in all_APPROVE if user.is_approved}
    finally:
        SESSION.close()


__load_APPROVE_users()


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
@gloggable
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
@gloggable
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
    sql.rm_APPROVE(user_id, reason)
    update.effective_message.reply_text(
        rt + "\nSuccessfully unapproved user {}".format(user_member.first_name))
    log_message = (f"#UNAPPROVE\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")
    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message
    return log_message


APPROVE_HANDLER = CommandHandler(("approve"), addsudo, pass_args=True, filters=Filters.group
UNAPPROVE_HANDLER = CommandHandler(("unapprove"), addsupport, pass_args=True, filters=Filters.group)

dispatcher.add_handler(APPROVE_HANDLER)
dispatcher.add_handler(UNAPPROVE_HANDLER)
