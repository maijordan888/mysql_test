#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys,os
from collections import deque
import curses
import mysql.connector
from mysql.connector import Error
import mysql_operator as myop


def get_str_pos(order, x, y, width):
    split_len = decompose(order, width)
    if (len(split_len)-1) >= y:
        if y != 0:
            str_pos = sum(split_len[:y])
        else:
            str_pos = 0
        if x < split_len[y]:
            str_pos += x
        else:
            str_pos += split_len[y] - 1
        return str_pos
    else:
        return len(order)

def now_pos_limit(order, x, y, width):
    split_len = decompose(order, width)
    return split_len[y] - 1, len(split_len) - 1

def last_pos(order, width):
    split_len = decompose(order, width)
    return split_len[-1] - 1, len(split_len) - 1

def decompose(order, width):
    """decompose the order

    params:
        order: the order you want to split.
        width: window width
    return:
        split_len: each split order len (with '\\n').

    """
    split_cl = order.split('\n')
    split_len = []
    
    for l in split_cl:
        if len(l) < width:
            split_len.append(len(l) + 1)
        else:
            temp = l
            while len(temp) >= width:
                split_len.append(width)
                temp = temp[width:]
            split_len.append(len(temp) + 1)
    return split_len

def draw_menu(stdscr, db_connection):

    # for old order
    order_deque = deque(maxlen=15)
    order_index = 0
    # Three part of text
    old_text = ""
    front_text = "Enter mysql order ('q;' or 'Q;' for exit): "
    order = ""
    
    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    while True:
        # key word
        k = 0
        # Initial pointer pos
        height, width = stdscr.getmaxyx()
        if len(old_text) > 0:
            standard_text = old_text + '\n' + front_text + '\n'
        else:
            standard_text = front_text + '\n'
        cursor_x = 0
        _, cursor_y = last_pos(standard_text, width)
        # Loop where k is the last character pressed
        while True:

            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            # Pointer bound
            _, up_bound_y = last_pos(standard_text, width)
            # combine text
            combine_text = standard_text + order

            if k == curses.KEY_DOWN:
                max_x, max_y = now_pos_limit(combine_text, cursor_x, cursor_y, width)
                # Do not move down over the text
                if cursor_y + 1 > max_y:
                    if order_index == 0:
                        cursor_x = max_x
                    else:
                        order_index += 1
                        if order_index == 0:
                            order = ''
                            combine_text = standard_text + order                        
                            cursor_x, cursor_y = 0, up_bound_y
                        else:
                            order = order_deque[order_index]
                            combine_text = standard_text + order
                            cursor_x, cursor_y = last_pos(combine_text, width)
                else:
                    cursor_y = cursor_y + 1
                    max_x, _ = now_pos_limit(combine_text, cursor_x, cursor_y, width)
                    cursor_x = min(cursor_x, max_x)
            elif k == curses.KEY_UP:
                # Do not move up to the old_text and front text
                if cursor_y - 1 >= up_bound_y:
                    cursor_y = cursor_y - 1
                    max_x, _ = now_pos_limit(combine_text, cursor_x, cursor_y, width)
                    cursor_x = min(cursor_x, max_x)
                else:
                    if len(order_deque) != 0 and abs(order_index) != len(order_deque):
                        order_index -= 1
                        order = order_deque[order_index]
                        combine_text = standard_text + order
                        cursor_x, cursor_y = last_pos(combine_text, width)
                    else:
                        cursor_x = 0
            elif k == curses.KEY_RIGHT:
                max_x, max_y = now_pos_limit(combine_text, cursor_x, cursor_y, width)
                if cursor_x + 1 > max_x:
                    if cursor_y + 1 <= max_y:
                        cursor_x = 0
                        cursor_y = cursor_y + 1
                else:
                    cursor_x = cursor_x + 1
            elif k == curses.KEY_LEFT:
                if cursor_x - 1 < 0:
                    if cursor_y - 1 >= 0:
                        cursor_y = cursor_y - 1
                        max_x, _ = now_pos_limit(combine_text, cursor_x, cursor_y, width)
                        cursor_x = max_x
                else:
                    cursor_x = cursor_x - 1
            else:
                if k != 0:
                    now_pos = get_str_pos(order, cursor_x, cursor_y-up_bound_y, width)
                    if k == 263:
                        order = order[:(now_pos-1)] + order[now_pos:]
                        if (cursor_x-1) >= 0:
                            cursor_x = cursor_x - 1
                        else:
                            if (cursor_y - 1) >=up_bound_y:
                                cursor_y = cursor_y - 1
                                combine_text = standard_text + order
                                max_x, _ = now_pos_limit(combine_text, cursor_x, cursor_y, width)
                                cursor_x = max_x
                    else:
                        order = order[:now_pos] + chr(k) + order[now_pos:]
                        if k != 10:
                            if (cursor_x + 1) < width:
                                cursor_x = cursor_x + 1
                            else:
                                cursor_x = 0
                                cursor_y = cursor_y + 1
                        else:
                            cursor_x = 0
                            if cursor_y + 1 < height:
                                cursor_y = cursor_y + 1
                            else:
                                if len(old_text) == 0:
                                    raise Exception('Order too long.')
                                cut_index = decompose(old_text + '\n' + front_text + '\n' + order, width)
                                cut_index = sum(cut_index[:-height])
                                old_text = old_text[cut_index:]
                                # Reload standard text
                                standard_text = old_text + '\n' + front_text + '\n'


            # Check whether terminate
            if len(order) >= 2:
                if order[-2:] == ';\n':
                    old_text += '\n' + order[:-1]
                    result = myop.execute_query(db_connection, order[:-1])
                    if result:
                        old_text += '\n' + result
                    old_text += '\n' + '"' * (width-1)
                    cut_index = decompose(old_text + '\n' + front_text + '\n', width)
                    cut_index = sum(cut_index[:-height])
                    # Reload standard text
                    old_text = old_text[cut_index:]
                    standard_text = old_text + '\n' + front_text + '\n'
                    break

            # adjust pos
            cursor_x = max(0, cursor_x)
            cursor_x = min(width-1, cursor_x)

            cursor_y = max(0, cursor_y)
            cursor_y = min(height-1, cursor_y)

            # Rendering some text
            stdscr.attron(curses.A_BOLD)
            combine_text = standard_text + order
            stdscr.addstr(0, 0, combine_text)
            stdscr.attroff(curses.A_BOLD)
            # locate pointer
            stdscr.move(cursor_y, cursor_x)

            # Refresh the screen
            stdscr.refresh()

            # Wait for next input
            k = stdscr.getch()

        if len(order) == 3:
            if order == 'q;\n' or order == 'Q;\n':
                break
        order_deque.append(order[:-1])
        order = ''

def run(db_connection):
    curses.wrapper(draw_menu, db_connection)

if __name__ == "__main__":
    print('host name: ', end='')
    host_name = input()
    print('user name: ', end='')
    user_name = input()
    print('user password: ', end='')
    user_password = input()
    print('database name: ', end='')
    db_name = input()
    db_connection = myop.create_db_connection(host_name, user_name, user_password, db_name)
    if db_connection:
        run(db_connection)
        db_connection.close()

