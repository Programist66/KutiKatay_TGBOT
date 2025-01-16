import datetime
from datetime import date
from calendar import monthrange
from enum import Enum
from io import BytesIO

from dateutil.relativedelta import relativedelta

import locale

import openpyxl
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InputFile

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
    remove = "➖"
    add = "➕"
    ok = "🆗"
    good = "🟩"
    bad = "🟥"

class callback_type(Enum):
    prew_my_month = "pmm"
    prew_operator_month = "pom"
    current_my_month = "cmm"
    current_operator_month = "com"
    next_my_month = "nmm"
    next_operator_month = "nom"
    my_day = "md"
    operator_day = "od"
    yes = "yes"
    no = "no"
    ok = "ok"
    remove = "remove"
    remove_operator = "ro"
    add = "add"
    add_operator ="ao"

def declension_hours(n, one = "час", two = "часа", five = "часов"):
    if n % 10 == 1 and n % 100 != 11:
        return one
    elif 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
        return two
    else:
        return five

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
        text = ""
        schedule = BDWorker.get_schedule_by_tg_id(msg.chat.id, date.month)
        items=[]
        if date <= date.today():
            items = [InlineKeyboardButton(f"{emoji.ok.value}", callback_data=f"{callback_id}-{callback_type.ok.value}-{date.strftime('%Y%m%d')}")]
            text = "Вы не работали!"
            for i in range(len(schedule)):
                if schedule[i][0] == date:
                    if schedule[i][1]:
                        if schedule[i][3] is None:
                          text = "Вы не работали"
                        else:
                            text = f"Вы работали на ТП: {BDWorker.get_rental_point_by_id(schedule[i][3])[0]}"
                            text += f"\nОтработали: {schedule[i][4]} {declension_hours(schedule[i][4])}"

        else:
            text = "ТП не назначена управляющим"            
            for i in schedule:
                if i[0] == date:
                    if i[3] is not None:
                        text = f"ТП: {BDWorker.get_rental_point_by_id(i[3])[0]}"
                    if i[1] == True:
                        items = [InlineKeyboardButton(f"{emoji.ok.value}", callback_data=f"{callback_id}-{callback_type.ok.value}-{date.strftime('%Y%m%d')}"),
                                InlineKeyboardButton(f"{emoji.no.value} Не буду рабоать", callback_data=f"{callback_id}-{callback_type.no.value}-{date.strftime('%Y%m%d')}")]
                    elif i[1] == False:
                        items = [InlineKeyboardButton(f"{emoji.yes.value} Буду рабоать", callback_data=f"{callback_id}-{callback_type.yes.value}-{date.strftime('%Y%m%d')}"),
                                InlineKeyboardButton(f"{emoji.ok.value}", callback_data=f"{callback_id}-{callback_type.ok.value}-{date.strftime('%Y%m%d')}")]
        markup.add(*items)
        self.bot.reply_to(msg, f"Выбранная дата: {date.day} {month_dic[date.strftime('%B')]}"
                              f"\n{text}", reply_markup=markup)
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
    
    def choise_day_for_operator(self, msg : types.Message, date:date, isFirstCall = True):
        markup = InlineKeyboardMarkup(row_width=7)
        days = []
        if isFirstCall:
            self.bot.delete_message(msg.chat.id, msg.message_id)
        points = BDWorker.get_subordinate_rental_points_id_by_tg_id(msg.chat.id) 
        for point in points:
            days = []
            schedule = BDWorker.get_schedule_by_month_and_rental_point_id(date.month, point[0])            
            for i in range(monthrange(date.year, date.month)[1]):
                text = f"{i + 1} {emoji.bad.value}"
                day = InlineKeyboardButton(text=f"{text}", callback_data=f"{callback_id}-{i + 1}"
                                                            f"-{datetime.date(date.year, date.month, i + 1).strftime('%Y%m%d')}"
                                                            f"-{callback_type.operator_day.value}-{point[0]}")
                for x in range(len(schedule)):
                    if schedule[x][0].day == i+1:
                        text = f"{i + 1} {emoji.good.value}"                        
                        day = InlineKeyboardButton(text=f"{text}", callback_data=f"{callback_id}-{i + 1}"
                                                    f"-{datetime.date(date.year, date.month, i + 1).strftime('%Y%m%d')}"
                                                    f"-{callback_type.operator_day.value}-{point[0]}")                    
                days.append(day)
            markup.add(*days)        
            self.bot.send_message(msg.chat.id, text=f"Выберите число для точки: {BDWorker.get_rental_point_by_id(point[0])[0]}",
                                   reply_markup=markup)
    
    def change_operator_list(self, msg : types.Message, date:date, rental_point_id:int):
        markup = InlineKeyboardMarkup(row_width=1)
        operators = []
        operators_id = BDWorker.get_operator_id_by_rental_point_id_and_date(rental_point_id, date)            
        for operator_id in operators_id:
            operators.append(InlineKeyboardButton(text=f"{BDWorker.get_operator_by_id(int(operator_id[0]))[0]}", callback_data="dummy"))
        
        if date >= datetime.date.today():
            if len(operators_id) > 0:
                operators.append(InlineKeyboardButton(text=f"{emoji.remove.value} удалить", callback_data=f"{callback_id}"
                                                    f"-{callback_type.remove.value}"
                                                    f"-{date.strftime('%Y%m%d')}"
                                                    f"-{rental_point_id}"))
            operators.append(InlineKeyboardButton(text=f"{emoji.add.value} добавить", callback_data=f"{callback_id}"
                                                f"-{callback_type.add.value}"
                                                f"-{date.strftime('%Y%m%d')}"
                                                f"-{rental_point_id}"))
        else:
            operators.append(InlineKeyboardButton(text=f"{emoji.ok.value}", callback_data=f"{callback_id}-{callback_type.ok.value}"))
        markup.add(*operators)
        self.bot.reply_to(msg, text=f"Дата: {date.day} {month_dic[date.strftime('%B')]}\n"
                          f"ТП: {BDWorker.get_rental_point_by_id(rental_point_id)[0]}\n"
                          f"Сотруднки:", reply_markup=markup)

    def show_operators_list(self, msg : types.Message, date:date, rental_point_id:int, command : str):
        operators_id = []
        operators =[]
        markup = InlineKeyboardMarkup(row_width=1)
        if command == callback_type.add.value:
            operators_id = BDWorker.get_operators_id_by_date(date)
            if len(operators_id) == 0:
                operators.append(InlineKeyboardButton(text=f"{emoji.ok.value}", callback_data=f"{callback_id}-{callback_type.ok.value}"))
                markup.add(*operators)
                self.bot.edit_message_text(chat_id = msg.chat.id, message_id = msg.message_id, 
                                   text=f"Нет сотрудников для добавления!",
                                   reply_markup = markup)
                return
        elif command == callback_type.remove.value:
            operators_id = BDWorker.get_operator_id_by_rental_point_id_and_date(rental_point_id, date)
        for operator_id in operators_id:
            operators.append(InlineKeyboardButton(text=f"{BDWorker.get_operator_by_id(operator_id[0])[0]}", 
                                                  callback_data=f"{callback_id}"
                                                  f"-{callback_type.add_operator.value if command == callback_type.add.value else callback_type.remove_operator.value}"
                                                  f"-{date.strftime('%Y%m%d')}"
                                                  f"-{rental_point_id}"
                                                  f"-{operator_id[0]}"))
        markup.add(*operators)
        self.bot.edit_message_text(chat_id = msg.chat.id, message_id = msg.message_id, 
                                   text=f"Выберите сотрудника которого хотите {"добавить" if command == callback_type.add.value else "удалить"}",
                                   reply_markup = markup)
    
    def remove_operator(self, msg : types.Message, date:date, rental_point_id:int, operator_id:int):
        BDWorker.remove_operator_by_id_and_date_and_rental_point_id(operator_id, date, rental_point_id)
        self.bot.delete_message(msg.chat.id, msg.reply_to_message.message_id)
        self.bot.delete_message(msg.chat.id, msg.message_id)
        self.choise_day_for_operator(msg, date, isFirstCall=False)
    
    def add_operator(self, msg:types.Message, date:date, renta_point_id:int, operator_id:int):
        BDWorker.update_schedules_for_operator_id_by_date_and_rental_point_id(operator_id, date, renta_point_id)
        self.bot.delete_message(msg.chat.id, msg.reply_to_message.message_id)
        self.bot.delete_message(msg.chat.id, msg.message_id)
        self.choise_day_for_operator(msg, date, isFirstCall=False)
    #endregion    
    #region Выгрузить отчет
    def create_report(self, msg : types.Message):        
        points_id = BDWorker.get_subordinate_rental_points_id_by_tg_id(msg.chat.id)
        for point_id in points_id:         
            excel_file = self.create_excel_file(point_id[0])
            excel_file.seek(0)
            uploaded_file = InputFile(excel_file, f'{BDWorker.get_rental_point_by_id(point_id[0])[0]}.xlsx')

            self.bot.send_document(
                msg.chat.id,
                uploaded_file,
                caption=f"{BDWorker.get_rental_point_by_id(point_id[0])[0]}"
            )

    def create_excel_file(self, rental_point_id:int):
        date = datetime.date.today()
        days_result = BDWorker.get_day_result_for_rental_point_id_by_month(rental_point_id, date.today())

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = f"{BDWorker.get_rental_point_by_id(rental_point_id)[0]}"
        sheet.append(["Дата", "Итоговая касса", "колличество чеков", "Время работы ТП"])
        
        all_dates = []
        for i in days_result:
            all_dates.append(i[0])
        
        print(f"До {all_dates}")
        all_dates.sort()
        print(f"После {all_dates}")
        for i in range(monthrange(date.year, date.month)[1]):
            current_date = datetime.date(date.year, date.month, i+1)
            if current_date in all_dates:
                for day_result in days_result:
                    if days_result[0] == current_date:
                        sheet.append([current_date.strftime("%d.%m.%Y"), day_result[1], day_result[2], day_result[3]])
            else:
                sheet.append([current_date.strftime("%d.%m.%Y"), 0, 0, 0])

        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)
        return excel_file
    
    #endregion
    #region обработчики сообщий, колбэков и комманд
    func = {"Заполнить свой график": lambda self, msg: self.choise_month_for_me(msg),
            "Заполнить график операторов": lambda self, msg: self.choise_month_for_operator(msg),
            "Добавить отчет": lambda self, msg: self.bot.send_message(msg.chat.id, text=f"Пока не реализованно!!"),
            "Выгрузить отчет": lambda self, msg: self.create_report(msg),
            }

    def msg_handler(self, msg):
        self.func[msg.text](self, msg)

    def callback_handler(self, call : types.CallbackQuery):
        data = call.data.split(sep="-")[1:]
        if data[0] == callback_type.prew_my_month.value:
            self.choise_day_for_me(msg=call.message, date=date.today() - relativedelta(months=1))
        elif data[0] == callback_type.prew_operator_month.value:
            self.choise_day_for_operator(msg=call.message, date=date.today() - relativedelta(months=1))
        elif data[0] == callback_type.current_my_month.value:
            self.choise_day_for_me(msg=call.message, date=date.today())
        elif data[0] == callback_type.current_operator_month.value:
            self.choise_day_for_operator(msg=call.message, date=date.today())
        elif data[0] == callback_type.next_my_month.value:
            self.choise_day_for_me(msg=call.message,date= date.today() + relativedelta(months=1))
        elif data[0] == callback_type.next_operator_month.value:
            self.choise_day_for_operator(msg=call.message, date=date.today() + relativedelta(months=1))
        elif data[0].isdigit():
            if 1 <= int(data[0]) <= 31:
                if data[2] == callback_type.my_day.value:
                    self.change_workstatus(msg=call.message, date=date.fromisoformat(data[1]))
                elif data[2] == callback_type.operator_day.value:                    
                    self.change_operator_list(msg=call.message, date=date.fromisoformat(data[1]),rental_point_id=int(data[3]))
        elif data[0] == callback_type.remove.value:
            self.show_operators_list(msg=call.message,date=date.fromisoformat(data[1]), rental_point_id = int(data[2]), command = callback_type.remove.value)
        elif data[0] == callback_type.remove_operator.value:
            self.remove_operator(msg=call.message, date=date.fromisoformat(data[1]), rental_point_id=int(data[2]), operator_id=int(data[3]))
        elif data[0] == callback_type.add.value:
            self.show_operators_list(msg=call.message,date=date.fromisoformat(data[1]), rental_point_id = int(data[2]), command = callback_type.add.value)
        elif data[0] == callback_type.add_operator.value:
            self.add_operator(msg=call.message, date=date.fromisoformat(data[1]), renta_point_id=int(data[2]), operator_id=int(data[3]))
        elif data[0] in (callback_type.yes.value, callback_type.no.value, callback_type.ok.value):
            if data[0] == callback_type.yes.value:
                if BDWorker.get_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1])):
                    BDWorker.update_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=True)
                else:
                    BDWorker.add_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=True)
                self.choise_day_for_me(msg=call.message.reply_to_message, date=date.fromisoformat(data[1]))
            elif data[0] == callback_type.no.value:
                if BDWorker.get_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1])):
                    BDWorker.update_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=False)
                else:
                    BDWorker.add_schedule_by_tg_id_and_date(tg_id=call.message.chat.id, date=date.fromisoformat(data[1]), isWork=False)
                self.choise_day_for_me(msg=call.message.reply_to_message, date=date.fromisoformat(data[1]))
            
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            
            
            
    #endregion