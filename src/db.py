from os import environ as env
import json
import psycopg2
from psycopg2.extras import RealDictCursor

db_host = env.get("DB_HOST")
db_user = env.get("DB_USER")
db_pass = env.get("DB_PASS")
db_name = env.get("DB_NAME")

class DB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=db_host, database=db_name, user=db_user, password=db_pass,
        )
        self.cur = self.conn.cursor()

    def cursor(self):
        return self.cur

    def conn(self):
        return self.conn

    def close(self):
        if self.conn:
            self.cur.close()
            self.conn.close()

