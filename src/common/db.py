import logging

from . import create_tables


connection = create_tables.connection
connection.autocommit = True
cursor = connection.cursor()


def add_task(name, task):
    query = """
    select count(id) from tasks;
    """
    cursor.execute(query, connection)
    rows = cursor.fetchall()

    id_task = rows[0][0] + 1
    query = f"""
    insert into tasks
    (id, task_name, task, status)
    values
    ({id_task}, '{name}', '{task}', 'в очереди');
    """
    cursor.execute(query, connection)
    return id_task


def get_task_list():
    """
        Function return task-list
        [
            ['id_1', 'name_1', 'task_1', 'status_1'], # First task `example`
            ['id_2', 'name_2', 'task_2', 'status_2', 'answer_1'],
        ]
    """
    query = "select (id, task_name, task, status, answer) from tasks;"
    cursor.execute(query, connection)
    rows = cursor.fetchall()
    tasks = []
    for row in rows:
        message = row[0]
        message = message[1:-1]
        message = message.split(',')
        tmp = [message[0]]
        if message[1][0] == '"':
            tmp.append(message[1][1:-1])
        else:
            tmp.append(message[1])
        if message[2][0] == '"':
            tmp.append(message[2][1:-1])
        else:
            tmp.append(message[2])
        if message[3][0] == '"':
            tmp.append(message[3][1:-1])
        else:
            tmp.append(message[3])
        if 'готов' in tmp[3]:
            logging.info('--> ' + str(message[4]) + ' <--')
            if message[4] == '':
                tmp.append('Нет ответа')
            elif message[4][0] == '"':
                tmp.append(message[4][1:-1])
            else:
                tmp.append(message[4])
        tasks.append(tmp)
    return tasks


def get_name_task(id_task):
    query = f"""
    select task_name
    from tasks
    where id={id_task};
    """
    cursor.execute(query, connection)
    name = cursor.fetchall()
    return name[0][0]


def get_task(id_task):
    query = f"""
    select task
    from tasks
    where id={id_task};
    """
    cursor.execute(query, connection)
    task = cursor.fetchall()
    return task[0][0]


def task_in_process(id_task):
    query = f"""
    update tasks
    set status='выполняется'
    where id={id_task}"""
    cursor.execute(query, connection)


def task_done(id_task, answer):
    query = f"""
    update tasks
    set status='готово'
    where id={id_task}"""
    cursor.execute(query, connection)
    query = f"""
    update tasks
    set answer='{answer}'
    where id={id_task}
    """
    cursor.execute(query, connection)


def task_fool(id_task):
    query = f"""
    update tasks
    set status='провал'
    where id={id_task}
    """
    cursor.execute(query, connection)
