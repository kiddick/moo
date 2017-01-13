# -*- coding: utf-8 -*-

'''A main module with Moo bot powered by Telegram Bot API.'''

import logging

import draft
import qstack
import packtpub
import utils

from telegram import ParseMode
from telegram.ext import Job, Updater
from telegram.ext import CommandHandler, MessageHandler, Filters

import config


if config.Config.DEBUG:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
else:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        filename='moo.log'
    )

logging.debug('>>> Bot is started!\n')


MENU, AWAIT_INPUT, AWAIT_LINK, AWAIT_CONFIRMATION = range(4)

YES, NO = ('ok', '-')


state = {}
context = {}
values = {}

CATEGORY = {
    'py': 'python',
    'js': 'javascript',
    'so': 'stackoverflow',
    'mx': 'mix'
}


class Record(object):

    def __init__(self, category):
        self.category = category
        self.link = None
        self.description = None

    def __str__(self):
        return ('Category: {0}\n'
                'Link: {1}\n'
                'Description: {2}'.format(
                    self.category,
                    self.link,
                    self.description)
                )

    def markdown(self):
        return ('* {0}\n\n'
                '{1}'.format(self.link, self.description))


def bookmark(bot, update, args=None):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text
    chat_state = state.get(chat_id, MENU)
    chat_context = context.get(chat_id, None)

    if chat_state == MENU and text[0] == '/':
        try:
            category = args[0]
        except IndexError:
            bot.sendMessage(chat_id, text='Provide category please.')
            return
        record_category = CATEGORY.get(category)
        if not record_category:
            bot.sendMessage(
                chat_id,
                text='There is no such category: *{}!*'.format(category),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        state[chat_id] = AWAIT_LINK
        context[chat_id] = (user_id, Record(record_category))
        bot.sendMessage(chat_id,
                        text='Current category *{}*. Put link'.format(
                            category),
                        parse_mode=ParseMode.MARKDOWN)

    elif chat_state == AWAIT_LINK and chat_context[0] == user_id:
        state[chat_id] = AWAIT_INPUT

        context[chat_id][1].link = text
        bot.sendMessage(chat_id,
                        text='Add some description.')

    elif chat_state == AWAIT_INPUT and chat_context[0] == user_id:
        state[chat_id] = AWAIT_CONFIRMATION
        context[chat_id][1].description = text

        bot.sendMessage(
            chat_id, text="Check bookmark\n" + str(context[chat_id][1]))

    elif chat_state == AWAIT_CONFIRMATION and chat_context[0] == user_id:
        record = context[chat_id][1]
        state[chat_id] = MENU
        context[chat_id] = None
        if text == YES:
            draft.bookmark(record.category, record)
            draft.push()

            bot.sendMessage(chat_id,
                            text='Your information was successfully added.')
        else:
            bot.sendMessage(chat_id,
                            text='No any changes.')


def cancel(bot, update):
    chat_id = update.message.chat_id
    state[chat_id] = MENU
    context[chat_id] = None


def info(bot, update):
    bot.sendMessage(update.message.chat_id, text='Use /add to test this bot.')


def src(bot, update, args):
    if not args or args[0] not in CATEGORY:
        bot.sendMessage(update.message.chat_id, text=config.Config.GREPO)
    else:
        link = '{repo}/blob/master/{cat}/{cat}.md'.format(
            repo=config.Config.GREPO, cat=CATEGORY[args[0]])
        bot.sendMessage(update.message.chat_id, text=link)


def pyq(bot, update):
    link, title = qstack.nextq()
    qstack.incrementq()
    content = '* _[{}]({})_\n'.format(title, link)
    draft.add_question(content)
    draft.push(m='Add new question.')
    bot.sendMessage(update.message.chat_id,
                    text='[{}]({})\n'.format(title, link),
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True)


def packtpub_on(bot, update, job_queue, chat_data):
    chat_id = update.message.chat_id
    job = chat_data.get('job')
    if job:
        bot.sendMessage(update.message.chat_id, text='Subscription is already started!')
        return

    def notify(bot, job=None):
        item = packtpub.check()
        if isinstance(item, str):
            bot.sendMessage(chat_id, text=item)
        else:
            label, image = item
            bot.sendPhoto(chat_id, photo=image, caption=label)

    notify(bot)
    job = Job(notify, interval=6 * 60 * 60, repeat=True, context=chat_id)
    chat_data['job'] = job
    job_queue.put(job, next_t=utils.total(6))


def packtpub_off(bot, update, chat_data):
    job = chat_data.get('job')
    if not job:
        bot.sendMessage(update.message.chat_id, text='Nothing to stop :)')
        return
    job.schedule_removal()
    del chat_data['job']
    bot.sendMessage(update.message.chat_id, text='Turned off!')


updater = Updater(config.Config.BTOKEN)


# Commands
updater.dispatcher.add_handler(CommandHandler('add', bookmark, pass_args=True))
updater.dispatcher.add_handler(MessageHandler(Filters.text, bookmark))
updater.dispatcher.add_handler(CommandHandler('cancel', cancel))
updater.dispatcher.add_handler(CommandHandler('info', info))
updater.dispatcher.add_handler(CommandHandler('src', src, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('pyq', pyq))
updater.dispatcher.add_handler(
    CommandHandler('ppub_on', packtpub_on, pass_job_queue=True, pass_chat_data=True))
updater.dispatcher.add_handler(
    CommandHandler('ppub_off', packtpub_off, pass_chat_data=True))


updater.start_polling()
updater.idle()
