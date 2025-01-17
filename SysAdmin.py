import telebot
from telebot import types
import openpyxl
from io import BytesIO
import Hasher
import BDWorker
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InputFile

callback_id='sadmin'

class SysAdmin:
    bot: telebot = None

    def __init__(self, _bot: telebot):
        self.bot = _bot
        self.page_size = 5
        self.current_employee_index = 0
        self.employees_list = BDWorker.get_all_users()

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
            thai_key = self.register_user(full_name, operator_type, None)
            self.bot.send_message(chat_id,
                                  f"Регистрация нового пользователя завершена. Его уникальный ключ: {thai_key}.")
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
        thai_key = Hasher.generate_unique_key()
        BDWorker.Add_User(full_name, operator_type, chat_id, thai_key)
        return thai_key

    def show_admin_buttons(self, chat_id):
        markup = self.get_sys_admin_func()
        self.bot.send_message(chat_id, "Выберите опцию администратора:", reply_markup=markup)

    def view_all_employees_handler(self, message):
        chat_id = message.chat.id
        users = BDWorker.get_all_users()

        markup = types.InlineKeyboardMarkup()
        for user in users:
            user_id, full_name, post_name, hour_rate = user
            markup.add(
                types.InlineKeyboardButton(text=f"{full_name} ({post_name})", callback_data=f"{callback_id}-view_user-{user_id}"))

        markup.add(types.InlineKeyboardButton(text="Назад", callback_data=f"{callback_id}-back_to_admin"))
        self.bot.send_message(chat_id, "Выберите сотрудника для просмотра информации:", reply_markup=markup)

    def handle_user_info(self, call, user_id):
        user_info = BDWorker.get_user_info_by_id(user_id)

        if user_info:
            full_name, post_name, hour_rate = user_info

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="👤 ФИО: " + full_name, callback_data="dummy"))
            markup.add(types.InlineKeyboardButton(text="📋 Должность: " + post_name, callback_data="dummy"))
            markup.add(
                types.InlineKeyboardButton(text="💰 Часовая ставка: " + str(hour_rate) + "₽", callback_data="dummy"))



            markup.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"{callback_id}-back_to_admin"))

            self.bot.send_message(call.message.chat.id,
                                  "🧑‍💼 **Информация о пользователе:**",
                                  reply_markup=markup,
                                  parse_mode='Markdown')
        else:
            self.bot.send_message(call.message.chat.id, "❌ Пользователь не найден.")
            self.view_all_employees_handler(call.message)

    def create_excel_handler(self, message):
        excel_file = self.create_excel_file()

        excel_file.seek(0)


        uploaded_file = InputFile(excel_file, 'Сотрудники.xlsx')

        self.bot.send_document(
            message.chat.id,
            uploaded_file,
            caption="Список сотрудников"
        )

    def create_excel_file(self):
        users = BDWorker.get_all_users()
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Сотрудники"


        sheet.append(["ID", "Имя", "Должность", "Часовая ставка"])


        for user in users:
            if len(user) == 4:
                user_id, full_name, post_name, hour_rate = user
                sheet.append([user_id, full_name, post_name, hour_rate])
            else:
                print("Ошибка: неверное количество данных для пользователя:", user)


        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)

        return excel_file

    def display_employee_details(self, msg):
        chat_id = msg.chat.id
        total_employees = len(self.employees_list)

        if total_employees == 0:
            self.bot.send_message(chat_id, "Нет сотрудников для отображения.")
            return

        start_index = self.current_employee_index * self.page_size
        end_index = start_index + self.page_size
        current_employees = self.employees_list[start_index:end_index]

        if not current_employees:
            self.bot.send_message(chat_id, "Ошибка: нет данных о сотрудниках на этой странице.")
            return

        markup = types.InlineKeyboardMarkup()
        for employee in current_employees:
            if len(employee) >= 4:
                user_id, full_name, post_name, hour_rate = employee[:4]
                markup.add(
                    types.InlineKeyboardButton(text=f"{full_name}", callback_data=f"{callback_id}-edit_name-{user_id}"),
                    types.InlineKeyboardButton(text=f"{post_name}", callback_data=f"{callback_id}-edit_role-{user_id}"),
                    types.InlineKeyboardButton(text=f"{hour_rate}₽", callback_data="dummy"),
                )
        items = []
        if self.current_employee_index > 0:
            items.append(types.InlineKeyboardButton("◀️", callback_data=f"{callback_id}-prev"))

        items.append(types.InlineKeyboardButton("❌", callback_data=f"{callback_id}-back_to_admin"))

        if end_index < total_employees:
            items.append(types.InlineKeyboardButton("▶️", callback_data=f"{callback_id}-next"))

        markup.add(*items)

        message = self.bot.send_message(chat_id, "🧑‍💼 Информация о сотрудниках:", reply_markup=markup)
        self.last_message_id = message.message_id

    func = {
        "Добавить пользователя": lambda self, msg: self.add_user_handler(msg),
        "Просмотр всех сотрудников": lambda self, msg: self.view_all_employees_handler(msg),
        "Создать Excel": lambda self, msg: self.create_excel_handler(msg),
        "Редактировать сотрудников": lambda self, msg: self.display_employee_details(msg)
        }

    def callback_handler(self, call):
        data = call.data.split(sep="-")[1:]
        if data[0] == "view_all_employees":
            self.view_all_employees_handler(call.message)
        elif data[0] == "view_user":
            user_id = int(data[1])
            self.handle_user_info(call, user_id)
        elif data[0] == "back_to_admin":
            self.show_admin_buttons(call.message.chat.id)
        elif data[0] == "create_excel":
            self.create_excel_handler(call.message)
        elif data[0] == "prev":
            if self.current_employee_index > 0:
                self.current_employee_index -= 1
                self.display_employee_details(call.message)
        elif data[0] == "next":
            if (self.current_employee_index + 1) * self.page_size < len(self.employees_list):
                self.current_employee_index += 1
                self.display_employee_details(call.message)
        elif data[0] == "edit_name":
            user_id = int(data[1])
            self.prompt_new_name(call.message, user_id)
        elif data[0] == "edit_role":
            user_id = int(data[1])
            self.prompt_select_role(call.message, user_id)
        elif data[0] == "update_role":
            user_id = int(data[1])
            new_role_id = int(data[2])
            BDWorker.update_employee_role_in_db(user_id, new_role_id)
            new_hour_rate = BDWorker.get_hour_rate_by_role(new_role_id)
            self.bot.send_message(call.message.chat.id,
                                  f"Роль обновлена на: {new_role_id}. Часовая ставка теперь: {new_hour_rate}₽.")
            self.display_employee_details(call.message)

    def prompt_new_name(self, message, user_id):
        self.bot.send_message(message.chat.id, "Введите новое ФИО оператора:")
        self.bot.register_next_step_handler(message, self.update_employee_name, user_id)

    def update_employee_name(self, message, user_id):
        new_name = message.text
        BDWorker.update_employee_name_in_db(user_id, new_name)
        self.bot.send_message(message.chat.id, f"Имя обновлено на: {new_name}!")
        self.display_employee_details(message)

    def prompt_select_role(self, message, user_id):
        roles = BDWorker.get_available_roles()
        markup = types.InlineKeyboardMarkup()
        for role in roles:
            role_id, role_name = role
            markup.add(types.InlineKeyboardButton(text=role_name, callback_data=f"{callback_id}-update_role-{user_id}-{role_id}"))

        self.bot.send_message(message.chat.id, "Выберите новую роль оператора:", reply_markup=markup)

    def callback_handler_update_role(self, call):
        _, user_id, new_role = call.data.split('-')
        new_hour_rate = BDWorker.get_hour_rate_by_role(new_role)
        BDWorker.update_employee_role_in_db(user_id, new_role, new_hour_rate)
        self.bot.send_message(call.message.chat.id,
                              f"Роль обновлена на: {new_role}. Часовая ставка теперь: {new_hour_rate}₽.")
        self.display_employee_details(call.message)
    def msg_handler(self, msg):
        self.func[msg.text](self, msg)

