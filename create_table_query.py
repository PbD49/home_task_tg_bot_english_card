from class_db import DataBase, username, password


db = DataBase('english_db', user=username, password=password, host='127.0.0.1', port='5432')


db.execute_query('''DROP TABLE IF EXISTS 
                    words, questions,
                    answers, used_questions
''')

db.execute_query('''CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    words_text TEXT NOT NULL
)''')

db.execute_query('''CREATE TABLE questions (
    question_id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    user_id BIGINT
)''')

db.execute_query('''CREATE TABLE answers (
    answer_id SERIAL PRIMARY KEY,
    question_id SERIAL REFERENCES questions(question_id),
    answer_text TEXT NOT NULL,
    is_correct BOOLEAN,
    user_id BIGINT
)''')

db.execute_query('''CREATE TABLE used_questions (
    id SERIAL PRIMARY KEY,
    question_id INTEGER UNIQUE,
    user_id BIGINT
)''')
