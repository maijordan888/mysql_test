import sys,os
import curses

def get_str_pos(string, x, y, width):
    split_len = split_string(string, width)
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
        return len(string)

def get_limit_pos(string, x, y, width):
    split_len = split_string(string, width)
    return split_len[y] - 1, len(split_len) - 1

def last_pos(string, width):
    split_len = split_string(string, width)
    return split_len[-1] - 1, len(split_len) - 1

def split_string(string, width):
    split_cl = string.split('\n')
    split_len = []
    for l in split_cl:
        if len(l) < width:
            split_len.append(len(l) + 1)
        else:
            temp = l.copy()
            while len(temp) >= width:
                split_len.append(width)
                temp = temp[width:]
            split_len.append(len(l) + 1)
    return split_len

def draw_menu(stdscr, order_deque):
    global string
    order_index = 0
    k = 0
    cursor_x = 0
    cursor_y = 0
    string = ""

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Loop where k is the last character pressed
    while True:

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN:
            max_x, max_y = get_limit_pos(string, cursor_x, cursor_y, width)
            if cursor_y + 1 > max_y:
                if order_index == 0:
                    cursor_x = max_x
                else:
                    order_index += 1
                    if order_index == 0:
                        string = ''
                        cursor_x, cursor_y = 0, 0
                    else:
                        string = order_deque[order_index]
                        cursor_x, cursor_y = last_pos(string, width)
            else:
                cursor_y = cursor_y + 1
                max_x, _ = get_limit_pos(string, cursor_x, cursor_y, width)
                cursor_x = min(cursor_x, max_x)
        elif k == curses.KEY_UP:
            if cursor_y - 1 >= 0:
                cursor_y = cursor_y - 1
                max_x, _ = get_limit_pos(string, cursor_x, cursor_y, width)
                cursor_x = min(cursor_x, max_x)
            else:
                if len(order_deque) != 0 and abs(order_index) != len(order_deque):
                    order_index -= 1
                    string = order_deque[order_index]
                    cursor_x, cursor_y = last_pos(string, width)
                else:
                    cursor_x = 0
        elif k == curses.KEY_RIGHT:
            max_x, max_y = get_limit_pos(string, cursor_x, cursor_y, width)
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
                    max_x, _ = get_limit_pos(string, cursor_x, cursor_y, width)
                    cursor_x = max_x
            else:
                cursor_x = cursor_x - 1
        else:
            if k != 0:
                now_pos = get_str_pos(string, cursor_x, cursor_y, width)
                if k == 263:
                    string = string[:(now_pos-1)] + string[now_pos:]
                    if (cursor_x-1) >= 0:
                        cursor_x = cursor_x - 1
                    else:
                        cursor_y = cursor_y - 1
                        max_x, _ = get_limit_pos(string, cursor_x, cursor_y, width)
                        cursor_x = max_x
                else:
                    string = string[:now_pos] + chr(k) + string[now_pos:]
                    if k != 10:
                        if (cursor_x + 1) < width:
                            cursor_x = cursor_x + 1
                        else:
                            cursor_x = 0
                            cursor_y = cursor_y + 1
                    else:
                        cursor_x = 0
                        cursor_y = cursor_y + 1

        # check whether terminate
        if len(string) >= 2:
            if string[-2:] == ';\n':
                break

        # adjust pos
        cursor_x = max(0, cursor_x)
        cursor_x = min(width-1, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(height-1, cursor_y)

        # Rendering some text
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(0, 0, string)
        stdscr.attroff(curses.A_BOLD)
        # locate pointer
        stdscr.move(cursor_y, cursor_x)

        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        k = stdscr.getch()

def input_windows(order_deque):
    global string
    curses.wrapper(draw_menu, order_deque)
    return string
