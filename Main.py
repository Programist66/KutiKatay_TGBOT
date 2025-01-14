import bcrypt as bcrypt

import BDWorker
import Config
import Manager

from telebot import TeleBot
from telebot import types

from datetime import date
from dateutil.relativedelta import relativedelta

import SysAdmin

bot = TeleBot(Config.TOKEN)

manager = Manager.Manager(bot)
sysAdmin = SysAdmin.SysAdmin(bot)


def show_buttons(chat_id, operator_type):
    markup = None
    if operator_type in ("Обычный", "Золотой", "Платиновый"):
        item1 = types.KeyboardButton("Заполнить график")
        markup.add(item1)
    elif operator_type == "Управляющий":
        markup = manager.Get_Manager_btn()
    bot.send_message(chat_id, "Выберите опцию:", reply_markup=markup)


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id

    if BDWorker.have_TG_id(chat_id):
        show_main_menu(chat_id)
    else:
        bot.send_message(message.chat.id, "Введите уникальный ключ:")
        bot.register_next_step_handler(message, check_key)


def show_main_menu(chat_id):
    markup = None
    operator_type = BDWorker.get_operator_type_by_id(chat_id)
    if operator_type == "Обычный":
        item1 = types.KeyboardButton("Заполнить график")
        markup.add(item1)
    elif operator_type == "Золотой":
        item1 = types.KeyboardButton("Заполнить график")
        item2 = types.KeyboardButton("Доступ к дополнительным ресурсам")
        markup.add(item1, item2)
    elif operator_type == "Платиновый":
        item1 = types.KeyboardButton("Заполнить график")
        item2 = types.KeyboardButton("Доступ к дополнительным ресурсам")
        item3 = types.KeyboardButton("Обратная связь с руководством")
        markup.add(item1, item2, item3)
    elif operator_type == "Управляющий":
        markup = manager.Get_Manager_btn()

    bot.send_message(chat_id, "Выберите опцию:", reply_markup=markup)


def check_key(message):
    chat_id = message.chat.id
    user_input = message.text.strip()

    if user_input == Config.SYS_ADMIN_KEY:
        bot.send_message(chat_id, "Добро пожаловать, Сисадмин!")
        sysAdmin.show_admin_buttons(chat_id)
        return
    else:
        operator_type = BDWorker.get_operator_by_uid(user_input)
        if operator_type is not None:
            BDWorker.update_user_chat_id_by_UID(user_input, chat_id)
            bot.send_message(chat_id, "Ключ принят!")
            show_buttons(chat_id, operator_type)
        else:
            bot.send_message(chat_id, "Неверный ключ или пользователь не найден. Попробуйте еще раз:")
            bot.register_next_step_handler(message, check_key)





@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call : types.CallbackQuery):
    try:
        if call.message:
            data = call.data.split(sep="-")
            if data[0] == Manager.callback_id:
                manager.callback_handler(call)
            if data[0] == SysAdmin.callback_id:
                sysAdmin.callback_handler(call)

    except Exception as e:
        print(e)


@bot.message_handler()
def message_handler(message : types.Message):
    try:
        operator_type = BDWorker.get_operator_type_by_id(message.chat.id)
        if operator_type in ("Обычный", "Золотой", "Платиновый"):
            pass
        elif operator_type == "Управляющий":
            if message.text in manager.func.keys():
                manager.msg_handler(message)
            else:
                bot.send_message(message.chat.id, "Неизвестная комманда")
        else:
            if message.text in sysAdmin.func.keys():
                sysAdmin.msg_handler(message)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    BDWorker.Create_all_tables()
    bot.polling(none_stop=True)
