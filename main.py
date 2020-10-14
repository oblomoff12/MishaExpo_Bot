# -*- coding: utf-8 -*-
# -*- Создание чат-бота для компании MishaExpo -*-

# Подготовочка
import config
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate
from random import randint
from oauthclient.oauth2api import oauth2api
from oauthclient.credentialutil import credentialutil
from oauthclient.model.model import environment
from urllib.parse import unquote
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from dateutil.parser import parse, ParserError
from datetime import datetime, timezone
from 

# Класс, собирающий все данные пользователя
class RequestStat:
    def _init_(self):
        self.goodid = 0
        self.start_date = datetime()
        self.finish_date = datetime()

# Словарик со значениями данных пользователя
StatRequests = dict()


# Работа с oauth2
oauth2api_inst = oauth2api()

user_access_token = None

credentialutil.load('ebay-config.yaml')

scopes = ['https://api.ebay.com/oauth/api_scope',
          'https://api.ebay.com/oauth/api_scope/buy.order.readonly',
          'https://api.ebay.com/oauth/api_scope/buy.guest.order',
          'https://api.ebay.com/oauth/api_scope/sell.marketing.readonly',
          'https://api.ebay.com/oauth/api_scope/sell.marketing',
          'https://api.ebay.com/oauth/api_scope/sell.inventory.readonly',
          'https://api.ebay.com/oauth/api_scope/sell.inventory',
          'https://api.ebay.com/oauth/api_scope/sell.account.readonly',
          'https://api.ebay.com/oauth/api_scope/sell.account',
          'https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly',
          'https://api.ebay.com/oauth/api_scope/sell.fulfillment',
          'https://api.ebay.com/oauth/api_scope/sell.analytics.readonly',
          'https://api.ebay.com/oauth/api_scope/sell.marketplace.insights.readonly',
          'https://api.ebay.com/oauth/api_scope/commerce.catalog.readonly',
          'https://api.ebay.com/oauth/api_scope/buy.shopping.cart',
          'https://api.ebay.com/oauth/api_scope/buy.offer.auction',
          'https://api.ebay.com/oauth/api_scope/commerce.identity.readonly',
          'https://api.ebay.com/oauth/api_scope/commerce.identity.email.readonly',
          'https://api.ebay.com/oauth/api_scope/commerce.identity.phone.readonly',
          'https://api.ebay.com/oauth/api_scope/commerce.identity.address.readonly',
          'https://api.ebay.com/oauth/api_scope/commerce.identity.name.readonly',
          'https://api.ebay.com/oauth/api_scope/commerce.identity.status.readonly',
          'https://api.ebay.com/oauth/api_scope/sell.finances',
          'https://api.ebay.com/oauth/api_scope/sell.item.draft',
          'https://api.ebay.com/oauth/api_scope/sell.payment.dispute',
          'https://api.ebay.com/oauth/api_scope/sell.item']

# создание функции,"дергающей" получение user_token'а
def get_user_token():
    # тут будет получения этого кода
    url_code = "v%5E1.1%23i%5E1%23f%5E0%23r%5E1%23p%5E3%23I%5E3%23t%5EUl41XzEwOjFCRjIyMEVERjZEN0FGQTNGOTNENTBGQjI1Mzk4RUU0XzJfMSNFXjEyODQ%3D"
    code = unquote(url_code)
    temp_access_token = oauth2api_inst.exchange_code_for_access_token(environment.SANDBOX, code)
    # проверка на ошибку
    global user_access_token
    user_access_token = temp_access_token

# Создание глобальной переменной для user_token'а
def get_user_access_token():
    global user_access_token
    if (user_access_token is None):
      get_user_token()
    # elif user_access_token.token_expiry > datetime.utcnow():
    # refresh_access_token()
    return user_access_token


# создание функции,"дергающей" получение refresh_user_token'а
def refresh_access_token():
   refresh_access_token = oauth2api_inst.get_access_token(environment.SANDBOX, user_access_token.refresh_token, scopes)
   #тут надо обновить поля токена если нет ошибки


#  Непосредственно, Каха (Бот MishaExpo-помощник)


GOODID, START_DATE, FINISH_DATE, PERFORM = range(4)

def start(update, context):

    update.message.reply_text\
        (
        "Привет!\n"
        "Меня зовут MishaExpo_bot, и я - твой помощник в получении статистики по товему товару в магазине Ebay :) \n\n"
        "В рамках нашего общения тебе нужно будет указать:\n"
        "свой GOODS_ID (Идентификатор твоего товара, состоящий из ____ цифр, известных только тебе)\n"
        )

    return GOODID

# Ввод ID товара
def user_entering_good_id(update, context):

    message = update.message
    if not message.text.isdigit():
        message.reply_text("Что-то пошло не так... Убедись, что введены исключительно цифры")

        return GOODID
    else:
        message.reply_text("Все здорово. Теперь введи дату начала периода, за который нужна аналитика, в формате дд.мм.гггг")
    StatRequests[message.chat.id] = RequestStat()
    StatRequests[message.chat.id].goodid = message.text
    return START_DATE


def parse_date(str_date):
  try:
    datetime = parse(str_date)
    return datetime
  except ParserError:
      print("Oops!  That was no date.  Try again...")

# Ввод начала периода
def user_entering_period_start(update, context):
    message = update.message
    str_date = update.message.text
    maybe_date = parse_date(str_date)
    if maybe_date is None:
        message.reply_text ("Че-т не так")
        return START_DATE
    if datetime.now() < maybe_date:
        message.reply_text("Че-т не так. Ты в будущем, чувак!")
        return START_DATE
    message.reply_text("Отлично. Ты шустришь. Надо бы потренироваться в том, чтобы успевать за тобой... А теперь введи дату окончания периода, за который нужна аналитика, в формате дд.мм.гггг")
    StatRequests[message.chat.id].start_date = maybe_date
    return FINISH_DATE

# Ввод окончания периода
def user_entering_period_finish(update, context):
    message = update.message
    str_date = update.message.text
    maybe_date = parse_date(str_date)
    if maybe_date is None:
        message.reply_text("Че-т не так")
        return FINISH_DATE
    if datetime.now() < maybe_date:
        message.reply_text("Че-т не так. Ты в будущем, чувак!")
        return FINISH_DATE
    if StatRequests[message.chat.id].start_date > maybe_date:
        message.reply_text("Че-т не так. Дта должна быть чуть раньше")
        return FINISH_DATE
    message.reply_text(
                "Ну, что ж. Здорово было пообщаться. Дай мне немного времени для того, чтобы отработать запрос, и увидимся в следующий раз!"
                )
    StatRequests[message.chat.id].finish_date = maybe_date
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END  # Это будет в самом конце

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(config.token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            GOODID: [MessageHandler(Filters.text & ~Filters.command, user_entering_good_id)],

            START_DATE: [MessageHandler(Filters.text & ~Filters.command, user_entering_period_start)],

            FINISH_DATE: [MessageHandler(Filters.text & ~Filters.command, user_entering_period_finish)]

            },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == "__main__":
    main()
