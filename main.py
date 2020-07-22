import config
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import telebot
from random import randint

#  Бот MishaExpo
import dbworker

bot = telebot.TeleBot(config.token)

#Поля, с которыми работает Бот
name = None
goods_id = None
period_start = None
period_end = None
pict = [
    'https://sun1-87.userapi.com/mWs_pmwCyeNpCNEYNrkT1NSyh_xzOGHryvkL8g/txAQThIQsYc.jpg',
    'https://static.tildacdn.com/tild6232-3235-4932-b933-663436363633/_.png'
    ]

#Начало диалога
@bot.message_handler(commands=["start"])
def cmd_start(message):
    state = dbworker.get_current_state(message.chat.id)
    if state == config.States.S_ENTER_NAME.value:
        bot.send_message(message.chat.id,
                         "Привет. Мне кажется, мы уже начинали наш с тобой диалог, и кто-то обещал отправить своё имя, но так и не сделал этого :( Жду...")
    elif state == config.States.S_ENTER_GOODS_ID.value:
        reply_ENTER_GOODS_ID = "Привет, " + dbworker.get_current_state(str(message.chat.id) + 'name')+"! Мне кажется, мы уже начинали наш с тобой диалог и в прошлый раз мы остановились на идентификаторе товара :( Жду..."
        bot.send_message(message.chat.id, reply_ENTER_GOODS_ID)
    elif state == config.States.S_PERIOD_START.value:
        reply_PERIOD_START = "Привет, " + dbworker.get_current_state(str(message.chat.id) + 'name') + "! Мне кажется, мы уже начинали наш с тобой диалог и в прошлый раз мы остановились на вводе даты начала периода, по которому нужно сформировать статистику :( Жду..."
        bot.send_message(message.chat.id,reply_PERIOD_START)
    elif state == config.States.S_PERIOD_END.value:
        reply_PERIOD_END = "Привет, " + dbworker.get_current_state(str(message.chat.id) + 'name') + "! Мне кажется, мы уже начинали наш с тобой диалог и в прошлый раз мы остановились на вводе даты окончания периода, по которому нужно сформировать статистику :( Жду..."
        bot.send_message(message.chat.id, reply_PERIOD_END)
    elif state == config.States.S_END.value:
        reply_END = "Привет, " + dbworker.get_current_state(str(message.chat.id) + 'name') + "! Мы уже как-то виделись с тобой. Давай попробуем еще разок получить нужную тебе информацию. Введи идентификационный номер своего товара. Напомню, что в нем могут быть только цифры"
        bot.send_message(message.chat.id, reply_END)
        dbworker.set_state(message.chat.id, config.States.S_ENTER_GOODS_ID.value)
    else:  # Под "остальным" понимаем состояние "0" - начало диалога
        bot.send_photo(message.chat.id, pict[randint(0, 1)])
        bot.send_message(message.chat.id, "Привет!\n"
                                      "Меня зовут MishaExpo_bot, и я - твой помощник в получении статистики по товему товару в магазине Ebay :) \n\n"
                                      "В рамках нашего общения тебе нужно будет указать:\n /GOODS_ID (Идентификатор твоего товара, состоящий из ____ цифр, известных только тебе)\n"
                                      "/PERIOD_START - начало периода, за который понадобится статистика.\n"
                                      '/PERIOD_END - окончание периода, за который понадобится статистика.\n\n'
                                      "Введи /info, чтобы узнать, кто я и чем я могу тебе помочь.\n"
                                      "Введи /commands, чтобы ознакомиться с доступными командами.\n"
                                      "Введи /reset, чтобы сбросить предыдущие состояния и начать заново.\n\n"
                                      "Давай знакомиться! Как тебя зовут?")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)

# Получение и сохранение пользовательских параметров для дальнейшего использования
def getting_name(message):
    name = message.text
    dbworker.set_property(str(message.chat.id)+"name", name)


def getting_goods_id(message):
    goods_id = message.text
    dbworker.set_property(str(message.chat.id)+"goods_id", goods_id)


def getting_period_start(message):
    period_start = datetime.strptime(message.text, '%d.%m.%Y').date()
    dbworker.set_property(str(message.chat.id)+"period_start", period_start)


def getting_period_end(message):
    period_end = datetime.strptime(message.text, '%d.%m.%Y').date()
    dbworker.set_property(str(message.chat.id)+"period_end", period_end)


# Сброс состояния, возврат к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Итак, напомни, как тебя зовут?")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)


@bot.message_handler(commands=["info"])
def cmd_info(message):
    bot.send_message(message.chat.id, " Метод /info расскажет тебе о том, что я умею.\n"
                                      "Для начала мы познакомимся и я попрошу ввести свой ник или Имя (как тебе будет удобно).\n"
                                      "На втором этапе я попрошу тебя ввести дату начала периода, за который требуется сформировать аналитику, \n"
                                      "на третьем - дату окончания этого периода.\n"
                                      "И, наконец, на четвертом этапе выдам тебе результат.\n"
                                      "Для того, чтобы начать заново, можно воспользоваться командой /reset")
    bot.send_message(message.chat.id, "Ряд комментариев:\n"
                                      "1. Я не буду ругаться на формат \"имени\". Твое имя или никнейм могут быть как реальными, так и не совсем\n"
                                      "2. А вот с введением идентификатора товара - буду. Если ты введешь нечисловое значение, то я выдам ошибку, поскольку идентификатор товара может быть только цифровым.\n"
                                      "3. К датам у меня чуть меньше претензий. Я умею их обрабатывать.\n"
                                      "4. Еще я умею запоминать команды, на которых мы остановились в прошлый раз.\n"
                                      "Здорово, если мы подружимся друг с другом, и я стану твоим незаменимым помощником")
    bot.send_message(message.chat.id, "Ниже команды, которыми ты можешь пользоваться: \n"
                                      "Ввод команды /commands расскажет тебе о существующих командах.\n"
                                      "Ввод команды /reset начнет диалог с начала.")

@bot.message_handler(commands=["commands"])
def cmd_commands(message):
    bot.send_message(message.chat.id, "/reset - возврат в начало диалога (этап \"знакомства\"); \n"
                                      "/start - \"стирание\" всех данных, и начало диалога;\n"
                                      "/info - общая информация о том, что я могу делать;\n"
                                      "/commands - общие сведения о командах.")
#Ввод имени/знакомство с юзером
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value)
def user_entering_name(message):
    getting_name (message)
    bot.send_message(message.chat.id, "Отличное(-ый) имя (никнейм), запомню!\n"
                                      "А ведь, наверное, меня могли звать так же...\n\n"
                                      "А теперь давай ближе к делу: введи твой GOODS_ID. Это уникальный идентификатор твоего товара, состоящий из ___ цифр.")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_GOODS_ID.value)


# Ввод ID товара
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_GOODS_ID.value)
def user_entering_goods_id(message):
    getting_goods_id(message)
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Что-то пошло не так... Убедись, что введены исключительно цифры")
        return
    else:
        bot.send_message(message.chat.id, "Все здорово. Теперь введи дату начала периода, за который нужна аналитика, в формате дд.мм.гггг")
    dbworker.set_state(message.chat.id, config.States.S_PERIOD_START.value)


# Ввод начала периода
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_PERIOD_START.value)
def user_entering_period_start(message):
    pattern = re.findall(r'(?<!\d)(?:0?[1-9]|[12][0-9]|3[01])[\.](?:0?[1-9]|1[0-2])[\.]\d{4}', message.text)
    if not message.text in pattern:
        bot.send_message(message.chat.id,
                         "Мне кажется, что-то не так с датой. Попробуй еще раз. Напомню про формат: дд.мм.гггг. И никак иначе")
        return
    else:
        getting_period_start(message)
        bot.send_message(message.chat.id,
                         "Отлично. Ты шустришь. Надо бы потренироваться в том, чтобы успевать за тобой... А теперь в том же формате введи дату окончания периода, за который нужна аналитика (в формате дд.мм.гггг)")
    dbworker.set_state(message.chat.id, config.States.S_PERIOD_END.value)


# Окончание диалога
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_PERIOD_END.value)
def user_end_dialog(message):
    pattern = re.findall(r'(?<!\d)(?:0?[1-9]|[12][0-9]|3[01])[\.](?:0?[1-9]|1[0-2])[\.]\d{4}', message.text)
    if not message.text in pattern:
        bot.send_message(message.chat.id,
                         "Мне кажется, что-то не так с датой. Попробуй еще раз. Напомню про формат: дд.мм.гггг. И никак иначе")
        return
    else:
        getting_period_end(message)
        bot.send_message(message.chat.id, "Ну, что ж. Здорово было пообщаться. Дай мне немного времени для того, чтобы отработать запрос, и увидимся в следующий раз!")
    dbworker.set_state(message.chat.id, config.States.S_END.value)


if __name__ == "__main__":
    bot.infinity_polling()