import sys,os
import curses
import locale
locale.setlocale(locale.LC_ALL, '')

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

def draw_menu(stdscr):
    k = 0
    cursor_x = 0
    cursor_y = 0
    string = ""
    # stdscr.scrollok(1)

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Loop where k is the last character pressed
    while (k != ord('q')):

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN:
            max_x, max_y = get_limit_pos(string, cursor_x, cursor_y, width)
            if cursor_y + 1 > max_y:
                cursor_x = max_x
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
                        cursor_x = width - 1
                        cursor_y = cursor_y - 1
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

        cursor_x = max(0, cursor_x)
        cursor_x = min(width-1, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(height-1, cursor_y)

        # Declaration of strings
        title = "Curses example"[:width-1]
        subtitle = "Written by Clay McLeod"[:width-1]
        keystr = "Last key pressed: {}".format(k)[:width-1]
        statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(cursor_x, cursor_y)
        if k == 0:
            keystr = "No key press detected..."[:width-1]

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)
        start_y = int((height // 2) - 2)

        # Rendering some text
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(0, 0, string)
        stdscr.attroff(curses.A_BOLD)

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
        stdscr.addstr(start_y + 5, start_x_keystr, keystr)
        stdscr.move(cursor_y, cursor_x)

        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        k = stdscr.getch()

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
