import logging
import os

import psycopg2


logging.basicConfig(
    filename='db.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')

db_name = os.environ.get('POSTGRES_DB')
db_user = os.environ.get('POSTGRES_USER')
db_password = os.environ.get('POSTGRES_PASSWORD')
db_host = 'db'
db_port = '5432'

connection = psycopg2.connect(
    database=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port)


def create_tables():
    connection.autocommit = True
    cursor = connection.cursor()

    query = """
    create table
    if not exists
    tasks (
    id int primary key,
    task_name varchar(255) not null,
    task varchar(255) not null,
    status varchar(32) not null,
    answer varchar(255)
    );
    """
    cursor.execute(query, connection)
