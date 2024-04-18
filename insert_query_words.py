from class_db import DataBase, username, password


db = DataBase('english_db', user=username, password=password, host='127.0.0.1', port='5432')


db.execute_query('''INSERT INTO words (words_text) VALUES 
('Hello'),
('World'),
('Apple'),
('Banana'),
('Cat'),
('Dog'),
('Sun'),
('Moon'),
('Goodbye'),
('Ocean')''')


db.execute_query('''INSERT INTO questions (question_text) VALUES 
('Привет'),
('Мир'),
('Яблоко'),
('Банан'),
('Кот'),
('Собака'),
('Солнце'),
('Луна'),
('До свидания'),
('Океан')''')


db.execute_query('''INSERT INTO answers (question_id, answer_text, is_correct) VALUES 
(1, 'Hello', TRUE),
(1, 'Way', FALSE),
(1, 'Get', FALSE),
(1, 'Look', FALSE),
(2, 'World', TRUE),
(2, 'River', FALSE),
(2, 'Big', FALSE),
(2, 'Take', FALSE),
(3, 'Apple', TRUE),
(3, 'Give', FALSE),
(3, 'Differ', FALSE),
(3, 'Make', FALSE),
(4, 'Banana', TRUE),
(4, 'Red', FALSE),
(4, 'Car', FALSE),
(4, 'House', FALSE),
(5, 'Cat', TRUE),
(5, 'Human', FALSE),
(5, 'Bus', FALSE),
(5, 'Father', FALSE),
(6, 'Dog', TRUE),
(6, 'Son', FALSE),
(6, 'Many', FALSE),
(6, 'Like', FALSE),
(7, 'Sun', TRUE),
(7, 'Know', FALSE),
(7, 'Study', FALSE),
(7, 'City', FALSE),
(8, 'Moon', TRUE),
(8, 'Run', FALSE),
(8, 'Book', FALSE),
(8, 'Real', FALSE),
(9, 'Goodbye', TRUE),
(9, 'Mountain', FALSE),
(9, 'Idea', FALSE),
(9, 'White', FALSE),
(10, 'Ocean', TRUE),
(10, 'Next', FALSE),
(10, 'Letter', FALSE),
(10, 'Bird', FALSE)''')
