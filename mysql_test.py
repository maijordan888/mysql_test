#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import deque
import mysql.connector
from mysql.connector import Error
import mysql_operator as myop
import mysql_order_window

if __name__ == "__main__":
    print('host name: ', end='')
    host_name = input()
    print('user name: ', end='')
    user_name = input()
    print('user password: ', end='')
    user_password = input()
    sv_connection, sv_cursor = myop.create_test_db(host_name, user_name, user_password)
    db_connection = myop.create_db_connection(host_name, user_name, user_password, 'test')

    try:    
        # create table
        print("First create the table(r for random):", end='')
        string = ''
        string = '\n'.join(iter(input, string))
        while string != 'q' and string != 'Q':
            if string != 'r':
                myop.create_table(db_connection, string)
            else:
                print("Choose to create random table. ", end='')
                print("First line key in the type (id, INT, VARCHAR(n). ", end='')
                print("second line key in the number of row:")
                string = ''
                string = '\n'.join(iter(input, string))
                myop.create_random_table(db_connection, string)
            print("Key in another table or exit(q or Q):", end='')
            string = ''
            string = '\n'.join(iter(input, string))
        # choose operate mechanism
        print("Key in the mechanism you want (o: old one but support chinese, n: new one but unsupport chinese: ", 
                end='')
        while 1:
            mech = input()
            if mech != 'n' and mech != 'o':
                print('\nplease enter "n" or "o": ', end='')
            else:
                break
        
        # operate table
        if mech == 'o':
            print("That's operate table:", end='')
            order = input()
            while order[-1] != ';':
                order += '\n' + input()
            while order != 'q;' and order != 'Q;':
                result = myop.execute_query(db_connection, order)
                if result:
                    print(result, end='')
                print("Give another order or exit(q; or Q;):", end='')
                order = input()
                while order[-1] != ';':
                    order += '\n' + input()
        else:
            mysql_order_window.run(db_connection)

    except Exception as err:
        print(err)

    db_connection.close()
    try:
        sv_cursor.execute('DROP DATABASE test;')
        sv_connection.commit()
    except Error as err:
        print("Drop Database Error:{}".format(err))

    sv_cursor.close()
    sv_connection.close()
