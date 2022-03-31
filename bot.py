from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram, vk_api
import logging, time, os, random
from threading import Thread
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlite3
from oauth2client.client import GoogleCredentials
import dialogflow_v2 as dialogflow
import handler_tools
from handler_tools import MyLogsHandler

# Функция echo телеграм
def echo_tg(bot, update):
    chat_id = update.message.chat_id
    user_message = update.message.text
    try:
        bot_answer = handler_tools.detect_intent_texts(handler_tools.project_id, chat_id, user_message, 'ru-RU')
        update.message.reply_text(bot_answer)
    except Exception:
        logger.exception("Проблема при получении и отправке сообщений в телеграм")

# Функция echo ВК
def echo_vk(event, vk_api):
    user_id = event.user_id
    user_message = event.text
    
    try:
        message = handler_tools.detect_intent_texts(handler_tools.project_id, event.user_id, user_message, 'ru-RU')
        # отправляем пользователя в базу
        adddb(event.user_id, 'VK', '', '')
        if message is not None:
            vk_api.messages.send(
                user_id=event.user_id,
                message=message,
                random_id=random.randint(1,1000000000)
            )
    except Exception:
        logger.exception("Проблема при получении и отправке сообщений в ВК")

# Функция старта для телеги    
def start(bot, update):
    update.message.reply_text('Привет! Я школьный бот. Чтобы узнать что я умею, спроси "Что ты умеешь?"')
    # отправляем пользователя в базу
    adddb(update.message.from_user.id, 'TG', '', '');

# Бот ВК
def vk():
    try:
        logger.info("Бот VK запущен")
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                echo_vk(event, vk_api)
        
    except Exception:
        logger.exception('Возникла ошибка в боте ВК ↓')

# Бот телеграм
def tg():
    try:        
        logger.info("Бот TG запущен")

        updater = Updater(handler_tools.telegram_token)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))

        echo_handler = MessageHandler (Filters.text, echo_tg)
        dp.add_handler(echo_handler)

        updater.start_polling()
        updater.idle()

    except Exception:
        logger.exception('Возникла ошибка в боте Телеграм ↓')

# рассылка
def send():
    m = 1
    while m < 10:
        print("> ", end="")
        answer = input()
        bot = telegram.Bot(token=handler_tools.telegram_token)
        # ищем пользователей ТГ
        sql = "SELECT user_id FROM users WHERE messenger='TG'"
        result = searchuser(sql)
        # рассылка ТГ
        for row in result:
            if row[0] != None:
                try:
                    bot.send_message(chat_id=row[0], text=answer)
                except Exception:
                    logger.exception("Проблема при получении и отправке сообщений в телеграм")
        # ищем пользователей ВК
        sql = "SELECT user_id FROM users WHERE messenger='VK'"
        result = searchuser(sql)
        # рассылка ВК
        for row in result:
            if row[0] != None:
                try:
                    vk_api.messages.send(peer_id=row[0], message=answer, random_id=random.randint(1,1000000000))
                except Exception:
                    logger.exception("Проблема при получении и отправке сообщений в ВК")

# добавляем/обновляем пользователя в БД        
def searchuser(sql):
    try:
        # поключаемся к базе
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        # отправляем запрос
        cursor.execute(sql)
        result = cursor.fetchall()
    except sqlite3.DatabaseError as err:       
        logger.info(err)
    else:
        conn.commit()
    return result

# добавляем/обновляем пользователя
def adddb(user, messenger, name, school_class):
    # ищем пользователя
    sql = "SELECT user_id FROM users WHERE user_id=:user"
    result = adduser(sql, user, messenger, name, school_class)
    if result == None:
        # добавляем пользователя
        sql = "INSERT INTO users VALUES (:user, :messenger, :name, :school_class)"
        adduser(sql, user, messenger, name, school_class)
    else:
        if name != '':
            sql = "UPDATE users SET name = :name WHERE user_id = :user"
        if school_class !='':
            sql = "UPDATE users SET class = :school_class WHERE user_id = :user"
        adduser(sql, result[0], messenger, name, school_class)

# добавляем/обновляем пользователя в БД        
def adduser(sql, user, messenger, name, school_class):
    try:
        # поключаемся к базе
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        # отправляем запрос
        cursor.execute(sql, {"user": user, "messenger": messenger, "name": name, "school_class": school_class})
        result = cursor.fetchone()
    except sqlite3.DatabaseError as err:       
        logger.info("Error: ", err)
    else:
        conn.commit()
    return result

# Main
if __name__ == '__main__': 
	# Запуск логгер  
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(MyLogsHandler())
    vk_session = vk_api.VkApi(token=handler_tools.vk_community_token)
    vk_api = vk_session.get_api()
    print('Стартуем бота, можно вводить сообщения для рассылки ниже')
    # Запускаем бот ВК
    thread = Thread(target=vk, args=())
    thread.start()
    # Запускаем input
    thread_input = Thread(target=send, args=())
    thread_input.start()
    # Запускаем бот телеграм
    tg()