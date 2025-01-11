import datetime
from datetime import date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

import locale

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

month_dic =\
    {
        "Январь":"Января",
        "Февраль":"Февраля",
        "Март":"Марта",
        "Апрель":"Апреля",
        "Май":"Мая",
        "Июнь":"Июня",
        "Июль":"Июля",
        "Август":"Августа",
        "Сентябрь":"Сентября",
        "Октябрь":"Октября",
        "Ноябрь":"Ноября",
        "Декабрь":"Декабря"
    }

schedule = \
        [True, False, True,True, False, True,False,
         True, False, True, True, False, True, False,
         True, False, True, True, False, True, False,
         True, False, True, True, False, True, False,
         True, False, True
        ]

yes = "✅"
no = "❌"

class Manager:
    bot: telebot = None

    def __init__(self, _bot: telebot):
        self.bot = _bot
        locale.setlocale(locale.LC_TIME, 'ru_RU')

    def choise_month(self, msg):
        current_month = date.today()
        next_month = date.today() + relativedelta(months=1)
        prev_month = date.today() - relativedelta(months=1)
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            InlineKeyboardButton(prev_month.strftime("%B"), callback_data="prev"),
            InlineKeyboardButton(current_month.strftime("%B"), callback_data="current"),
            InlineKeyboardButton(next_month.strftime("%B"), callback_data="next"))
        send_msg = self.bot.send_message(msg.chat.id, "Выберите месяц: ", reply_markup=markup)

    def choise_day(self, msg, date : date):
        markup = InlineKeyboardMarkup(row_width=7)
        days = []
        for i in range(monthrange(date.year, date.month)[1]):
            days.append(InlineKeyboardButton(f"{i + 1} {yes if schedule[i] else no}",
                                             callback_data=f"{i + 1}"
                                                           f"-{datetime.date(date.year, date.month, i + 1).strftime("%Y%m%d")}"))
        markup.add(*days)
        self.bot.edit_message_text(chat_id = msg.chat.id,message_id=msg.message_id ,
                                   text = "Выберите число: ", reply_markup=markup)

    def change_workstatus(self, msg, date : date):
        markup = InlineKeyboardMarkup(row_width=2)
        choises = []
        choises.append(InlineKeyboardButton(f"{yes} Да", callback_data=f"yes-{date.strftime("%Y%m%d")}"))
        choises.append(InlineKeyboardButton(f"{no} Нет", callback_data=f"no-{date.strftime("%Y%m%d")}"))
        markup.add(*choises)
        self.bot.send_message(msg.chat.id,
                         f"Выбранная дата: {date.day} {month_dic[date.strftime("%B")]}"
                         f"\nВы работаете:", reply_markup = markup)