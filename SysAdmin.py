import telebot
import Hasher
import BDWorker
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


class SysAdmin:
    bot: telebot = None

    def __init__(self, _bot: telebot):
        self.bot = _bot

    def get_sys_admin_func(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        items = []
        for i in self.func.keys():
            items.append(KeyboardButton(i))
        markup.add(*items)
        return markup

    def add_user_handler(self, message):
        self.bot.send_message(message.chat.id, "Введите фамилию и имя нового пользователя (например, Иван Иванов):")
        self.bot.register_next_step_handler(message, self.add_user_name)

    def add_user_name(self, message):
        full_name = message.text.strip()
        chat_id = message.chat.id
        markup = ReplyKeyboardMarkup(row_width=2)
        item1 = KeyboardButton("Обычный")
        item2 = KeyboardButton("Золотой")
        item3 = KeyboardButton("Платиновый")
        item4 = KeyboardButton("Управляющий")
        markup.add(item1, item2, item3, item4)
        self.bot.send_message(chat_id, "Выберите тип оператора:", reply_markup=markup)
        self.bot.register_next_step_handler(message, lambda msg: self.add_user_operator(msg, full_name, chat_id))

    def add_user_operator(self, message, full_name, chat_id):
        operator_type = message.text.strip()
        if operator_type not in {"Обычный", "Золотой", "Платиновый", "Управляющий"}:
            self.bot.send_message(chat_id, "Неверный тип оператора. Попробуйте снова.")
            return
        try:
            hashed_key = self.register_user(full_name, operator_type, None)
            self.bot.send_message(chat_id,
                                  f"Регистрация нового пользователя завершена. Его уникальный ключ: {hashed_key}.")
            self.show_admin_buttons(chat_id)

        except Exception as e:
            self.bot.send_message(chat_id, f"Произошла ошибка при регистрации: {e}")

    def register_new_user(self, message):
        full_name = message.text.strip()
        chat_id = message.chat.id
        markup = ReplyKeyboardMarkup(row_width=2)
        item1 = KeyboardButton("Обычный")
        item2 = KeyboardButton("Золотой")
        item3 = KeyboardButton("Платиновый")
        item4 = KeyboardButton("Управляющий")
        markup.add(item1, item2, item3, item4)
        self.bot.send_message(chat_id, "Выберите тип оператора:", reply_markup=markup)
        self.bot.register_next_step_handler(message, lambda msg: self.add_user_operator(msg, full_name, chat_id))

    def register_user(self, full_name, operator_type, chat_id):
        hashed_key = Hasher.generate_unique_key()[1]
        BDWorker.Add_User(full_name, operator_type, chat_id, hashed_key)
        return hashed_key

    def show_admin_buttons(self, chat_id):
        markup = self.get_sys_admin_func()
        self.bot.send_message(chat_id, "Выберите опцию администратора:", reply_markup=markup)

    func = {
        "Добавить пользователя": lambda self, msg: self.add_user_handler(msg)
    }

    def msg_handler(self, msg):
        self.func[msg.text](self, msg)
