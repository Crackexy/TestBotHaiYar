# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
"""
This module updates the userbot based on Upstream revision
"""

import sys
from os import execl, remove, path
import heroku3

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from alexa import HEROKU_APIKEY, HEROKU_APPNAME, STRING_SESSION
from alexa.events import register


async def gen_chlog(repo, diff):
    ch_log = ''
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += f'•[{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n'
    return ch_log


async def is_off_br(br):
    off_br = ['stable', 'master']
    if br in off_br:
        return 1
    return


@register(pattern="^/update(?: |$)(.*)")
async def upstream(ups):
    "For .update command, check if the bot is up to date, update if specified"
    lol = await ups.edit("`Checking for updates, please wait....`")
    conf = ups.pattern_match.group(1)
    off_repo = 'https://github.com/Ayush1311/RealAlexaBot'

    try:
        txt = "`Oops.. Updater cannot continue due to "
        txt += "some problems.`\n\n**LOGTRACE:**\n"
        repo = Repo()
    except NoSuchPathError as error:
        await lol.edit(f'{txt}\n`directory {error} is not found`')
        return
    except InvalidGitRepositoryError as error:
        await lol.edit(f'{txt}\n`directory {error} does \
                        not seems to be a git repository`')
        return
    except GitCommandError as error:
        await lol.edit(f'{txt}\n`Early failure! {error}`')
        return

    ac_br = repo.active_branch.name
    if not await is_off_br(ac_br):
        await lol.edit(
            f'**[UPDATER]:**` Looks like you are using your own custom branch ({ac_br}). '
            'In that case, Updater is unable to perform a successful update. '
            'Please checkout to any official branch.`')
        return

    try:
        repo.create_remote('upstream', off_repo)
    except BaseException:
        pass

    ups_rem = repo.remote('upstream')
    ups_rem.fetch(ac_br)
    changelog = await gen_chlog(repo, f'HEAD..upstream/{ac_br}')

    if not changelog:
        await lol.edit(f'\n`Your BOT is `**up-to-date**` with `**{ac_br}**\n')
        return

    if conf != "now":
        changelog_str = f'**New UPDATE available for [{ac_br}]:\n\nCHANGELOG:**\n`{changelog}`'
        if len(changelog_str) > 4096:
            await lol.edit("`Changelog is too big, view the file to see it.`")
            file = open("output.txt", "w+")
            file.write(changelog_str)
            file.close()
            await ups.client.send_file(
                ups.chat_id,
                "output.txt",
                reply_to=ups.id,
            )
            remove("output.txt")
        else:
            await lol.edit(changelog_str)
        await ups.respond("Use the `/update now` command to update")
        return

    await lol.edit('`New update found, updating...`')

    ups_rem.fetch(ac_br)
    repo.git.reset('--hard', 'FETCH_HEAD')

    if HEROKU_APIKEY != None:
        # Heroku configuration, which can rebuild the Docker image with newer changes
        heroku = heroku3.from_key(HEROKU_APIKEY)
        if HEROKU_APPNAME != None:
            try:
                heroku_app = heroku.apps()[HEROKU_APPNAME]
            except KeyError:
                await lol.edit(
                    "```Error: HEROKU_APPNAME config is invalid! Make sure an app with that "
                    "name exists and your HEROKU_APIKEY config is correct.```")
                return
        else:
            await lol.edit(
                "```Error: HEROKU_APPNAME config is not set! Make sure to set your "
                "Heroku Application name in the config.```")
            return

        await lol.edit(
            "`Heroku configuration found! Updater will try to update and restart Alexa"
            "automatically if succeeded. Try checking if Alexa is alive by using the"
            "\".alive\" command after a few minutes.`")

        # Set git config for commiting session and config
        repo.config_writer().set_value("user", "name",
                                       "Alexa Updater").release()
        repo.config_writer().set_value("user", "email",
                                       "<>").release()  # No Email

 
        heroku_remote_url = heroku_app.git_url.replace(
            "https://", f"https://api:{HEROKU_APIKEY}@")

        remote = None
        if 'heroku' in repo.remotes:
            remote = repo.remote('heroku')
            remote.set_url(heroku_remote_url)
        else:
            remote = repo.create_remote('heroku', heroku_remote_url)

        try:
            remote.push(refspec="HEAD:refs/heads/master", force=True)
        except GitCommandError as e:
            await lol.edit(f'{txt}\n`Early failure! {e}`')
            return
    else:
        # Heroku configs not set, just restart the bot
        await lol.edit(
            '`Successfully Updated!\n'
            'Alexa is restarting... Wait for a few seconds, then '
            'check if Alexa is alive by using the "/start" command.`')

        await ups.client.disconnect()
        # Spin a new instance of bot
        execl(sys.executable, sys.executable, *sys.argv)
        # Shut the existing one down
        exit()