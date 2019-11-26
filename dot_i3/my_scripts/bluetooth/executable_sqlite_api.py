import sqlite3
from sqlite3 import Error
from datetime import datetime
import os


USER = os.environ["USER"]
db = "/home/" + USER + "/.i3/my_scripts/bluetooth/bluetooth.db"


def create_bluetooth_table():
    conn = create_connection(db)
    c = conn.cursor()
    c.execute("""CREATE TABLE bluetooth(date DATETIME, value TEXT)""")
    conn.close()


def drop_bluetooth_table():
    conn = create_connection(db)
    c = conn.cursor()
    c.execute("""DROP TABLE bluetooth""")
    conn.close()


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        # print(sqlite3.version)
        return conn
    except Error as e:
        print(e)


def read_bluetooth_status():
    conn = create_connection(db)

    try:
        c = conn.cursor()
        res = c.execute("SELECT * FROM bluetooth ORDER BY date DESC LIMIT 1")

        state = []
        for row in res:
            state += [row]
        print(state[0][1])
        return state[0][1]

    finally:
        conn.close()


def update_bluetooth_status(connected=True):
    conn = create_connection(db)

    status = '' if connected else ''
    try:
        c = conn.cursor()
        c.execute('insert into bluetooth values (?,?)', (datetime.now(), status))
        conn.commit()
    finally:
        conn.close()
