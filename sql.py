from faker import Faker
import sqlite3
import random

fake = Faker()

conn = sqlite3.connect("Database.db", check_same_thread=False)

cursor = conn.cursor()

def create_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        first_name TEXT,
        last_name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        admin BOOLEAN,
        is_active BOOLEAN,
        fighter BOOLEAN,
        id INTEGER PRIMARY KEY AUTOINCREMENT
        )
    ''')

    # for _ in range(20):
    #     cursor.execute('''
    #                 INSERT INTO users (first_name, last_name, email, password, admin, is_active)
    #                 VALUES (?, ?, ?, ?, ?, ?)
    #                 ''', (
    #                     fake.first_name(),
    #                     fake.last_name(),
    #                     fake.email(),
    #                     fake.password(),
    #                     random.randint(1, 12) // 10,
    #                     1,
    #                 ))
        
    conn.commit()
        

create_table()


def registration(first_name, last_name, email, password, password_2):
    if "@" not in email or "." not in email:
        print("Неверный адрес электронной почты")
        return
    elif password != password_2:
        print("Пароли не совпадают")
        return

    try:
        cursor.execute('''
                       INSERT INTO users (first_name, last_name, email, password, admin, is_active, fighter)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (first_name,
                               last_name,
                               email,
                               password,
                               0,
                               1,
                               0)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: users.email" in str(e):
            print("Пользователь с таким email уже зарегистрирован")
        else:
            print(f"Ошибка целостности\n{e}")

def login(email, password):
    cursor.execute('''
                  SELECT * FROM users WHERE email = ? AND password = ?  
                    ''',
                    (email,
                      password)
        )
    user = cursor.fetchone()
    if user:
        print("Логин произошёл")
    else:
        print("нет такого пользователя")