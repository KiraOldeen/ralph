import datetime
import json
import os
import re

from bot import Bot
from database import Database
from keyboard import Keyboards
from scheduler import Date
from scheduler import Schedule
from students import students

db = Database(os.environ["DATABASE_URL"])
bot = Bot()
kbs = Keyboards()

for event in bot.longpoll.listen():
    bot.event = event
    if (
        bot.event.type == bot.NEW_MESSAGE
        and bot.event.object.text
        and bot.event.object.out == 0
        and bot.event.object.from_id == bot.event.object.peer_id
    ):
        if not db.is_user_exist(bot.event.object.from_id):
            db.create_user(bot.event.object.from_id)
        if not db.is_session_exist(bot.event.object.from_id):
            db.create_session(bot.event.object.from_id)
        try:
            payload = json.loads(bot.event.object.payload)
        except TypeError:
            payload = {"button": ""}
        text = bot.event.object.text.lower()
        if text in ["начать", "старт"]:
            bot.send_gui()
        elif payload["button"] == "letter":
            bot.send_message(
                msg=f"Отправка клавиатуры с фамилиями на букву \"{payload['letter']}\"",
                pid=bot.event.object.from_id,
                keyboard=kbs.generate_names_keyboard(payload["letter"]),
            )
        elif payload["button"] == "student":
            db.append_to_call_ids(bot.event.object.from_id, db.get_vk_id(payload["id"]))
            bot.send_message(
                msg=f"{payload['name']} добавлен к списку призыва.",
                pid=bot.event.object.from_id,
            )
        elif payload["button"] == "back":
            bot.send_message(
                msg="Отправка клавиатуры с алфавитом.",
                pid=bot.event.object.from_id,
                keyboard=kbs.generate_alphabet_keyboard(),
            )
        elif payload["button"] == "call":
            db.update_session_state(bot.event.object.from_id, "ask_for_call_message")
            if not db.call_session_exist(bot.event.object.from_id):
                db.create_call_session(bot.event.object.from_id)
            bot.send_message(
                msg="Отправьте сообщение к призыву (вложения не поддерживаются)",
                pid=bot.event.object.from_id,
                keyboard=kbs.skip(),
            )
        elif payload["button"] == "skip":
            db.update_session_state(bot.event.object.from_id, "call_configuring")
            bot.send_message(
                msg="Отправка клавиатуры с алфавитом.",
                pid=bot.event.object.from_id,
                keyboard=kbs.generate_alphabet_keyboard(),
            )
        elif payload["button"] == "send_to_all":
            ids = ",".join(list(students.keys()))
            db.update_call_ids(bot.event.object.from_id, ids)
            bot.send_message(
                msg="Все студенты отмечены как получатели уведомления. Готово к "
                'отправке, нажмите "Сохранить"',
                pid=bot.event.object.from_id,
            )
        elif (
            payload["button"] == "confirm"
            and db.get_session_state(bot.event.object.from_id) == "call_configuring"
        ):
            bot.log.log.info("Отправка призыва...")
            cid = db.get_conversation(bot.event.object.from_id)
            text = db.get_call_message(bot.event.object.from_id)
            bot.send_message(pid=cid, msg=text)
            db.empty_call_storage(bot.event.object.from_id)
            db.update_session_state(bot.event.object.from_id, "main")
            bot.send_gui(text="Сообщение отправлено.")
        elif payload["button"] == "deny":
            db.update_call_message(bot.event.object.from_id, " ")
            db.update_call_ids(bot.event.object.from_id, " ")
            db.update_session_state(bot.event.object.from_id, "main")
            bot.send_gui(text="Выполнение команды отменено.")
        elif payload["button"] == "debtors":
            bot.send_message(
                msg="Выберите статью расходов (колонку в таблице)",
                pid=bot.event.object.from_id,
                keyboard=open(
                    f"keyboards/select_col.json", "r", encoding="UTF-8"
                ).read(),
            )
        elif payload["button"] == "col_id":
            bot.col = payload["id"]
            bot.get_debtors()
        elif payload["button"] == "schedule":
            bot.send_message(
                msg="Отправка клавиатуры с расписанием.",
                pid=bot.event.object.from_id,
                keyboard=kbs.generate_schedule_keyboard(),
            )
        elif payload["button"] == "today":
            d = Date()
            s = Schedule(d.today)
            schedule = s.get()
            bot.send_message(msg=schedule, pid=bot.event.object.from_id)
        elif payload["button"] == "tomorrow":
            d = Date()
            s = Schedule(d.tomorrow)
            schedule = s.get()
            bot.send_message(msg=schedule, pid=bot.event.object.from_id)
        elif payload["button"] == "day_after_tomorrow":
            d = Date()
            s = Schedule(d.day_after_tomorrow)
            schedule = s.get()
            bot.send_message(msg=schedule, pid=bot.event.object.from_id)
        elif payload["button"] == "arbitrary":
            bot.send_message(
                msg="Напишите дату в формате ДД-ММ-ГГГГ.",
                pid=bot.event.object.from_id,
                keyboard=kbs.cancel(),
            )
            db.update_session_state(bot.event.object.from_id, "ask_for_schedule_date")
        elif payload["button"] == "chconv":
            bot.change_conversation()
        elif payload["button"] == "cancel":
            db.empty_call_storage(bot.event.object.from_id)
            db.update_session_state(bot.event.object.from_id, "main")
            bot.send_gui("Выполнение команды отменено.")
        elif payload["button"] == "cancel_sch":
            db.update_session_state(bot.event.object.from_id, "main")
            bot.send_message(
                msg="Выполнение команды отменено.",
                pid=bot.event.object.from_id,
                keyboard=kbs.generate_schedule_keyboard(),
            )
        elif payload["button"] == "save":
            bot.send_message(
                msg=f"В {'тестовую ' if bot.cid.endswith('1') else 'основную '}"
                f"беседу будет отправлено сообщение:",
                pid=bot.event.object.from_id,
                keyboard=kbs.prompt(),
            )
            f = False
            text = (
                f"{bot.generate_mentions(ids=db.get_call_ids(bot.event.object.from_id), names=f)}\n"
                f"{db.get_call_message(bot.event.object.from_id)}"
            )
            db.update_call_message(bot.event.object.from_id, text)
            bot.show_msg(text)
        elif payload["button"] == "newsletters":
            bot.send_message(
                msg="Отправка клавиатуры со списком рассылок.",
                pid=bot.event.object.from_id,
                keyboard=kbs.generate_mailings_keyboard(),
            )
        elif payload["button"] == "mailing":
            bot.send_message(
                msg=f"Меню управления рассылкой \"{payload['name']}\":",
                pid=bot.event.object.from_id,
                keyboard=kbs.generate_mailing_mgmt(
                    is_admin=bot.current_is_admin(),
                    slug=payload["slug"],
                    user_id=bot.event.object.from_id,
                ),
            )
        elif payload["button"] == "subscribe":
            db.query(
                f"UPDATE vk_subscriptions SET {payload['slug']}=1 WHERE "
                f"user_id={payload['user_id']}"
            )
            bot.send_message(
                msg="Вы были успешно подписаны на рассылку.",
                pid=bot.event.object.from_id,
                keyboard=kbs.generate_mailing_mgmt(
                    is_admin=bot.current_is_admin(),
                    slug=payload["slug"],
                    user_id=bot.event.object.from_id,
                ),
            )
        elif payload["button"] == "unsubscribe":
            db.query(
                f"UPDATE vk_subscriptions SET {payload['slug']}=0 WHERE "
                f"user_id={payload['user_id']}"
            )
            bot.send_message(
                msg="Вы были успешно отписаны от рассылки.",
                pid=bot.event.object.from_id,
                keyboard=kbs.generate_mailing_mgmt(
                    is_admin=bot.current_is_admin(),
                    slug=payload["slug"],
                    user_id=bot.event.object.from_id,
                ),
            )
        elif payload["button"] == "home":
            bot.send_gui(text="Главный экран")
        elif db.get_session_state(bot.event.object.from_id) == "ask_for_call_message":
            db.update_call_message(bot.event.object.from_id, bot.event.object.text)
            bot.send_message(
                msg="Отправка клавиатуры призыва",
                pid=bot.event.object.from_id,
                keyboard=kbs.generate_alphabet_keyboard(),
            )
            db.update_session_state(bot.event.object.from_id, "call_configuring")
        elif db.get_session_state(bot.event.object.from_id) == "ask_for_schedule_date":
            if re.match(r"^\d\d(.|-|/)\d\d(.|-|/)20\d\d$", bot.event.object.text):
                try:
                    d = datetime.datetime.strptime(
                        bot.event.object.text, "%d-%m-%Y"
                    ).strftime("%Y-%m-%d")
                except ValueError:
                    bot.send_message(
                        msg="Неверный формат даты. Попробуйте еще раз.",
                        pid=bot.event.object.from_id,
                    )
                else:
                    s = Schedule(d)
                    schedule = s.get()
                    keyboard = ""
                    if schedule != "Расписание отсутствует.":
                        keyboard = kbs.generate_schedule_keyboard()
                        db.update_session_state(bot.event.object.from_id, "main")
                    else:
                        schedule += "\nПопробуй указать другую дату."
                        db.update_session_state(
                            bot.event.object.from_id, "ask_for_schedule_date"
                        )
                    bot.send_message(
                        msg=schedule, pid=bot.event.object.from_id, keyboard=keyboard,
                    )
            else:
                bot.send_message(
                    msg="Неверный формат даты. Попробуйте еще раз.",
                    pid=bot.event.object.from_id,
                )
