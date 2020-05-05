import os

from vk_api.keyboard import VkKeyboard

from database import Database


class Keyboards:
    """
    Класс с генераторами пользовательских клавиатур
    """

    def __init__(self):
        self.db = Database(os.environ["DATABASE_URL"])

    @staticmethod
    def generate_main_menu(is_admin: bool):
        """
        Генерирует клавиатуру с главным меню
        """
        kb = VkKeyboard()
        if is_admin:
            kb.add_button(label="Призыв", payload={"button": "call"})
            kb.add_button(label="Финансы", payload={"button": "finances"})
            kb.add_line()
        kb.add_button(label="Расписание", payload={"button": "schedule"})
        kb.add_line()
        kb.add_button(
            label="Управление рассылками", payload={"button": "mailings"},
        )
        if is_admin:
            kb.add_line()
            kb.add_button(label="Настройки", payload={"button": "prefs"})
            kb.add_button(label="Веб", payload={"button": "web"})
        return kb.get_keyboard()

    @staticmethod
    def generate_schedule_keyboard():
        """
        Возвращает клавиатуру с выбором даты получения расписания
        """
        kb = VkKeyboard()
        kb.add_button(label="На сегодня", payload={"button": "today"})
        kb.add_button(label="На завтра", payload={"button": "tomorrow"})
        kb.add_line()
        kb.add_button(
            label="На послезавтра", payload={"button": "day_after_tomorrow"},
        )
        kb.add_button(
            label="Выбрать дату", payload={"button": "arbitrary"},
        )
        kb.add_line()
        kb.add_button(
            label="Назад", payload={"button": "home"},
        )
        return kb.get_keyboard()

    @staticmethod
    def empty():
        """
        Возвращает пустую клавиатуру
        """
        kb = VkKeyboard()
        return kb.get_empty_keyboard()

    @staticmethod
    def skip():
        """
        Возвращает клавиатуру с кнопкой "Пропустить"
        """
        kb = VkKeyboard()
        kb.add_button(label="Пропустить", payload={"button": "skip"})
        return kb.get_keyboard()

    @staticmethod
    def cancel():
        """
        Возвращает клавиатуру с кнопкой "Отмена"
        """
        kb = VkKeyboard()
        kb.add_button(label="Отмена", payload={"button": "cancel"})
        return kb.get_keyboard()

    @staticmethod
    def generate_prefs_keyboard():
        """
        Возвращает клавиатуру с настройками бота
        """
        kb = VkKeyboard()
        kb.add_button(label="Чаты", payload={"button": "chats"})
        kb.add_line()
        kb.add_button(label="Использование имён в призыве", payload={"button": "names"})
        kb.add_line()
        kb.add_button(
            label="Назад", payload={"button": "home"},
        )
        return kb.get_keyboard()

    @staticmethod
    def generate_chat_prefs():
        kb = VkKeyboard()
        kb.add_button(
            label="Глобальные настройки чатов", payload={"button": "global_chat"}
        )
        kb.add_line()
        kb.add_button(
            label="Локальные настройки чатов", payload={"button": "local_chat"}
        )
        kb.add_line()
        kb.add_button(
            label="Назад", payload={"button": "prefs"},
        )
        return kb.get_keyboard()

    @staticmethod
    def generate_local_chat_prefs(chat):
        kb = VkKeyboard()
        if chat:
            kb.add_button(
                label="Переключиться на тестовую беседу",
                payload={"button": "activate_test_chat"},
            )
        else:
            kb.add_button(
                label="Переключиться на основную беседу",
                payload={"button": "activate_main_chat"},
            )
        kb.add_line()
        kb.add_button(label="Назад", payload={"button": "chats"})
        return kb.get_keyboard()

    def generate_global_chat_prefs(self, group: int):
        kb = VkKeyboard()
        chats = self.db.get_chats_of_group(group)
        for i, v in enumerate(chats):
            if len(kb.lines[-1]) == 2:
                kb.add_line()
            if v[1]:
                kb.add_button(
                    label="Основная беседа",
                    payload={
                        "button": "configure_chat",
                        "group": group,
                        "chat_type": 1,
                        "chat_id": v[0],
                    },
                )
            else:
                kb.add_button(
                    label="Тестовая беседа",
                    payload={
                        "button": "configure_chat",
                        "group": group,
                        "chat_type": 0,
                        "chat_id": v[0],
                    },
                )
        if len(chats) < 2 and self.db.get_cached_chats():
            kb.add_button(label="Зарегистрировать чат", payload={"button": "reg_chat"})
        kb.add_line()
        kb.add_button(label="Назад", payload={"button": "chats"})
        return kb.get_keyboard()

    @staticmethod
    def reg_chat(chats, chats_info):
        kb = VkKeyboard()
        for i, v in enumerate(chats):
            if chats_info["items"]:
                kb.add_button(
                    label=chats_info["items"][0]["chat_settings"]["title"],
                    payload={"button": "add_chat", "chat_id": v},
                )
            else:
                kb.add_button(label="???", payload={"button": "add_chat", "chat_id": v})
            if len(kb.lines[-1]) == 2:
                kb.add_line()
        if kb.lines[-1]:
            kb.add_line()
        kb.add_button(label="Назад", payload={"button": "global_chat"})
        return kb.get_keyboard()

    def configure_chat(self, group: int, chat_type: int):
        kb = VkKeyboard()
        if not self.db.is_chat_active(group, chat_type):
            kb.add_button(
                label="Активировать",
                payload={
                    "button": "activate_chat",
                    "group": group,
                    "chat_type": chat_type,
                },
            )
        if kb.lines[-1]:
            kb.add_line()
        kb.add_button(label="Назад", payload={"button": "global_chat"})
        return kb.get_keyboard()

    def generate_available_chat_types(self, chat_id: int, group: int):
        kb = VkKeyboard()
        if not self.db.is_main_chat_added(group):
            kb.add_button(
                label="Основной", payload={"button": "reg_as_main", "chat_id": chat_id}
            )
        if not self.db.is_test_chat_added(group):
            kb.add_button(
                label="Тестовый", payload={"button": "reg_as_test", "chat_id": chat_id}
            )
        kb.add_line()
        kb.add_button(label="Назад", payload={"button": "reg_chat"})
        return kb.get_keyboard()

    @staticmethod
    def generate_names_selector(status: bool):
        kb = VkKeyboard()
        if status:
            kb.add_button(label="Выключить", payload={"button": "off_using_names"})
        else:
            kb.add_button(label="Включить", payload={"button": "on_using_names"})
        kb.add_line()
        kb.add_button(
            label="Назад", payload={"button": "prefs"},
        )
        return kb.get_keyboard()

    @staticmethod
    def fin_category_menu():
        kb = VkKeyboard()
        kb.add_button(label="📈 Доход", payload={"button": "add_donate"})
        kb.add_button(label="📉 Расход", payload={"button": "add_expense"})
        kb.add_line()
        kb.add_button(label="Статистика", payload={"button": "fin_stat"})
        kb.add_line()
        kb.add_button(label="📢 Должники", payload={"button": "debtors"})
        kb.add_button(label="⚙ Настройки", payload={"button": "fin_prefs"})
        kb.add_line()
        kb.add_button(label="👈🏻 Назад", payload={"button": "finances"})
        return kb.get_keyboard()

    @staticmethod
    def fin_prefs():
        kb = VkKeyboard()
        kb.add_button(label="Изменить сумму", payload={"button": "update_summ"})
        kb.add_button(label="Переименовать", payload={"button": "update_name"})
        kb.add_line()
        kb.add_button(label="Удалить", payload={"button": "delete_expense"})
        kb.add_line()
        kb.add_button(
            label="Назад", payload={"button": "fin_category"},
        )
        return kb.get_keyboard()

    @staticmethod
    def inline_unsubscribe(m_id, sub_id):
        kb = VkKeyboard(inline=True)
        kb.add_button(
            label="Отписаться от таких сообщений",
            payload={"button": "inline_unsubscribe", "slug": m_id, "user_id": sub_id},
        )
        return kb.get_keyboard()

    def generate_call_prompt(self, group: int):
        kb = self.generate_alphabet_keyboard(group)
        kb.add_line()
        kb.add_button(label="Отмена", payload={"button": "cancel"})
        kb.add_button(label="Сохранить", payload={"button": "save"})
        kb.add_line()
        kb.add_button(label="Отправить всем", payload={"button": "send_to_all"})
        return kb.get_keyboard()

    def generate_finances_prompt(self, group):
        kb = self.generate_alphabet_keyboard(group)
        kb.add_line()
        kb.add_button(label="Отмена", payload={"button": "cancel"})
        return kb.get_keyboard()

    def generate_alphabet_keyboard(self, group: int):
        """
        Генерирует клавиатуру с алфавитными кнопками
        """
        kb = VkKeyboard()
        letters = self.db.get_last_names_letters(group)
        for i, v in enumerate(letters):
            if len(kb.lines[-1]) < 4:
                kb.add_button(label=v, payload={"button": "letter", "letter": v})
            else:
                kb.add_line()
                kb.add_button(label=v, payload={"button": "letter", "letter": v})

        return kb

    def generate_names_keyboard(self, letter: str, group: int):
        """
        Генерирует клавиатуру с фамилиями, начинающимися на букву (аргумент)
        """
        names = self.db.get_list_of_names(letter=letter, group=group)
        kb = VkKeyboard()
        for i, v in enumerate(names):
            label = f"{v[2]} {v[1][0]}."
            kb.add_button(
                label=label, payload={"button": "student", "name": label, "id": v[0]},
            )
            if len(kb.lines[-1]) == 2:
                kb.add_line()
        if kb.lines[-1]:
            kb.add_line()
        kb.add_button(
            label="Назад", payload={"button": "back"},
        )
        return kb.get_keyboard()

    def generate_mailings_keyboard(self, group: int):
        """
        Генерация клавиатуры со списком доступных рассылок
        """
        mailings = self.db.get_mailings_list(group)
        kb = VkKeyboard()
        for i, v in enumerate(mailings):
            kb.add_button(
                label=v[1], payload={"button": "mailing", "name": v[1], "id": v[0]},
            )
            if len(kb.lines[-1]) == 2:
                kb.add_line()
        if kb.lines[-1]:
            kb.add_line()
        kb.add_button(
            label="Назад", payload={"button": "home"},
        )
        return kb.get_keyboard()

    def generate_mailing_mgmt(self, user_id: int, is_admin: bool, m_id: int):
        uid = self.db.get_user_id(vk_id=user_id)
        status = self.db.get_subscription_status(m_id=m_id, user_id=uid)

        kb = VkKeyboard()
        if is_admin:
            kb.add_button(
                label="Отправить рассылку",
                payload={"button": "send_mailing", "mailing": m_id},
            )
        kb.add_button(
            label=f"{'Отписаться' if status else 'Подписаться'}",
            payload={
                "button": f"{'unsubscribe' if status else 'subscribe'}",
                "slug": m_id,
                "user_id": uid,
            },
        )
        kb.add_line()
        kb.add_button(
            label="Назад", payload={"button": "mailings"},
        )
        return kb.get_keyboard()

    def prompt(self, user_id: int = None):
        """
        Возвращает клавиатуру с подтверждением действия
        """
        kb = VkKeyboard()
        kb.add_button(label="Подтвердить", payload={"button": "confirm"})
        kb.add_button(label="Отмена", payload={"button": "deny"})
        if user_id is not None and self.db.get_session_state(user_id) in [
            "call_configuring",
            "debtors_forming",
        ]:
            kb.add_line()
            kb.add_button(
                label="Сменить беседу", payload={"button": "chconv_call"},
            )
            kb.add_line()
            kb.add_button(
                label="Переключить использование имён",
                payload={"button": "chnames_call"},
            )
        return kb.get_keyboard()

    def finances_main(self, group: int):
        kb = VkKeyboard()
        list_of_cats = self.db.get_list_of_finances_categories(group)
        for i, v in enumerate(list_of_cats):
            label = v[1]
            kb.add_button(
                label=label,
                payload={"button": "fin_category", "id": v[0], "name": v[1]},
            )
            if len(kb.lines[-1]) == 2:
                kb.add_line()
        if kb.lines[-1]:
            kb.add_line()
        kb.add_button(label="Баланс", payload={"button": "balance"})
        kb.add_button(label="Добавить статью", payload={"button": "add_expense_cat"})
        kb.add_line()
        kb.add_button(label="Назад", payload={"button": "home"})
        return kb.get_keyboard()

    def generate_administrating_groups(self, admin_id):
        kb = VkKeyboard()
        groups = self.db.get_administrating_groups(admin_id)
        for i, v in enumerate(groups):
            label = v
            kb.add_button(
                label=label, payload={"button": "get_auth_link", "group": v},
            )
            if len(kb.lines[-1]) == 2:
                kb.add_line()
        if kb.lines[-1]:
            kb.add_line()
        kb.add_button(label="Назад", payload={"button": "home"})
        return kb.get_keyboard()
