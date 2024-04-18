import psycopg2
import configparser


config = configparser.ConfigParser()
config.read("settings.ini")


class DataBase:
    """
    Класс для работы с базой данных.

    ...

    Атрибуты
    ----------
    db_name: str
        Название базы данных.
    user: str
        Имя пользователя базы данных.
    password: str
        Пароль пользователя базы данных.
    host: str
        Хост базы данных.
    port: str
        Порт базы данных.
    connection: psycopg2.connection
        Объект соединения с базой данных.
    cursor: psycopg2.cursor
        Объект курсора для выполнения запросов.
    """

    def __init__(self, db_name, user, password, host, port):
        """
        Инициализация объекта базы данных.

        Параметры
        ----------
        db_name: str
            Название базы данных.
        user: str
            Имя пользователя базы данных.
        password: str
            Пароль пользователя базы данных.
        host: str
            Хост базы данных.
        port: str
            Порт базы данных.
        """
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Устанавливает соединение с базой данных.
        """
        self.connection = psycopg2.connect(dbname=self.db_name, user=self.user,
                                           password=self.password, host=self.host, port=self.port)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        """
        Закрывает соединение с базой данных.
        """
        if self.connection:
            self.cursor.close()
            self.connection.close()

    def execute_query(self, query, params=None):
        """
        Выполняет SQL-запрос и фиксирует изменения.

        Параметры
        ----------
        query: str
            SQL-запрос.
        params: tuple, optional
            Кортеж с параметрами для запроса.
        """
        self.connect()
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.connection.commit()
        self.disconnect()

    def fetch_all(self, query, params=None):
        """
        Выполняет SQL-запрос и возвращает все полученные строки.

        Параметры
        ----------
        query: str
            SQL-запрос.
        params: tuple, optional
            Кортеж с параметрами для запроса.

        Возвращает
        -------
        list
            Список кортежей с данными.
        """
        self.connect()
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.disconnect()
        return result

    def fetch_one(self, query, params=None):
        """
        Выполняет SQL-запрос и возвращает первую полученную строку.

        Параметры
        ----------
        query: str
            SQL-запрос.
        params: tuple, optional
            Кортеж с параметрами для запроса.

        Возвращает
        -------
        tuple
            Кортеж с данными.
        """
        self.connect()
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        result = self.cursor.fetchone()
        self.disconnect()
        return result


username = config["name"]["username"]
password = config["password"]["password"]
db = DataBase('english_db', user=username, password=password, host='127.0.0.1', port='5432')
db.connect()
