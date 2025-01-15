import datetime
from datetime import date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

import locale

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

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

    def choise_month(self, msg):
        current_month = date.today()
        next_month = date.today() + relativedelta(months=1)
        prev_month = date.today() - relativedelta(months=1)
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            InlineKeyboardButton(prev_month.strftime("%B"), callback_data=f"{callback_id}-prev"),
            InlineKeyboardButton(current_month.strftime("%B"), callback_data=f"{callback_id}-current"),
            InlineKeyboardButton(next_month.strftime("%B"), callback_data=f"{callback_id}-next"))
        send_msg = self.bot.send_message(msg.chat.id, "Выберите месяц: ", reply_markup=markup)

    def choise_day(self, msg, date : date):
        markup = InlineKeyboardMarkup(row_width=7)
        days = []
        for i in range(monthrange(date.year, date.month)[1]):
            days.append(InlineKeyboardButton(f"{i + 1} {yes if schedule[i] else no}",
                                             callback_data=f"{callback_id}-{i + 1}"
                                                           f"-{datetime.date(date.year, date.month, i + 1).strftime('%Y%m%d')}"))
        markup.add(*days)
        self.bot.edit_message_text(chat_id = msg.chat.id,message_id=msg.message_id ,
                                   text = "Выберите число: ", reply_markup=markup)

    def change_workstatus(self, msg, date : date):
        markup = InlineKeyboardMarkup(row_width=2)
        choises = []
        choises.append(InlineKeyboardButton(f"{yes} Да", callback_data=f"{callback_id}-yes-{date.strftime('%Y%m%d')}"))
        choises.append(InlineKeyboardButton(f"{no} Нет", callback_data=f"{callback_id}-no-{date.strftime('%Y%m%d')}"))
        markup.add(*choises)
        self.bot.send_message(msg.chat.id,
                         f"Выбранная дата: {date.day} {month_dic[date.strftime('%B')]}"
                         f"\nВы работаете:", reply_markup = markup)

    def salary(self, msg):
        temploee = 1
        c = 1
        B = 1
        tpoint = 1
        n = 1
        s = (temploee * c) + (B/(tpoint*n*temploee))
        self.bot.send_message(msg.chat.id, s)

    def report(self, message):
        send = self.bot.send_message(message.chat.id, "Введите текст отчета:")
        self.bot.register_next_step_handler(send, self.create_report)

    def create_report(self, message):
        a = list(message.text.split('\n'))
        point_name = a[0]
        date = a[1]
        cash = a[2][a[2].find(':') + 2:]
        non_cash = a[3][a[3].find(':') + 2:]
        app = a[4][a[4].find(':') + 2:]
        returns = a[5][a[5].find(':') + 2:]
        number_of_receipts = a[6][a[6].find(':') + 2:]
        all_cash = a[7][a[7].find(':') + 2:]
        terminal = a[8][a[8].find(':') + 2:]
        merchant = a[9][a[9].find(':') + 2:]
        staff = a[10][a[10].find(':') + 2:]
        user_name = a[11][:a[11].find('(')]
        rate = a[11][a[11].find('(') + 1:a[11].find(')')]
        time = a[11][a[11].find('-') + 2:a[11].find('ч')]

        #self.bot.send_message(message.chat.id, point_name)
    
    func = {
        "Посмотреть зарплату" : lambda self, msg : self.salary(msg),
        "График смен" : lambda self, msg : self.choise_month(msg),
        "Добавить отчет" : lambda self, msg : self.report(msg)
    }

    def msg_handler(self, message):
        self.func[message.text](self, message)

    def callback_handler(self, call):
        try:
            if call.message:
                data = call.data.split(sep="-")[1:]
                if data[0] == "prev":
                    self.choise_day(call.message, date.today() - relativedelta(months=1))
                elif data[0] == "current":
                    self.choise_day(call.message, date.today())
                elif data[0] == "next":
                    self.choise_day(call.message, date.today() + relativedelta(months=1))
                elif data[0].isdigit():
                    if int(data[0]) >= 1 and int(data[0]) <= 31:
                        self.change_workstatus(call.message, date.fromisoformat(data[1]))
                elif call.data == 'create_report':
                    self.bot.send_message(call.message.chat.id, 'Enter the :')
                elif data[0] == "yes":
                    schedule[date.fromisoformat(data[1]).day - 1] = True
                    self.bot.delete_message(call.message.chat.id, call.message.message_id)
                elif data[0] == "no":
                    schedule[date.fromisoformat(data[1]).day - 1] = False
                    self.bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print(e)