import telebot
from datetime import datetime
from telebot import types
import config

# импортируем токен tg-бота
TOKEN = config.API_token
bot = telebot.TeleBot(TOKEN)

sleep_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,f'Привет! Я буду помогать тебе отслеживать параметры сна!\n\n' 
                              f'Используй команды:\n \n/sleep - время засыпания \n/wake - время подъема'
                              f'\n/quality - оценить сон \n/notes - записать заметки')

@bot.message_handler(commands=['sleep'])
def sleep_start(message):
    user_id = message.from_user.id
    sleep_data[user_id] = {'start_time': datetime.now()}
    bot.reply_to(message, 'Спокойной ночи! Не забудь сообщить мне, когда проснешься командой /wake')


@bot.message_handler(commands=['wake'])
def sleep_end(message):
    user_id = message.from_user.id
    if user_id not in sleep_data:
        bot.reply_to(message, 'Я не вижу, что ты сообщил мне о начале сна')
    else:
        sleep_time = sleep_data[user_id]['start_time']
        awake_time = datetime.now()
        sleep_duration = awake_time - sleep_time
        hours_slept = round(sleep_duration.total_seconds() / 3600, 3)
        sleep_data[user_id]['duration'] = hours_slept
        bot.reply_to(message, f'Доброе утро! Ты проспал около {hours_slept} часов.\n\n\n'
                                    f'Что-бы записать данные о качестве сна нажми /quality')

@bot.message_handler(commands=['quality'])
def sleep_quality(message):
    # Добавляем кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # добавляю кнопки для оценки качества сна
    button1 = types.KeyboardButton('😍')
    button2 = types.KeyboardButton('😌')
    button3 = types.KeyboardButton('🥱')
    button4 = types.KeyboardButton('😩')
    button5 = types.KeyboardButton('😑')
    bot.reply_to(message, f'Оцени качество твоего сна => \n \n \n Отправь свою оценку:'
                                f'\n 5 - 😍 Выспался и полон сил \n 4 - 😌 Спалось хорошо'
                                f'\n 3 - 🥱 Чашка кофе мне не помешает \n 2 - 😩 Ну такое себе'
                                f'\n 1 - 😑 Я точно не жаворонок!')

    markup.add(button1, button2, button3, button4, button5)
    bot.send_message(message.chat.id, 'Выбери оценку для описания своего сна:', reply_markup= markup)

    @bot.message_handler(content_types=["text"])
    def sleep_text(message):
        a = types.ReplyKeyboardRemove()
        # Действия при нажатии на кнопки
        dict_answer = {'😍': 5,
                       '😌': 4,
                       '🥱': 3,
                       '😩': 2,
                       '😑': 1}
        # узнаем id-пользователя
        user_id = message.from_user.id
        if message.text in dict_answer.keys():
            # записываем в наш словарь новый словарь grade и заносим туда оценки по дням
            sleep_data[user_id]['grade'] = dict_answer[message.text]
            bot.send_message(message.chat.id, f'Спасибо! Данные успешно записаны)\n\n\n'
                                               f'Если хочешь внести заметки о своем сне нажми /notes', reply_markup=a)
        else:
            # записываем в наш словарь новый словарь grade и заносим туда оценки по дням
            sleep_data[user_id]['notes'] = message.text
            bot.send_message(message.chat.id, f'Отлично! Заметки о твоем сне успешно записаны!\n\n'
                                              f'Не забывай вечером записать время засыпания командой /sleep')



@bot.message_handler(commands=["notes"])
def sleep_notes(message):
    bot.send_message(message.chat.id, f'Запиши заметку о сегодняшнем качестве сна\n\n'
                                      f'Например: снились кошмары, спалось отлично, всю ночь просыпался')


bot.polling()

print(sleep_data)

'''Часть 2. Заносим данные в БД'''

import psycopg2

try:
    # пытаемся подключиться к базе данных
    connection = psycopg2.connect(dbname='postgres',
                                  user='postgres',
                                  password='postgres',
                                  host="localhost")

    connection.autocommit = True

    # создаю таблицу для записи id каждого подзователя
    #with connection.cursor() as cursor:
    #    cursor.execute(
    #        """CREATE TABLE users(
    #            id_user serial PRIMARY KEY,
    #            id_tg INT);"""
    #    )

    #    print("[INFO] Table created successfully")

    # delete a table
    #with connection.cursor() as cursor:
    #    cursor.execute(
    #        """DROP TABLE users;"""
    #    )

    #    print("[INFO] Table was deleted")

    # создаю таблицу для записи данных каждого пользователя
    #with connection.cursor() as cursor:
    #    cursor.execute(
    #        """CREATE TABLE info_users(
    #            info_id serial PRIMARY KEY,
    #            start_time DATE,
    #            duration DECIMAL(8,2),
    #            grade INT,
    #            notes VARCHAR(300),
    #            id_user INT NOT NULL,
    #            FOREIGN KEY (id_user) REFERENCES users (id_user) ON DELETE CASCADE);"""
    #    )

    #    print("[INFO] Table created successfully")

    # находим всех пользователей приложения
    users = list(sleep_data.keys())

    # создаем для каждого пользователя свой id
    for user in users:
        user_db = (str(user),)
        # добавляю записи в БД users
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO users (id_tg)
                VALUES (%s);""", user_db
            )

            print("[INFO] Data USERS was succefully inserted")

        # находим данные по пользователю user
        recording_day = str(sleep_data[user]['start_time']).split()[0]
        duration = sleep_data[user]['duration']
        grade = sleep_data[user].get('grade', '')
        notes = sleep_data[user].get('notes', '')

        # записываю данные по пользователю user в таблицу info_users
        cursor = connection.cursor()
        cursor.execute("""SELECT id_user FROM users WHERE id_tg = (%s);""", user_db)
        id_user_db = cursor.fetchone()

        values = (recording_day, duration, grade, notes, id_user_db)

        cursor.execute("""INSERT INTO info_users (start_time, duration, grade, notes, id_user)
                VALUES (%s, %s, %s, %s, %s);""", values)

        print("[INFO] Data INFO_USERS was succefully inserted")


except Exception as _ex:
    print("[INFO] Error while working with PostgreSQL", _ex)
finally:
    if connection:
        connection.close()
        print("[INFO] PostgreSQL connection closed")


