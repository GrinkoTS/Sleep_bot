'''Часть 2. Заносим данные в google-таблицу'''

import gspread
import config

filename='google_token.json'
my_key = config.my_key

class Google_sheets:
    def __init__(self, filename, my_key):
        self.filename = filename
        self.my_key = my_key

    def connection_google(self):
        # подключаемся к сервисному аккаунту
        self.SERVICE = gspread.service_account(self.filename)
        # открываем документ
        self.SHEET = self.SERVICE.open_by_key(self.my_key)

    def old_users(self):
        Google_sheets.connection_google(self)
        # находим список пользователей, который уже есть в нашем документе
        self.old_users = []
        worksheet_list = self.SHEET.worksheets()
        for element in worksheet_list:
            self.old_users.append(element.title)
        return self.old_users

my_google = Google_sheets(filename, my_key)
print(my_google.old_users())

# находим пользователей приложения
users = list(sleep_data.keys())
# создаем для каждого пользователя свой лист
for user in users:
    if str(user) not in my_google.old_users():
        # добавляем заголовки
        header_row = ['Дата', 'Продолжительность', 'Оценка', 'Заметки']
        WORKSHEET = SHEET.add_worksheet(title=f'{user}', rows=1, cols=len(header_row))
        WORKSHEET.insert_row(header_row)
        # редактируем заголовок
        WORKSHEET.format('A1:D1', {'textFormat': {'bold': True}})
    else:
        WORKSHEET = SHEET.worksheet(f'{user}')
    # заносим данные по пользователям в таблицы
    recording_day = str(sleep_data[user]['start_time']).split()[0]
    duration = sleep_data[user]['duration']
    grade = sleep_data[user].get('grade', '')
    notes = sleep_data[user].get('notes', '')
    WORKSHEET.insert_row([recording_day, duration, grade, notes], 2)