from create_tables import connection


connection = create_tables.connection
connection.autocommit = True
cursor = connection.cursor()


def add_task(name, task):
    query = f"""
    insert into tasks
    (task_name, task, status)
    values
    ('{name}', '{task}', 'в очереди');
    """
    cursor.execute(query, connection)


def get_task_list():
    query = "select * from tasks;"
    cursor.execute(query, connection)
    rows = cursor.fetchall()
