import datetime
from datetime import date
from calendar import monthrange
from urllib.parse import scheme_chars

from dateutil.relativedelta import relativedelta

import locale

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

import BDWorker

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

yes = "✅"
no = "❌"
ok = "🆗"

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
        schedule = BDWorker.get_schedule_by_tg_id(msg.chat.id, date.month)
        for i in range(monthrange(date.year, date.month)[1]):
            text = f"{i + 1}"
            for x in range(len(schedule)):
                if schedule[x][0].day == i+1:
                    if schedule[x][1]:
                        text += f" {yes}"
                    elif not schedule[x][1]:
                        text += f" {no}"
            days.append(InlineKeyboardButton(f"{text}",
                                             callback_data=f"{callback_id}-{i + 1}"
                                                           f"-{datetime.date(date.year, date.month, i + 1).strftime('%Y%m%d')}"))
        markup.add(*days)
        self.bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                   text="Выберите число: ", reply_markup=markup)

    def change_workstatus(self, msg, date: date):
        markup = InlineKeyboardMarkup(row_width=1)
        text = "Вы будете работать?"
        schedule = BDWorker.get_schedule_by_tg_id(msg.chat.id, date.month)
        if date < date.today():
            items = [InlineKeyboardButton(f"{ok}", callback_data=f"{callback_id}-ok-{date.strftime('%Y%m%d')}")]
            text = "Вы не работали!"
            for i in range(len(schedule)):
                if schedule[i][0] == date:
                    if schedule[i][1]:
                        text = "Вы работали!"

        else:
            items = [InlineKeyboardButton(f"{yes} Да", callback_data=f"{callback_id}-yes-{date.strftime('%Y%m%d')}"),
                    InlineKeyboardButton(f"{no} Нет", callback_data=f"{callback_id}-no-{date.strftime('%Y%m%d')}")]
        markup.add(*items)

        self.bot.send_message(msg.chat.id,
                              f"Выбранная дата: {date.day} {month_dic[date.strftime('%B')]}"
                              f"\n{text}", reply_markup=markup)

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
        self.func[msg.text](self, msg)

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
            if BDWorker.get_schedule_by_tg_id_and_date(call.message.chat.id, date.fromisoformat(data[1])):
                BDWorker.update_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=True)
            else:
                BDWorker.add_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=True)
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
        elif data[0] == "no":
            if BDWorker.get_schedule_by_tg_id_and_date(call.message.chat.id, date.fromisoformat(data[1])):
                BDWorker.update_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=False)
            else:
                BDWorker.add_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=False)
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
        elif data[0] == "ok":
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
