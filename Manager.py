import datetime
from datetime import date
from calendar import monthrange

from dateutil.relativedelta import relativedelta

import locale

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

month_dic = \
    {
        "Январь": "Января",
        "Февраль": "Февраля",
        "Март": "Марта",
        "Апрель": "Апреля",
        "Май": "Мая",
        "Июнь": "Июня",
        "Июль": "Июля",
        "Август": "Августа",
        "Сентябрь": "Сентября",
        "Октябрь": "Октября",
        "Ноябрь": "Ноября",
        "Декабрь": "Декабря"
    }

schedule = \
    [True, False, True, True, False, True, False,
     True, False, True, True, False, True, False,
     True, False, True, True, False, True, False,
     True, False, True, True, False, True, False,
     True, False, True
     ]

yes = "✅"
no = "❌"

callback_id = "manager"

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
            InlineKeyboardButton(prev_month.strftime("%B"), callback_data= f"{callback_id}-prev"),
            InlineKeyboardButton(current_month.strftime("%B"), callback_data=f"{callback_id}-current"),
            InlineKeyboardButton(next_month.strftime("%B"), callback_data=f"{callback_id}-next"))
        send_msg = self.bot.send_message(msg.chat.id, "Выберите месяц: ", reply_markup=markup)

    def choise_day(self, msg, date: date):
        markup = InlineKeyboardMarkup(row_width=7)
        days = []
        for i in range(monthrange(date.year, date.month)[1]):
            days.append(InlineKeyboardButton(f"{i + 1} {yes if schedule[i] else no}",
                                             callback_data=f"{callback_id}-{i + 1}"
                                                           f"-{datetime.date(date.year, date.month, i + 1).strftime('%Y%m%d')}"))
        markup.add(*days)
        self.bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                   text="Выберите число: ", reply_markup=markup)

    def change_workstatus(self, msg, date: date):
        markup = InlineKeyboardMarkup(row_width=2)
        choices = [InlineKeyboardButton(f"{yes} Да", callback_data=f"{callback_id}-yes-{date.strftime('%Y%m%d')}"),
                   InlineKeyboardButton(f"{no} Нет", callback_data=f"{callback_id}-no-{date.strftime('%Y%m%d')}")]
        markup.add(*choices)
        self.bot.send_message(msg.chat.id,
                              f"Выбранная дата: {date.day} {month_dic[date.strftime('%B')]}"
                              f"\nВы работаете:", reply_markup=markup)

    def Get_Manager_btn(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        items = []
        for i in self.func.keys():
            items.append(KeyboardButton(i))
        markup.add(*items)
        return markup

    func = {"Заполнить свой график": lambda self, msg: self.choise_month(msg),
            "Заполнить график операторов": 1,
            "Добавить отчет": 1,
            "Выгрузить отчет": 1,
            "Табелировать оператора": 1
            }

    def msg_handler(self, msg):
        self.func[msg.text](msg)

    def callback_handler(self, call):
        data = call.data.split(sep="-")[1:]
        if data[0] == "prev":
            self.choise_day(call.message, date.today() - relativedelta(months=1))
        elif data[0] == "current":
            self.choise_day(call.message, date.today())
        elif data[0] == "next":
            self.choise_day(call.message, date.today() + relativedelta(months=1))
        elif data[0].isdigit():
            if 1 <= int(data[0]) <= 31:
                self.change_workstatus(call.message, date.fromisoformat(data[1]))
        elif data[0] == "yes":
            schedule[date.fromisoformat(data[1]).day - 1] = True
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
        elif data[0] == "no":
            schedule[date.fromisoformat(data[1]).day - 1] = False
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
