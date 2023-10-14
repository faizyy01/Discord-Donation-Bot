import sqlite3
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)
log_formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(message)s')
log_file_handler = logging.FileHandler(filename=f'{__name__}.log',mode='a')
log_file_handler.setFormatter(log_formatter)
logger.addHandler(log_file_handler)


DB_URL = os.getcwd() + '/Email/payrecs.db'

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        logger.debug('Connected to db')
    except Exception as e:
        logger.error(f'There was an error connecting to the database below is the exception: \n\n {e}\n\n__________________________________')
    finally:
        if conn:
            return conn

def checkTableExists(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute("""SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{0}';""".format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True
    dbcur.close()
    return False

conn = create_connection(DB_URL)

# Checking if table exists
if checkTableExists(conn, 'USERS'):
    print('Table exists.')
else:
    conn.execute('''
    CREATE TABLE "USERS" (
    "id"	INTEGER,
    "discord_username"	TEXT,
    "email"	TEXT,
    PRIMARY KEY("id" AUTOINCREMENT)
    );
    ''')

def save_user(username, email):
    if username and email:
        conn.execute("INSERT INTO USERS (discord_username, email) VALUES ('"+ username +"', '" + email +  "')")
        conn.commit()
        print("User added to db.")
    else:
        return "Username or email cannot be empty"

def read_useremail():
    cur = conn.cursor()
    cur.execute("SELECT * FROM USERS")
    rows = cur.fetchall()
    all = []
    for row in rows:
        all.append(row)
    return all