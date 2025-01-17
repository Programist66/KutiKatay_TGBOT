import datetime
from datetime import date
from calendar import monthrange
from enum import Enum
import re
from dateutil.relativedelta import relativedelta

import locale
import BDWorker

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

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
    current_my_month = "cmm"
    next_my_month = "nmm"
    my_day = "md"
    yes = "yes"
    no = "no"
    ok = "ok"

def declension_hours(n, one = "час", two = "часа", five = "часов"):
    if n % 10 == 1 and n % 100 != 11:
        return one
    elif 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
        return two
    else:
        return five

callback_id = "operator"

class Operator:
    bot: telebot = None

    def __init__(self, _bot: telebot):
        self.bot = _bot
        locale.setlocale(locale.LC_TIME, 'ru_RU')

    def Get_operator_Btn(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        items = []
        for i in self.func.keys():
            items.append(KeyboardButton(i))
        markup.add(*items)
        return markup

    #region Посмотреть график
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
            items = [InlineKeyboardButton(f"{emoji.yes.value} Буду рабоать", callback_data=f"{callback_id}-{callback_type.yes.value}-{date.strftime('%Y%m%d')}"),
                                InlineKeyboardButton(f"{emoji.no.value} Не буду рабоать", callback_data=f"{callback_id}-{callback_type.no.value}-{date.strftime('%Y%m%d')}")]            
            for i in schedule:
                print(i)
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
    #region Посмотреть зарплату
    def calculate_salary_per_day(self, day, user_id):
        date_of_work, point_id, hour_count = day
        emploee_count = len(BDWorker.get_operator_id_by_rental_point_id_and_date(rental_point_id=point_id, date=date_of_work))
        hour_rate = BDWorker.get_hour_rate_by_user_id(user_id=user_id)[0]
        percent_rate = BDWorker.get_percent_rate_by_point_id(rental_point_id=point_id)[0]
        total_cash, point_work_hour = BDWorker.get_day_result_for_rental_point_id_by_date(rental_point_id=point_id, date=date_of_work)
        if point_work_hour is None:
            point_work_hour = 12
        return self.calculate_salary(hour_count=hour_count, hour_rate=hour_rate, percent_rate=percent_rate, 
                                                    total_cash=total_cash, point_work_hours=point_work_hour, emploee_count=emploee_count)

    def calculate_salary(self, hour_count : int, hour_rate : int, percent_rate : int, total_cash : int, point_work_hours : int, emploee_count : int):
        salary = 0
        salary += hour_count * hour_rate
        percentage_of_total_cash = total_cash / 100 * percent_rate
        try:
            salary += percentage_of_total_cash / (point_work_hours * emploee_count) * hour_count
        except:
            pass
        return salary 

    def salary(self, msg : types.Message):
        send_msg = self.bot.send_message(msg.chat.id, "Обрабатывается...")
        user_id = BDWorker.get_user_by_TG_id(msg.chat.id)
        near_salary = 0
        next_salaty = 0
        today_date = date.today()
        if date(today_date.year, today_date.month, 10) < today_date <= date(today_date.year, today_date.month, 25):
            start_date = date(today_date.year, today_date.month, 1)
            end_date = date(today_date.year, today_date.month, 15)
            schedule = BDWorker.get_schedule_for_opeartor_id_by_date_diapozone(opeartor_id=user_id, start_date=start_date, end_date=end_date)
            for day in schedule:                
                near_salary += self.calculate_salary_per_day(day=day, user_id=user_id)
            if today_date <= end_date:
                next_salaty = 0
            else:
                start_date = date(start_date.year, start_date.month, 15)
                end_date = date(today_date.year, today_date.month, monthrange(today_date.year, today_date.month)[1])
                schedule = BDWorker.get_schedule_for_opeartor_id_by_date_diapozone(opeartor_id=user_id, start_date=start_date, end_date=end_date)
                for day in schedule:                
                    next_salaty += self.calculate_salary_per_day(day=day, user_id=user_id)
            self.bot.edit_message_text(chat_id=msg.chat.id, message_id=send_msg.message_id, text=f"Ближайшая зарплата(25 {month_dic[today_date.strftime('%B')]}): {near_salary}\n"+
                                  f"Следующая зарплата(10 {month_dic[(today_date + relativedelta(months=1)).strftime('%B')]}): {next_salaty}")
        else:
            if 1 <= today_date.day <= 10:
                start_date = today_date - relativedelta(months=1)
            else:
                start_date = today_date
            start_date = date(start_date.year, start_date.month, 16)
            end_date = date(start_date.year, start_date.month, monthrange(start_date.year, start_date.month)[1])
            schedule = BDWorker.get_schedule_for_opeartor_id_by_date_diapozone(opeartor_id=user_id, start_date=start_date, end_date=end_date)
            for day in schedule:                
                near_salary += self.calculate_salary_per_day(day=day, user_id=user_id)
            if 25 < today_date.day <= end_date.day:
                next_salaty = 0
                start_date += relativedelta(months=1)
            else:
                start_date = date(today_date.year, today_date.month, 1)
                end_date = date(today_date.year, today_date.month, 15)
                schedule = BDWorker.get_schedule_for_opeartor_id_by_date_diapozone(opeartor_id=user_id, start_date=start_date, end_date=end_date)
                for day in schedule:                
                    next_salaty += self.calculate_salary_per_day(day=day, user_id=user_id)
            self.bot.edit_message_text(chat_id=msg.chat.id, message_id=send_msg.message_id, text=f"Ближайшая зарплата(10 {month_dic[start_date.strftime('%B')]}): {near_salary}\n"+
                                  f"Следующая зарплата(25 {month_dic[start_date.strftime('%B')]}): {next_salaty}")
    #endregion
    #region Добавить отчет
    def report(self, message):
        send = self.bot.send_message(message.chat.id, "Введите текст отчета:")
        self.bot.register_next_step_handler(send, self.create_report)

    def create_report(self, message : types.Message):
        lines = message.text.strip().split('\n')
        lines = [i.strip() for i in lines]
        lines = [i for i in lines if i]
        point_name = lines[0]
        date = datetime.datetime.strptime(lines[1],"%d.%m.%y").date()
        cash = int(re.search(r'\d+', lines[2]).group())
        non_cash = int(re.search(r'\d+', lines[3]).group())
        app = int(re.search(r'\d+', lines[4]).group())
        refund = int(re.search(r'\d+', lines[6]).group())
        number_of_receipts = int(re.search(r'\d+', lines[7]).group())
        emploee_name = re.search(r'[а-яА-Я]+\s[а-яА-Я]+', lines[12]).group()
        hour_count = int(re.search(r'\d{1,2}\s?ч', lines[12]).group()[:-1].strip())

        BDWorker.add_report(date=date, point_name=point_name, emploee_name=emploee_name, 
                            cash=cash, non_cah=non_cash, count_of_checks=number_of_receipts, 
                            hour_count=hour_count, refund=refund, app=app)
        self.bot.send_message(message.chat.id, "Отчет успешно добавлен")
    #endregion
    func = {
        "Посмотреть зарплату" : lambda self, msg : self.salary(msg),
        "График смен" : lambda self, msg : self.choise_month(msg),
        "Добавить отчет" : lambda self, msg : self.report(msg)
    }

    def msg_handler(self, message):
        self.func[message.text](self, message)

    def callback_handler(self, call : types.CallbackQuery):
        data = call.data.split(sep="-")[1:]
        if data[0] == callback_type.prew_my_month.value:
            self.choise_day_for_me(msg=call.message, date=date.today() - relativedelta(months=1))
        elif data[0] == callback_type.current_my_month.value:
            self.choise_day_for_me(msg=call.message, date=date.today())
        elif data[0] == callback_type.next_my_month.value:
            self.choise_day_for_me(msg=call.message,date=date.today() + relativedelta(months=1))
        elif data[0].isdigit():
            if 1 <= int(data[0]) <= 31:
                if data[2] == callback_type.my_day.value:
                    self.change_workstatus(msg=call.message, date=date.fromisoformat(data[1]))
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