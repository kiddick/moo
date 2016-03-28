# -*- coding: utf-8 -*-

import logging

import draft

from telegram import Emoji, ForceReply, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater

import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                           '%(message)s',
                    level=logging.DEBUG)

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
        self.category = CATEGORY[category]
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


def bookmark(bot, update, args):
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

        state[chat_id] = AWAIT_LINK
        context[chat_id] = (user_id, Record(category))
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

        # context[chat_id] = (user_id, update.message.text)
        context[chat_id][1].description = text
        # reply_markup = ReplyKeyboardMarkup([[YES, NO]], one_time_keyboard=True)
        # reply_markup=reply_markup
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
    bot.sendMessage(update.message.chat_id, text="Use /add to test this bot.")


updater = Updater(config.Config.BTOKEN)

# The command
updater.dispatcher.addTelegramCommandHandler('add', bookmark)
updater.dispatcher.addTelegramMessageHandler(bookmark)
updater.dispatcher.addTelegramCommandHandler('cancel', cancel)
updater.dispatcher.addTelegramCommandHandler('info', info)


updater.start_polling()
updater.idle()
