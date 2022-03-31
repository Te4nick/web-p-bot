import sqlite3
 
conn = sqlite3.connect("users.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()
 
# Создание таблицы
cursor.execute("""CREATE TABLE users
                  (user_id text, messenger text, name text, class text)
               """)