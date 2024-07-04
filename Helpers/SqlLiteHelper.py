import sqlite3
from sqlite3 import Error


class SQLiteHelper:

    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = self.create_connection()
        self.create_table()

    def create_connection(self):
        """ create a database connection to the SQLite database """
        try:
            conn = sqlite3.connect(self.db_file)
            print(f'Connected to SQLite database {self.db_file}')
        except Error as e:
            print(e)
        else:
            return conn

    def get_sgl_codes(self):
        """ Retrieve distinct sgl_unique_model_code values from Parts table """
        select_sql = 'SELECT DISTINCT sgl_unique_model_code FROM Parts'
        try:
            c = self.conn.cursor()
            c.execute(select_sql)
            data = c.fetchall()
            return [row[0] for row in data]
        except Error as e:
            print(e)

    def create_table(self):
        """ create table with specified columns """
        create_table_sql = '''CREATE TABLE IF NOT EXISTS parts (
        id INTEGER PRIMARY KEY,
        sgl_unique_model_code TEXT NOT NULL,
        section TEXT NOT NULL,
        part_number TEXT NOT NULL,
        description TEXT NOT NULL,
        item_number TEXT NOT NULL,
        section_diagram TEXT NOT NULL
        );'''
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def insert_record(self, record):
        """ insert a new record into the parts table """
        sql = 'INSERT INTO parts(sgl_unique_model_code, section, part_number, description, item_number, section_diagram) VALUES(?,?,?,?,?,?)'
        cur = self.conn.cursor()
        cur.execute(sql, (
            record['sgl_unique_model_code'], record['section'], record['part_number'], record['description'],
            record['item_number'], record['section_diagram']))
        self.conn.commit()
        return cur.lastrowid

    def insert_many_records(self, records):
        """ insert multiple records into the parts table """
        sql = 'INSERT INTO parts(sgl_unique_model_code, section, part_number, description, item_number, section_diagram) VALUES(?,?,?,?,?,?)'
        cur = self.conn.cursor()
        cur.executemany(sql, [(record['sgl_unique_model_code'], record['section'], record['part_number'],
                               record['description'], record['item_number'], record['section_diagram']) for record in
                              records])
        self.conn.commit()

    def close_connection(self):
        """ close the database connection """
        if self.conn:
            self.conn.close()
            print(f'Connection to SQLite database {self.db_file} closed')
