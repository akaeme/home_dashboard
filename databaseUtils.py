import sqlite3

def connection():
    try:
        con = sqlite3.connect('home_dashboard.db')
    except sqlite3.Error as error:
        print(error)
    else:
        return con

