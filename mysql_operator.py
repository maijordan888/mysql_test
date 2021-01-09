
import mysql.connector
from mysql.connector import Error
import pprint
import re
import math
import random
from collections import deque
import curses_input
table_index = 1
letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def create_test_db(host_name, user_name, user_password):
    """create database "test"

    params:
        host_name: host name. For example, 'localhost'.
        user_name: user name. For example, 'root'.
        user_password: password of the user name in mysql.
    
    return:
        connection: mysql.connector connection object of mysql server.
        cursor: mysql.connector cursor object of mysql server.

    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name, 
            user = user_name, 
            passwd = user_password
        )
    except Error as err:
        print("Connect Error:{}".format(err))
    else:
        cursor = connection.cursor()
        try:
            cursor.execute("CREATE DATABASE test;")
            connection.commit()
        except Error as err:
            print("Create database Error:{}".format(err))
    return connection, cursor

def create_db_connection(host_name, user_name, user_password, db_name):
    """create connection with data base

    params:
        host_name: host name. For example, 'localhost'.
        user_name: user name. For example, 'root'.
        user_password: password of the user name in mysql.
        db_name: database name.
    
    return:
        connection: mysql.connector connection object of database.

    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name, 
            user = user_name, 
            passwd = user_password, 
            database = db_name
        )
    except Error as err:
        print("Connect database Error:{}".format(err))
    
    return connection

def execute_query(connection, order=None):
    """execute mysql order without return information

    params:
        connection: mysql.connector object.
        order: mysql order you want to execute by connection.

    """
    if not order:
        order = input()
    cursor = connection.cursor()
    first_word = order.split(' ')[0]
    output = None
    try:
        cursor.execute(str(order))
        if cursor.with_rows:
            description = cursor.description 
            fetchall = cursor.fetchall()
            output = block_print(description, fetchall)
        if first_word != 'SHOW':
            connection.commit()
    except Error as err:
        output = "execute Error:{}".format(err)
    return output

def block_print(description, fetchall):
    """print result blockly

    params:
        description: cursor.description object.
        fetchall: cursor.fetchall object.

    return:
        output: string that has been blocked.

    """
    if len(fetchall) == 0:
        return

    width = []
    columns = []
    sep = '+'
    column_form = '|'
    column_len = []
    value_len = []
    output = ''

    for i, ds in enumerate(description):
        column_len.append(count_actual_len(ds[0]))
        value_len.append([count_actual_len(f[i]) for f in fetchall])        
        width.append(max(column_len[-1], max(value_len[-1])))
        columns.append(ds[0])
    
    for i in range(len(width)):
        times = int((width[i] + 3)//8 + 1)
        sep += '-'*(times*8 - 1) + '+'
        c_times = math.ceil(width[i] - column_len[i])
        column_form += " {" + "}" + " "*c_times + " \t|"
    
    output += sep + '\n'
    output += column_form.format(*columns) + '\n'
    output += sep + '\n'
    for i, fetch in enumerate(fetchall):
        value_form = '|'
        for j in range(len(width)):
            v_times = math.ceil(width[j] - value_len[j][i])
            value_form += " {" + "}" + " "*v_times + " \t|"
        f = [str(v) for v in fetch]
        output += value_form.format(*f) + '\n'
    output += sep + '\n'
    return output

def count_chineese_num(string):
    """count how many chineese word in string
    """
    try:
        chineese_word_num = len(re.findall('[\u4100-\u9fff]', string))
    except:
        chineese_word_num = 0
    return chineese_word_num

def count_actual_len(string):
    """count actual length of string with chineese
    
    test for "-", 1 chineese word length is 2 "-"
    (but in interactive windows is 5/3 "-" and I don't
    know why)
    
    """
    chineese_word_num = count_chineese_num(string)
    actual_len = length(string) + chineese_word_num
    return actual_len    

def length(s):
    if type(s) == float:
        return len(str(s)) - 1
    else:
        return len(str(s))

def create_table(connection, string):
    """use table string to create table

    params:
        connection: mysql.connector object which connect to
            test database.
        string: table string.

    """
    global table_index
    names, values = split_table_string(string)
    name_types = [check_type(value) for value in values]
    table_string = table_string_construct(names, name_types)
    execute_query(connection, table_string)
    for i in range(len(values[0])):
        insert_into(connection, 'table{}'.format(table_index), 
                    *[value[i] for value in values])
    table_index += 1


def create_random_table(connection, string):
    """create random table columns by user define types

    params:
        connection: mysql.connector object which connect to
            test database.
        string: "id" or "INT" or "VARCHAR(n)" split by space
            and number of row at second line.
            Ex:
            id INT INT VARCHAR(10)
            3

    """
    # decomposition order string
    rows = string.split('\n')
    if len(rows[-1]) == 0:
        rows = rows[:-1]
    types = rows[0].split(' ')
    row_num = int(rows[1])
    # construct columns
    column_index = 1
    table = ""
    for ty in types:
        if table != "":
            table += ', '
        if ty == 'id':
            table += 'id'
            table += ' '
            table += 'INT'
        else:
            table += 'column{}'.format(column_index)
            table += ' '
            table += ty
            column_index += 1
    # construct table string
    table_string = """
    CREATE TABLE table{}(
        {}
    );
    """.format(table_index, table)
    execute_query(connection, table_string)    
    # add random row value
    values = []    
    for ty in types:
        if ty == 'id':
            values.append([i for i in range(row_num)])
        elif ty == 'INT' or ty == 'int':
            values.append([random.randint(0, 100) for _ in range(row_num)])
        elif 'VARCHAR(' in ty and ')' in ty:
            z = re.match('VARCHAR\(([0-9]+)\)', ty)
            wml = int(z.group(1))
            values.append([random_word(wml) for _ in range(row_num)])
        else:
            print("error input: {}".format(string))
            return

    for r in range(row_num):
        insert_into(connection, 'table{}'.format(table_index), 
                    *[values[i][r] for i in range(len(values))])

def random_word(n):
    """return random word with max length n
    """
    word_len = random.randint(1, n)
    word = ''
    for i in range(word_len):
        word += letters[random.randint(0, 51)]
    return word

def insert_into(connection, table_name, *values):
    """mysql order: INSERT INTO table_name VALUES()

    params:
        connection: mysql.connector object.
        table_name: insert into this table.
        *values: values you want to insert

    """
    insert_values = ''
    for v in values:
        if insert_values != '':
            insert_values += ', '
        if v != 'NULL':
            temp = "'" + str(v) + "'"
        else:
            temp = v
        insert_values += temp
    order = """
    INSERT INTO {} VALUES(
        {}
    );
    """.format(table_name, insert_values)
    execute_query(connection, order)

def table_string_construct(names, types):
    """construct table string and return it
    """
    global table_index
    table = ""
    for n, y in zip(names, types):
        if table != "":
            table += ', '
        table += n
        table += ' '
        table += y

    table_string = """
    CREATE TABLE table{}(
        {}
    );
    """.format(table_index, table)
    return table_string

def check_type(values):
    """check which type the value is

    params:
        values: list of the str value.

    return:
        condition: word type. Can be INT, DOUBLE, VARCHAR. 
    """
    condition = 'INT'
    int_word = '[0-9]+$'
    double_word = '[0-9]+\.[0-9]+$'
    max_len = max([len(value) for value in values])
    
    for value in values:
        if condition == 'INT':
            try:
                z = re.match(int_word, value).group()
            except:
                condition = 'DOUBLE'
        if condition == 'DOUBLE':
            try:
                z = re.match(double_word, value).group()
            except:
                condition = 'VARCHAR({})'.format(max_len)
        if condition == 'VARCHAR({})'.format(max_len):
            break
    
    return condition                
    
def split_table_string(string):
    """split the table string to column name and values

    params:
        string which need to split.

    return:
        column_names: name of columns.
        column_values: value of columns.

    Example:
        name course grade
        張三 語文 81
        張三 數學 75
        李四 語文 76
        李四 數學 90
        王五 語文 81
        王五 數學 100
        王五 英語 90
    
    Example return:
        columns_names:
            ['name', 'course', 'grade']
        columns_values:
            [['張三', '張三', '李四', '李四', '王五', '王五', '王五'],
            ['語文', '數學', '語文', '數學', '語文', '數學', '英語'],
            ['81', '75', '76', '90', '81', '100', '90']])
    """
    rows = string.split('\n')
    if len(rows[-1]) == 0:
        rows = rows[:-1]
    split_rows = [row.split(' ') for row in rows]
    columns = []
    for i in range(len(split_rows[0])):
        columns.append([r[i] for r in split_rows])
    column_values = [c[1:] for c in columns]
    column_names = [c[0] for c in columns]
    return column_names, column_values
