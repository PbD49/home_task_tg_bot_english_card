import configparser
import random

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from class_db import DataBase, username, password
from translate_words import translate_text_rus_to_eng

db = DataBase('english_db', user=username, password=password, host='127.0.0.1', port='5432')

config = configparser.ConfigParser()
config.read("settings.ini")

username = config["name"]["username"]
password = config["password"]["password"]
token = config["token"]["token"]


class StartBot:
    """
    Родительский класс для запуска бота.

    :param token: Токен для API телеграм.
    Методы
    -------
    init(token)
    Инициализирует объект StartBot с токеном.
    start_handler(message)
    send_message_with_buttons(self, message, text)
    """
    def __init__(self, token):
        """
        Инициализация бота.

        :param token: Токен бота для API Telegram.
        """
        self.bot = telebot.TeleBot(token)

        @self.bot.message_handler(commands=['start'])
        def start_handler(message):
            """
            Обработчик команды '/start'.

            Обрабатывает команду "/start" и отправляет приветственное сообщение пользователю.

            :param message: Объект сообщения.
            """
            photo = open('1.jpeg', 'rb')
            self.bot.send_photo(message.chat.id, photo)
            text = ('''Привет! Я твой умный помощник в изучении английского языка по словам. 
Давай вместе улучшать свой словарный запас и достигать новых высот в изучении иностранного языка! 
Готов начать? 😉📚''')
            self.send_message_with_buttons(message, text)

    def send_message_with_buttons(self, message, text):
        """
        Отправка сообщения с пользовательской клавиатурой, содержащей различные варианты.

        :param message: Объект сообщения.
        :param text: Текст, который будет отправлен вместе с пользовательской клавиатурой.
        """
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Начать тренировку 🎮')
        keyboard.add('Посмотреть список изучаемых слов 💼')
        keyboard.add('Добавить новое слово ➕')
        keyboard.add('Удалить слово ❌')
        self.bot.send_message(message.chat.id, text, reply_markup=keyboard)


class StartGame(StartBot):
    """
    Класс StartGame для обработки начала игры перевода слов.

    """
    def __init__(self, token):
        """
        Инициализация класса StartGame токеном.

        :param token: Токен, используемый для авторизации бота.
        """
        super().__init__(token)

        @self.bot.message_handler(func=lambda message: message.text == 'Начать тренировку 🎮')
        def start_game(message):
            """
            Обработчик начала тренировки.

            Обрабатывает команду "Начать тренировку" и начинает игру для пользователя.

            :param message: Объект сообщения.
            """
            user_id = message.from_user.id
            used_questions = db.fetch_all('''SELECT DISTINCT question_id FROM used_questions''')
            if len(used_questions) >= 10:
                common_words(message, user_id)
            query = db.fetch_one(
                '''SELECT question_id,  question_text 
                          FROM questions 
                          WHERE user_id = %s OR user_id IS NULL
                          ORDER BY RANDOM()''',
                (user_id,))
            if query:
                question_text = query[1]
                question_id = query[0]
                while question_id in [q[0] for q in used_questions]:
                    query = db.fetch_one(
                        '''SELECT question_id, question_text 
                                  FROM questions 
                                  WHERE user_id = %s OR user_id IS NULL
                                  ORDER BY RANDOM()''',
                        (user_id,))
                    if query:
                        question_text = query[1]
                        question_id = query[0]

                db.execute_query(
                    '''INSERT INTO used_questions (question_id, user_id) 
                              VALUES (%s, %s)''',
                    (question_id, user_id)
                )

                all_answers(user_id, question_text, question_id)

        def all_answers(user_id, question_text, question_id):
            """
            Обработчик отправки всех вариантов ответа.

            Отправляет пользователю все варианты ответа на текущий вопрос.

            :param user_id: идентификатор пользователя.
            :param question_text: Текст вопроса.
            :param question_id: идентификатор вопроса.
            """
            answers = db.fetch_all(
                '''SELECT answer_text
                          FROM answers 
                          WHERE question_id = %s''',
                (question_id,)
            )

            random.shuffle(answers)
            send_results_with_buttons(user_id, answers, question_text, question_id)

        def send_results_with_buttons(user_id, answers, question_text, question_id):
            """
            Обработчик отправки результатов с кнопками.

            Отправляет пользователю сообщение с вариантами ответа в виде кнопок.

            :param user_id: идентификатор пользователя.
            :param answers: Варианты ответа.
            :param question_text: Текст вопроса.
            :param question_id: идентификатор вопроса.
            """
            markup = InlineKeyboardMarkup(row_width=1)
            for answer in answers:
                answer_text = answer[0]
                btn = InlineKeyboardButton(text=answer_text, callback_data=f'answer_{answer_text}_{question_id}')
                markup.add(btn)
            reply = f'''⏳ <b>Как переводится слово:</b>
                             \n\n{question_text}\n\nЕсли сомнений нет - нажмите на кнопку: 📨'''
            self.bot.send_message(user_id, reply, reply_markup=markup, parse_mode='HTML')

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('answer'))
        def check_answer(call):
            """
            Обработчик проверки ответа.

            Проверяет правильность ответа пользователя и отправляет соответствующее сообщение.

            :param call: Вызов обратного вызова.
            """
            user_id = call.message.chat.id
            chosen_answer = call.data.split('_')[1]
            question_id = call.data.split('_')[2]
            correct_answer = db.fetch_one(
                '''SELECT answer_text 
                          FROM answers 
                          WHERE question_id = %s 
                          AND answer_text = %s 
                          AND is_correct = true 
                          AND (user_id = %s OR user_id IS NULL)''',
                (question_id, chosen_answer, user_id,))
            if correct_answer:
                self.bot.send_message(call.message.chat.id, text='<b>Ответ правильный. Поздравляю!</b>',
                                      parse_mode='HTML')
                start_game(call)
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                self.bot.send_message(call.message.chat.id, text='<b>Ответ неправильный. Попробуйте еще раз.</b>',
                                      parse_mode='HTML')

        def common_words(message, user_id):
            """
            Обработчик сброса списка использованных вопросов.

            Сбрасывает список использованных вопросов для пользователя, чтобы он мог начать новую игру.

            :param message: Объект сообщения.
            :param user_id: идентификатор пользователя.
            """
            db.execute_query(
                '''DELETE FROM used_questions 
                   WHERE user_id = %s''',
                (user_id,)
            )
            start_game(message)


class ListWords(StartBot):
    """
    Класс для представления списка слов.

    ...

    Атрибуты
    ----------
    token: str
    токен, используемый для авторизации

    Методы
    -------
    init(token)
    Инициализирует объект ListWords с токеном.
    list_words(message)
    Функция для обработки списка слов для пользователя.
    """
    def __init__(self, token):
        """
        Инициализирует объект ListWords предоставленным токеном.

        Параметры:
        token (str): строковый токен для авторизации.
        """
        super().__init__(token)

        @self.bot.message_handler(func=lambda message: message.text == 'Посмотреть список изучаемых слов 💼')
        def list_words(message):
            """
            Функция для обработки списка слов на основе ввода пользователя.

            Параметры:
            message : Message
            Объект сообщения, который вызвал вызов функции.
            """
            chat_id = message.chat.id
            query = db.fetch_all('''SELECT DISTINCT q.question_text 
                                           FROM questions q 
                                           WHERE user_id = %s OR user_id IS NULL;''',
                                 (chat_id,))

            if query:
                words = [row[0] for row in query]
                wordslist = '\n'.join([f"{i}. {word}" for i, word in enumerate(words, start=1)])
                reply = f'<b>Список изучаемых слов:</b> 🪧\n\n{wordslist}'
                self.bot.send_message(chat_id, reply, parse_mode='HTML')
            else:
                reply = '<b>В настоящий момент у вас нет добавленных слов.</b>'
                self.bot.send_message(chat_id, reply, parse_mode='HTML')


class AddWord(StartBot):
    """
    Класс для представления добавления слова.

    ...

    Атрибуты
    ----------
    token: str
    токен, используемый для авторизации

    Методы
    -------
    init(token)
    Инициализирует объект AddWord с токеном.
    send_message_for_add_word(message)
    Отправляет сообщение для добавления нового слова.
    add_word(message)
    Добавляет новое слово в базу данных.
    add_wrong_answer(message, add_word, translated_text_eng)
    Добавляет неправильные ответы для нового слова.
    """
    def __init__(self, token):
        """
        Инициализирует объект AddWord предоставленным токеном.

        Параметры:
        token (str): строковый токен для авторизации.
        """
        super().__init__(token)

        @self.bot.message_handler(func=lambda message: message.text == 'Добавить новое слово ➕')
        def send_message_for_add_word(message):
            """
            Отправляет сообщение для добавления нового слова.

            Параметры:
            message : Message
            Объект сообщения, который вызвал вызов функции.
            """
            reply = 'Напишите новое слово:'
            self.bot.send_message(message.from_user.id, reply)
            self.bot.register_next_step_handler(message, self.add_word)

    def add_word(self, message):
        """
        Добавляет новое слово в базу данных.

        Параметры:
        message : Message
        Объект сообщения, который вызвал вызов функции.
        """
        chat_id = message.from_user.id
        add_word = message.text
        translated_text_eng = translate_text_rus_to_eng(add_word)
        question_exists = db.fetch_one(
            '''SELECT question_text
                      FROM questions 
                      WHERE question_text = %s 
                      AND (user_id = %s OR user_id IS NULL)''',
            (add_word, chat_id,))
        if not question_exists:
            db.execute_query('''INSERT INTO questions (question_text, user_id) 
                                       VALUES (%s, %s);''',
                             (add_word, chat_id,))
            self.add_wrong_answer(message, add_word, translated_text_eng)
        else:
            reply = '<b>Такое слово уже есть в базе данных. Попробуйте добавить другое слово.</b>'
            self.bot.send_message(message.from_user.id, reply, parse_mode='HTML')

    def add_wrong_answer(self, message, add_word, translated_text_eng):
        """
        Добавляет неправильные ответы для нового слова.

        Параметры:
        message : Message
        Объект сообщения, который вызвал вызов функции.
        add_word: str
        Новое слово, которое добавляется.
        translated_text_eng: str
        Переведенный текст нового слова на английский язык.
        """
        chat_id = message.from_user.id
        question_id = db.fetch_one('''SELECT question_id 
                                             FROM questions 
                                             WHERE question_text = %s 
                                             AND (user_id = %s OR user_id IS NULL);''',
                                   (add_word, chat_id))[0]

        bad_words = db.fetch_all('''SELECT words_text FROM words ORDER BY RANDOM() LIMIT 3''')

        bad_words.append(translated_text_eng)

        for wrong_word in bad_words:
            is_correct = wrong_word == translated_text_eng
            db.execute_query(
                '''INSERT INTO answers (question_id, answer_text, is_correct, user_id) 
                          VALUES (%s, %s, %s, %s);''',
                (question_id, wrong_word, is_correct, chat_id,)
            )

        reply = '<b>Новое слово успешно добавлено.</b>'
        self.bot.send_message(message.from_user.id, reply, parse_mode='HTML')
        photo = open('2.jpeg', 'rb')
        self.bot.send_photo(message.chat.id, photo)


class DeleteWord(StartBot):
    """
    Класс DeleteWord для обработки удаления слов из базы данных.
    """
    def __init__(self, token):
        """
        Конструктор для класса DeleteWord.

        Параметры:
        token (str): Токен API Telegram.
        """
        super().__init__(token)

        @self.bot.message_handler(func=lambda message: message.text == 'Удалить слово ❌')
        def delete_word(message):
            """
            Функция-обработчик для удаления слова на основе ввода пользователя.

            Параметры:
            message (Telegram message): Входное сообщение от пользователя.
            """
            user_id = message.from_user.id
            query = db.fetch_all('''SELECT DISTINCT q.question_text 
                                           FROM questions q
                                           WHERE user_id = %s;''', (user_id,))
            if query:
                words = [row[0] for row in query]
                markup = InlineKeyboardMarkup()
                for word in words:
                    btn = InlineKeyboardButton(text=word, callback_data=f'delete_{word}')
                    markup.add(btn)
                reply = f'<b>Выберите слово, чтобы удалить:</b> 🗑'
                self.bot.send_message(message.from_user.id, reply, reply_markup=markup, parse_mode='HTML')
            else:
                reply = '<b>В настоящий момент у вас нет добавленных слов.</b>'
                self.bot.send_message(message.from_user.id, reply, parse_mode='HTML')

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('delete'))
        def delete_word(call):
            """
            Функция обратного вызова для удаления выбранного слова.

            Параметры:
            call (Telegram callback): Данные обратного вызова для выбранного слова.
            """
            user_id = call.from_user.id
            word_id = call.data.split('_')[1]
            db.execute_query('''DELETE
                                FROM
                                answers
                                WHERE
                                question_id
                                IN
                                (SELECT question_id
                                FROM questions
                                WHERE question_text ILIKE '%{}%' AND user_id = '{}')'''.format(word_id, user_id))

            db.execute_query('''DELETE
                                FROM
                                questions
                                WHERE
                                question_id
                                IN
                                (SELECT question_id
                                FROM questions
                                WHERE question_text ILIKE '%{}%' AND user_id = '{}')'''.format(word_id, user_id))

            self.bot.send_message(user_id, '<b>Выбранное слово удалено!</b>', parse_mode='HTML')
            self.bot.delete_message(call.message.chat.id, call.message.message_id)


class BotRunner(ListWords, DeleteWord, AddWord, StartGame, StartBot):
    """
    Этот класс отвечает за запуск бота и выполнение различных операций, таких как:
    * вывод списка слов
    * удаление слов
    * добавление слов
    * начало игры
    * запуск бота
    """
    def __init__(self, token):
        """
        Инициализация объекта BotRunner указанным токеном.

        :param token: Токен для доступа к боту.
        """
        super().__init__(token)

    def run(self):
        """
        Запустить бота для постоянной работы.

        Этот метод опрашивает бота и обрабатывает любые исключения, возникшие в процессе опроса.
        """
        while True:
            try:
                self.bot.polling(none_stop=True)
            except Exception as e:
                print(f'Ошибка: {e}')
                continue


bot = BotRunner(token)
bot.run()
