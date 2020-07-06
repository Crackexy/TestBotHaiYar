import requests
from telegram import Bot, Message, Update, ParseMode
from telegram.ext import CommandHandler, run_async

from haruka import dispatcher
from haruka.modules.helper_funcs.chat_status import user_admin


@run_async
@user_admin
def define(bot: Bot, update: Update, args):
    msg = update.effective_message
    word = " ".join(args)
    res = requests.get(f"https://googledictionaryapi.eu-gb.mybluemix.net/?define={word}")
    if res.status_code == 200:
        info = res.json()[0].get("meaning")
        if info:
            meaning = ""
            for count, (key, value) in enumerate(info.items(), start=1):
                meaning += f"<b>{count}. {word}</b> <i>({key})</i>\n"
                for i in value:
                    defs = i.get("definition")
                    meaning += f"• <i>{defs}</i>\n"
            msg.reply_text(meaning, parse_mode=ParseMode.HTML)
        else:
            return 
    else:
        msg.reply_text("No results found!")
        
        
        
DEFINE_HANDLER = CommandHandler("define", define, pass_args=True)
dispatcher.add_handler(DEFINE_HANDLER)


__mod_name__ = "Dictionary"
