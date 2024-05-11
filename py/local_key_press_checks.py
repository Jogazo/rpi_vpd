#!/usr/bin/python3
import sys
import select
import tty
import termios

button_delay = 0.1


def has_input():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def loop():
    while True:
        if has_input():
            c = sys.stdin.read(1)

            if c == '\x1b':
                print('Exit.')
                break

            elif c == 'a':
                print('Left pressed')
            elif c == 'd':
                print('Right pressed')
            elif c == 'w':
                print('Up pressed')
            elif c == 's':
                print('Down pressed')
            elif c == ' ':
                print('Stop the car!')
            else:
                print(c)


old_settings = termios.tcgetattr(sys.stdin)
try:
    tty.setcbreak(sys.stdin.fileno())
    loop()
finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
