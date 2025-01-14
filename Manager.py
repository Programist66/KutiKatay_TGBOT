import datetime
from datetime import date
from calendar import monthrange
from enum import Enum

from dateutil.relativedelta import relativedelta

import locale

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

import BDWorker

month_dic = {
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

class emoji(Enum):    
    yes = "✅"
    no = "❌"
    ok = "🆗"
    good = "🟩"
    bad = "🟥"

class callback_type(Enum):
    prew_my_month = "prev_my_month"
    prew_operator_month = "prev_operator_month"
    current_my_month = "current_my_month"
    current_operator_month = "current_operator_month"
    next_my_month = "next_my_month"
    next_operator_month = "next_operator_month"
    my_day = "my_day"
    operator_day = "op_day"
    yes = "yes"
    no = "no"
    ok = "ok"

callback_id = "manager"

class Manager:
    bot: telebot = None

    def __init__(self, _bot: telebot):
        self.bot = _bot
        locale.setlocale(locale.LC_TIME, 'ru_RU')

    def Get_Manager_btn(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        items = []
        for i in self.func.keys():
            items.append(KeyboardButton(i))
        markup.add(*items)
        return markup

    #region Создать свой график:
    def choise_month_for_me(self, msg):
        current_month = date.today()
        next_month = date.today() + relativedelta(months=1)
        prev_month = date.today() - relativedelta(months=1)
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            InlineKeyboardButton(prev_month.strftime("%B"), callback_data= f"{callback_id}-{callback_type.prew_my_month.value}"),
            InlineKeyboardButton(current_month.strftime("%B"), callback_data=f"{callback_id}-{callback_type.current_my_month.value}"),
            InlineKeyboardButton(next_month.strftime("%B"), callback_data=f"{callback_id}-{callback_type.next_my_month.value}"))
        self.bot.send_message(msg.chat.id, "Выберите месяц: ", reply_markup=markup)

    def choise_day_for_me(self, msg, date: date):
        markup = InlineKeyboardMarkup(row_width=7)
        days = []
        schedule = BDWorker.get_schedule_by_tg_id(msg.chat.id, date.month)
        for i in range(monthrange(date.year, date.month)[1]):
            text = f"{i + 1}"
            for x in range(len(schedule)):
                if schedule[x][0].day == i+1:
                    if schedule[x][1]:
                        text += f" {emoji.yes.value}"
                    elif not schedule[x][1]:
                        text += f" {emoji.no.value}"
            days.append(InlineKeyboardButton(f"{text}",
                                             callback_data=f"{callback_id}-{i + 1}"
                                                           f"-{datetime.date(date.year, date.month, i + 1).strftime('%Y%m%d')}-{callback_type.my_day.value}"))
        markup.add(*days)
        self.bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                   text="Выберите число: ", reply_markup=markup)

    def change_workstatus(self, msg, date: date):
        markup = InlineKeyboardMarkup(row_width=1)
        text = "Вы будете работать?"
        schedule = BDWorker.get_schedule_by_tg_id(msg.chat.id, date.month)
        if date <= date.today():
            items = [InlineKeyboardButton(f"{emoji.ok.value}", callback_data=f"{callback_id}-{callback_type.ok.value}-{date.strftime('%Y%m%d')}")]
            text = "Вы не работали!"
            for i in range(len(schedule)):
                if schedule[i][0] == date:
                    if schedule[i][1]:
                        if schedule[i][3] is None:
                          text = "Вы работали"
                        else:
                            text = f"Вы работали на ТП: {BDWorker.get_rantal_point_by_id(schedule[i][3])}"

        else:
            items = [InlineKeyboardButton(f"{emoji.yes.value} Да", callback_data=f"{callback_id}-{callback_type.yes.value}-{date.strftime('%Y%m%d')}"),
                    InlineKeyboardButton(f"{emoji.no.value} Нет", callback_data=f"{callback_id}-{callback_type.no.value}-{date.strftime('%Y%m%d')}")]
        markup.add(*items)
        self.bot.reply_to(msg, f"Выбранная дата: {date.day} {month_dic[date.strftime('%B')]}"
                              f"\n{text}", reply_markup=markup)
        # self.bot.send_message(msg.chat.id,
        #                       f"Выбранная дата: {date.day} {month_dic[date.strftime('%B')]}"
        #                       f"\n{text}", reply_markup=markup)
    #endregion
    #region Создать график операторов
    def choise_month_for_operator(self, msg):
        current_month = date.today()
        next_month = date.today() + relativedelta(months=1)
        prev_month = date.today() - relativedelta(months=1)
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            InlineKeyboardButton(prev_month.strftime("%B"), callback_data= f"{callback_id}-{callback_type.prew_operator_month.value}"),
            InlineKeyboardButton(current_month.strftime("%B"), callback_data=f"{callback_id}-{callback_type.current_operator_month.value}"),
            InlineKeyboardButton(next_month.strftime("%B"), callback_data=f"{callback_id}-{callback_type.next_operator_month.value}"))
        self.bot.send_message(msg.chat.id, "Выберите месяц: ", reply_markup=markup)
    
    def choise_day_for_operator(self, msg : types.Message, date:date):
        markup = InlineKeyboardMarkup(row_width=7)
        days = []
        self.bot.delete_message(msg.chat.id, msg.message_id)
        points = BDWorker.get_subordinate_rental_points_id_by_tg_id(msg.chat.id)        
        for point in points:
            days = []
            schedule = BDWorker.get_schedule_by_month_and_rental_point_id(date.month, point[0])
            for i in range(monthrange(date.year, date.month)[1]):
                text = f"{i + 1} {emoji.bad.value}"
                day = InlineKeyboardButton(text=f"{text}", callback_data=f"{callback_id}-{i + 1}"
                                                            f"-{datetime.date(date.year, date.month, i + 1).strftime('%Y%m%d')}"
                                                            f"-{callback_type.operator_day.value}-None")
                for x in range(len(schedule)):
                    if schedule[x][0].day == i+1:
                        text = f"{i + 1} {emoji.good.value}"
                        day = InlineKeyboardButton(text=f"{text}", callback_data=f"{callback_id}-{i + 1}"
                                                            f"-{datetime.date(date.year, date.month, i + 1).strftime('%Y%m%d')}"
                                                            f"-{callback_type.operator_day.value}-{schedule[x][1]}")
                days.append(day)
            markup.add(*days)        
            self.bot.send_message(msg.chat.id, text=f"Выберите число для точки: {BDWorker.get_rental_point_by_id(point[0])[0]}",
                                   reply_markup=markup)
    #endregion    
    #region обработчики сообщий, колбэков и комманд
    func = {"Заполнить свой график": lambda self, msg: self.choise_month_for_me(msg),
            "Заполнить график операторов": lambda self, msg: self.choise_month_for_operator(msg),
            "Добавить отчет": 1,
            "Выгрузить отчет": 1,
            }

    def msg_handler(self, msg):
        self.func[msg.text](self, msg)

    def callback_handler(self, call : types.CallbackQuery):
        data = call.data.split(sep="-")[1:]
        if data[0] == callback_type.prew_my_month.value:
            self.choise_day_for_me(call.message, date.today() - relativedelta(months=1))
        elif data[0] == callback_type.prew_operator_month.value:
            self.choise_day_for_operator(call.message, date.today() - relativedelta(months=1))
        elif data[0] == callback_type.current_my_month.value:
            self.choise_day_for_me(call.message, date.today())
        elif data[0] == callback_type.current_operator_month.value:
            self.choise_day_for_operator(call.message, date.today())
        elif data[0] == callback_type.next_my_month.value:
            self.choise_day_for_me(call.message, date.today() + relativedelta(months=1))
        elif data[0] == callback_type.next_operator_month.value:
            self.choise_day_for_operator(call.message, date.today() + relativedelta(months=1))
        elif data[0].isdigit():
            if 1 <= int(data[0]) <= 31:
                if data[2] == callback_type.my_day.value:
                    self.change_workstatus(call.message, date.fromisoformat(data[1]))
                elif data[2] == callback_type.operator_day.value:
                    pass
        elif data[0] in (callback_type.yes.value, callback_type.no.value, callback_type.ok.value):
            if data[0] == callback_type.yes.value:
                if BDWorker.get_schedule_by_tg_id_and_date(call.message.chat.id, date.fromisoformat(data[1])):
                    BDWorker.update_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=True)
                else:
                    BDWorker.add_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=True)
            elif data[0] == callback_type.no.value:
                if BDWorker.get_schedule_by_tg_id_and_date(call.message.chat.id, date.fromisoformat(data[1])):
                    BDWorker.update_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=False)
                else:
                    BDWorker.add_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=False)
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.choise_day_for_me(call.message.reply_to_message, date.fromisoformat(data[1]))
    #endregion