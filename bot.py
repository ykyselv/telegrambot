import telebot
from telebot import types
from db_filling import db_filling
import threading
from db_connection import db_connection
from connection_close import connection_close
from datetime import datetime
from datetime import date, time
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from validation import validation
from average_search import average_search

argums = []
select_date = None

connection = db_connection()
cursor = connection.cursor()

t = threading.Thread(target = db_filling).start()

bot = telebot.TeleBot('5106469267:AAEp4zcMAYdE9KqCyA_By6iIxD3ZnrTiTEo')

def calen(call):
    calendar, step = DetailedTelegramCalendar(max_date=date.today()).build()
    bot.send_message(call.message.chat.id,
                     f"Select {LSTEP[step]}",
                     reply_markup=calendar)

@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def calen_call(call):
    result, key, step = DetailedTelegramCalendar(max_date=date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        global select_date
        select_date = result
        bot.edit_message_text(f"You selected {select_date}",
                              call.message.chat.id,
                              call.message.message_id)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        key_but1 = types.InlineKeyboardButton(text="Найти среднее за день", callback_data='average')
        key_but2 = types.InlineKeyboardButton(text="Курс на время", callback_data='time course')
        keyboard.add(key_but1, key_but2)
        bot.send_message(call.message.chat.id, "Выберите функцию", reply_markup=keyboard)

@bot.message_handler(commands=["start"])
def start(m, res = False):
    argums.clear()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_but1 = types.InlineKeyboardButton(text="BTC", callback_data='BTC')
    key_but2 = types.InlineKeyboardButton(text="BCH", callback_data='BCH')
    key_but3 = types.InlineKeyboardButton(text="DASH", callback_data='DASH')
    key_but4 = types.InlineKeyboardButton(text="ETH", callback_data='ETH')
    key_but5 = types.InlineKeyboardButton(text="LTC", callback_data='LTC')
    key_but6 = types.InlineKeyboardButton(text="XRP", callback_data='XRP')
    keyboard.add(key_but1, key_but2, key_but3, key_but4, key_but5, key_but6)
    bot.send_message(m.chat.id, "Выберите криптовалюту ", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    msg = None

    if call.data == 'BTC':
        msg = "BTC"
    elif call.data == 'BCH':
        msg = "BCH"
    elif call.data == 'DASH':
        msg = "DASH"
    elif call.data == 'ETH':
        msg = "ETH"
    elif call.data == 'LTC':
        msg = "LTC"
    elif call.data == 'XRP':
        msg = "XRP"
    elif call.data == 'UAH':
        msg = "UAH"
    elif call.data == 'USD':
        msg = "USD"
    elif call.data == 'EUR':
        msg = "EUR"
    elif call.data == 'GBP':
        msg = "GBP"

    if msg != None:
        bot.edit_message_text(f"You selected {msg}",
                          call.message.chat.id,
                          call.message.message_id)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_but1 = types.InlineKeyboardButton(text="UAH", callback_data='UAH')
    key_but2 = types.InlineKeyboardButton(text="USD", callback_data='USD')
    key_but3 = types.InlineKeyboardButton(text="EUR", callback_data='EUR')
    key_but4 = types.InlineKeyboardButton(text="GBP", callback_data='GBP')
    keyboard.add(key_but1, key_but2, key_but3, key_but4)
    if msg != None:
        argums.append(msg)
    if len(argums)<2:
        bot.send_message(call.message.chat.id, "Выберите валюту ", reply_markup=keyboard)
    else:
        if call.data == 'average':
            average = average_search(select_date, argums, cursor)
            bot.send_message(call.message.chat.id, average)
        elif call.data == 'time course':
            bot.send_message(call.message.chat.id, "Введите время в формате hh:mm")
        else:
            calen(call)

def res(msg):
    msg_text = msg.text
    global select_date
    select_daten = select_date.strftime('%m/%d/%Y')
    select_date_list = select_daten.split('/')
    select_date_tuple = date(int(select_date_list[2]), int(select_date_list[0]), int(select_date_list[1]))

    if validation(msg_text) == True:
        timem = msg_text.split(':')
        time_tuple = time(int(timem[0]),int(timem[1]))
    else:
        bot.send_message(msg.chat.id, f'Время введено не корректно')

    date_param = datetime.combine(select_date_tuple, time_tuple)

    try:
        val = ({'mes': date_param, 'cp_curr':argums[0],'curr':argums[1] })
        select_query = '''SELECT price FROM bitcoin WHERE DATE_TIME = %(mes)s AND CP_CURR = %(cp_curr)s AND CURR = %(curr)s'''
        cursor.execute(select_query, val)
        result = cursor.fetchall()
        markdown = """
            *bold text*
            _italic text_
            [text](URL)
            """
        bot.send_message(msg.chat.id, f"Курс {argums[0]} к {argums[1]} на дату {select_date} в {msg_text}: *{result[0][0]}*", parse_mode="Markdown")
        argums.clear()
    except IndexError:
        bot.send_message(msg.chat.id, "Данных по заданному времени не существует")

@bot.message_handler(content_types=["text"])
def response(msg):
    print("msg",msg.text)
    if msg.text == 'exit':
        connection_close(cursor, connection)
        exit()
    else:
        res(msg)

bot.infinity_polling()
























# from telebot import TeleBot
# from datetime import date
#
# from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
#
# bot = TeleBot('5277553579:AAHERvJFDP1-boy5mpTGurBRggy9E_ZeDRg')
#
#
# @bot.message_handler(commands=['start'])
# def start(m):
#     calendar, step = DetailedTelegramCalendar(max_date=date.today()).build()
#     bot.send_message(m.chat.id,
#                      f"Select {LSTEP[step]}",
#                      reply_markup=calendar)
#
#
# @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
# def cal(c):
#     print("Vania and Gnom best friends")
#     result, key, step = DetailedTelegramCalendar(max_date=date.today()).process(c.data)
#     if not result and key:
#         bot.edit_message_text(f"Select {LSTEP[step]}",
#                               c.message.chat.id,
#                               c.message.message_id,
#                               reply_markup=key)
#     elif result:
#         bot.edit_message_text(f"You selected {result}",
#                               c.message.chat.id,
#                               c.message.message_id)
#
#
# bot.polling()
