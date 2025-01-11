import telebot.types

import Config
from telebot import TeleBot
from telebot import types

from datetime import date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

import Manager

bot = TeleBot(Config.BOT_TOKEN)

user_id = 0

Rate = {
    "Обычный": 250,
    "Золотой": 275,
    "Платиновый": 300
}

user = {
    "FIO": 1,
    "Rate": 2
}


manager = Manager.Manager(bot)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Добро пожаловать в бота который считает зарплату операторов КутиКатай.")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)


    item1 = types.KeyboardButton("Отчет")
    item2 = types.KeyboardButton("Изменить профиль")
    item3 = types.KeyboardButton("График смен")
    item4 = types.KeyboardButton("Зарплата")
    markup.add(item1, item2, item3, item4)
    bot.send_message(message.chat.id, "Вы зарегистрированы!", reply_markup=markup)

    print(message.chat.id)


@bot.message_handler(commands=['help'])
def send_help(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Отчет")
    item2 = types.KeyboardButton("Изменить профиль")
    item3 = types.KeyboardButton("График смен")
    item4 = types.KeyboardButton("Зарплата")
    markup.add(item1, item2, item3, item4)
    bot.send_message(message.chat.id,
                     "Вот список команд:\n/registration - зарегистрироваться\n/Report - отправить отчет о закрытии смены\n/Change_Profile - изменить данные профиля\n/shift_schedule - посмотреть график смен\n/salary - посмотреть зарплату",
                     reply_markup=markup)


# @bot.message_handler(commands=['registration'])
# def user_reg(message):
#     try:
#         markup = types.ReplyKeyboardRemove(selective=False)
#         msg = bot.send_message(message.chat.id, "Введите ФИО в формате(Иванов Иван Иванович):", reply_markup=markup)
#         bot.register_next_step_handler(msg, process_fullname_step)
#     except Exception as e:
#         print(e)
#         bot.reply_to(message, "ops")
#
#
# def process_fullname_step(message):
#     try:
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#         item1 = types.KeyboardButton("Обычный")
#         markup.add(item1)
#         item1 = types.KeyboardButton("Золотой")
#         markup.add(item1)
#         item1 = types.KeyboardButton("Платиновый")
#         markup.add(item1)
#         user["FIO"] = message.text
#         msg = bot.send_message(message.chat.id, "Введите ваш статус:", reply_markup=markup)
#         bot.register_next_step_handler(msg, process_Status)
#     except Exception as e:
#         print(e)
#         bot.reply_to(message, "ops")
#
#
# def process_Status(message):
#     try:
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         item1 = types.KeyboardButton("Отчет")
#         item2 = types.KeyboardButton("Изменить профиль")
#         item3 = types.KeyboardButton("График смен")
#         item4 = types.KeyboardButton("Зарплата")
#         markup.add(item1, item2, item3, item4)
#         user["Rate"] = message.text
#         bot.send_message(message.chat.id, f"Ваш профиль:\n{user['FIO']}\n{user['Rate']} оператор", reply_markup=markup)
#     except Exception as e:
#         print(e)
#         bot.reply_to(message, "ops")
#
#
# @bot.message_handler(commands=['Report'])
# def report(message):
#     try:
#         markup = types.ReplyKeyboardRemove(selective=False)
#         msg = bot.send_message(message.chat.id, "Перешлите сюда отчет о закрытии", reply_markup=markup)
#         bot.register_next_step_handler(msg, process_Report)
#
#     except Exception as e:
#         print(e)
#         bot.reply_to(message, "ops")
#
#
# def process_Report(message):
#     markup = types.InlineKeyboardMarkup(row_width=2)
#     item1 = types.InlineKeyboardButton("Верно", callback_data="good")
#     item2 = types.InlineKeyboardButton("Не верно", callback_data="bad")
#     markup.add(item1, item2)
#     bot.send_message(message.chat.id,
#                      f"Получите со ставки {250} за {12} часов: {3300}\nПолучите с кассы {30000} - {3}%: {30000 / 100 * 3}\nИтого:{4200} ",
#                      reply_markup=markup)
#
#
# @bot.callback_query_handler(func=lambda call: True)
# def callback_inline(call):
#     try:
#         if call.message:
#             if call.data == "good":
#
#                 #
#                 bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                       reply_markup=None, text=call.message.text)
#             elif call.data == "bad":
#                 pass
#             markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#             item1 = types.KeyboardButton("Отчет")
#             item2 = types.KeyboardButton("Изменить профиль")
#             item3 = types.KeyboardButton("График смен")
#             item4 = types.KeyboardButton("Зарплата")
#             markup.add(item1, item2, item3, item4)
#             bot.send_message(call.message.chat.id, "Отчет добавлен", reply_markup=markup)
#     except Exception as e:
#         print(e)
#
#
# @bot.message_handler(commands=['Change_Profile'])
# def change_profile(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     item1 = types.KeyboardButton("Обычный")
#     markup.add(item1)
#     item1 = types.KeyboardButton("Золотой")
#     markup.add(item1)
#     item1 = types.KeyboardButton("Платиновый")
#     markup.add(item1)
#     msg = bot.send_message(message.chat.id, "Введите ваш статус:", reply_markup=markup)
#     bot.register_next_step_handler(msg, process_Status)
#
#
@bot.message_handler(commands=['shift_schedule'])
def select_month(message):
    manager.choise_month(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            data = call.data.split(sep="-")
            if data[0] == "prev":
                manager.choise_day(call.message, date.today() - relativedelta(months=1))
            elif data[0] == "current":
                manager.choise_day(call.message, date.today())
            elif data[0] == "next":
                manager.choise_day(call.message, date.today() + relativedelta(months=1))
            elif data[0].isdigit():
                if int(data[0]) >= 1 and int(data[0]) <= 31:
                    manager.change_workstatus(call.message, date.fromisoformat(data[1]))
            elif data[0] == "yes":
                Manager.schedule[date.fromisoformat(data[1]).day-1] = True
                bot.delete_message(call.message.chat.id, call.message.message_id)
            elif data[0] == "no":
                Manager.schedule[date.fromisoformat(data[1]).day-1] = False
                bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(e)

# @bot.message_handler(commands=['salary'])
# def Salary(message):
#     bot.send_message(message.chat.id, "Ваша зарплата: ")

#
# @bot.message_handler()
# def worker(message):
#     if message.text == "Регистрация":
#         user_reg(message)
#     elif message.text == "Отчет":
#         report(message)
#     elif message.text == "Изменить профиль":
#         change_profile(message)
#     elif message.text == "График смен":
#         Schedule(message)
#     elif message.text == "Зарплата":
#         Salary(message)


bot.infinity_polling()
