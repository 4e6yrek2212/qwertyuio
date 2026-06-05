import sqlite3
from datetime import datetime
import csv

def init_db():
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute('''Drop table if exists books''')
    cur.execute('''Drop table if exists readers''')
    cur.execute('''Drop table if exists loans''')   
    cur.execute('''create table if not exists books
                   (id INTEGER PRIMARY KEY, title TEXT, author TEXT, available INTEGER)''')
    cur.execute('''create table if not exists readers
                   (id INTEGER PRIMARY KEY, name TEXT)''')
    cur.execute('''create table if not exists loans
                   (id INTEGER PRIMARY KEY, book_id INTEGER, reader_id INTEGER, 
                    loan_date TEXT, return_date TEXT, 
                    FOREIGN KEY(book_id) REFERENCES books(id),
                    FOREIGN KEY(reader_id) REFERENCES readers(id))''')
    conn.commit()
    return conn

def add_book(conn):
    title = input("Название: ")
    author = input("Автор: ")
    conn.execute("INSERT INTO books (title, author, available) VALUES (?, ?, 1)", (title, author))
    conn.commit()
    print("Книга добавлена")

def list_books(conn):
    books = conn.execute("SELECT * FROM books").fetchall()
    for i in books:
        status = "доступна" if i[3] else "выдана"
        print(f"{i[0]}. {i[1]} - {i[2]} - {status}")

def add_reader(conn):
    name = input("Имя читателя: ")
    conn.execute("INSERT INTO readers (name) VALUES (?)", (name,))
    conn.commit()
    print("Читатель добавлен")

def list_readers(conn):
    readers = conn.execute("SELECT * FROM readers").fetchall()
    for x in readers:
        print(f"{x[0]}. {x[1]}")

def issue_book(conn):
    list_books(conn)
    book_id = int(input("ID книги: "))
    book = conn.execute("SELECT available FROM books WHERE id=?", (book_id,)).fetchone()
    if not book or book[0] == 0:
        print("Книга недоступна")
        return
    list_readers(conn)
    reader_id = int(input("ID читателя: "))
    loan_date = datetime.now().strftime("%Y-%m-%d")
    conn.execute("UPDATE books SET available=0 WHERE id=?", (book_id,))
    conn.execute("INSERT INTO loans (book_id, reader_id, loan_date) VALUES (?, ?, ?)", (book_id, reader_id, loan_date))
    conn.commit()
    print("Книга выдана")

def return_book(conn):
    reader_id = int(input("ID читателя: "))
    loans = conn.execute("SELECT loans.id, books.title FROM loans JOIN books ON loans.book_id=books.id WHERE loans.reader_id=? AND loans.return_date IS NULL", (reader_id,)).fetchall()
    if not loans:
        print("Нет задолженностей")
        return
    for l in loans:
        print(f"{l[0]}. {l[1]}")
    loan_id = int(input("ID выдачи: "))
    return_date = datetime.now().strftime("%Y-%m-%d")
    loan = conn.execute("SELECT book_id FROM loans WHERE id=?", (loan_id,)).fetchone()
    conn.execute("UPDATE loans SET return_date=? WHERE id=?", (return_date, loan_id))
    conn.execute("UPDATE books SET available=1 WHERE id=?", (loan[0],))
    conn.commit()
    print("Книга возвращена")

def reports(conn):
    total = conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM loans WHERE return_date IS NULL").fetchone()[0]
    print(f"Всего выдач: {total}, сейчас на руках: {active}")

def export_text(conn):
    with open("export_data", "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "title", "author"])
        writer.writerows(conn.execute("SELECT id, title, author FROM books").fetchall())

def menu():
    conn = init_db()
    command = None
    while command != 9:
        command = int(input(
                "\n"
                "1.Добавить книгу\n"
                "2.Просмотреть доступные книги\n"
                "3.Добавить читателя\n"
                "4.Просмотреть читателей\n"
                "5.Выдача книги\n"
                "6.Вернуть книгу\n"
                "7.Отчёт\n"
                "8.Экспорт\n"
                "9.Выход\n"
                "Выберите команду: "))
        if command == 1:
            add_book(conn)
        elif command == 2:
            list_books(conn)
        elif command == 3:
            add_reader(conn)
        elif command == 4:
            list_readers(conn)
        elif command == 5:
            issue_book(conn)
        elif command == 6:
            return_book(conn)
        elif command == 7:
            reports(conn)
        elif command == 8:
            export_text(conn)
    conn.close()
menu()
