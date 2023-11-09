import telebot
from datetime import datetime
from telebot import types


bot = telebot.TeleBot('TOKEN')

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
        hours_slept = sleep_duration.total_seconds() / 3600
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
        # находим ключ для записи оценки
        # ключ - сегодняшняя дата без времени
        data_n = datetime.now()
        date_only = data_n.date()
        if message.text == '😍' or message.text == '😌' or message.text == '🥱' or message.text == '😩' or message.text == '😑':
            # записываем в наш словарь новый словарь grade и заносим туда оценки по дням
            sleep_data[user_id]['grade'] = {date_only: dict_answer[message.text]}
            bot.send_message(message.chat.id, f'Спасибо! Данные успешно записаны)\n\n\n'
                                               f'Если хочешь внести заметки о своем сне нажми /notes', reply_markup=a)
        else:
            # записываем в наш словарь новый словарь grade и заносим туда оценки по дням
            sleep_data[user_id]['notes'] = {date_only: []}
            sleep_data[user_id]['notes'][date_only].append(message.text)
            bot.send_message(message.chat.id, f'Отлично! Заметки о твоем сне успешно записаны!\n\n'
                                              f'Не забывай вечером записать время засыпания командой /sleep')



@bot.message_handler(commands=["notes"])
def sleep_notes(message):
    bot.send_message(message.chat.id, f'Запиши заметку о сегодняшнем качестве сна\n\n'
                                      f'Например: снились кошмары, спалось отлично, всю ночь просыпался')


bot.polling()

print(sleep_data)
