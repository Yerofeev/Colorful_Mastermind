# coding: utf-8
from __future__ import print_function
import os
import sys
import tty
import termios
from time import sleep
from random import randint


try:
    input = raw_input
except NameError:
    pass


# [red, yellow, green, blue, white, purple,light blue] Extended ANSI
colors = ['\033[91m',
          '\033[93m',
          '\033[32m',
          '\033[34m',
          '\033[37m',
          '\033[35m',
          '\033[96m',
          ]
bull = '▶ '
cow = '▷ '
peg = '⏺ '


def print_there(x, y, text):
    """Print at a certain position(x,y) in the terminal"""
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.flush()


def input_difficulty(message):
    """User input in range [3,7]"""
    while True:
        difficulty = input(message)
        try:
            if 3 <= int(difficulty) <= 7:
                return int(difficulty)
        except ValueError:
            if difficulty == 'q':
                sys.exit()


def preliminaries():
    """Set the screen, get the password length and number of different colors in code from player,
    paint the game-field"""
    y = 47
    os.system('clear')
    print_there(1, 60, '(q - Quit)')
    print('Choose difficulty level: ')
    length = input_difficulty('Enter the length of code [3-7]: ')
    strength = input_difficulty('Enter the number of possible distinct symbols [3-7]: ')
    os.system('clear')
    secret_number = []
    for i in range(length):
        secret_number.append(randint(1, strength))
    for i in range(1, 21):
        print(i)
        print_there(i, length + 16, '# #' + ' '*17 + '# #')
    print_there(3, y, 'Length = ' + str(length))
    print_there(5, y, 'Q - Quit')
    print_there(7, y, bull + 'Right color & position')
    print_there(8, y, cow + 'Right color')
    for i in range(strength):
        print_there(10 + i, y, (colors[i] + peg))
        print_there(10 + i, y + 2, str(i + 1))
    print_there(18, y, colors[2] + 'Only digits or Q')
    os.system('setterm -cursor off')                       # disable cursor
    return length, strength, secret_number


def get_char(length, strength, entered_number, y):
    """Dynamically reads one symbol entered by player
    then either add one symbol to the code according to color-scheme depending on length and strength of code:
    1 - Red
    2 - Yellow
    ...
    or perform comparison to the secret code if 'Enter' or exits if 'Q'"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    k = 0
    print_there(18, 47, colors[2] + 'Only digits or Q')
    while True:
        try:
            tty.setcbreak(fd)
            answer = sys.stdin.read(1)
            try:
                answer = int(answer)
                if not 1 <= answer <= strength:
                    continue
                print_there(y, 6 + 2*(k % length), colors[answer - 1] + peg)
                entered_number[k % length] = answer
                k += 1
            except ValueError:
                if answer == 'Q':
                    sys.exit()
                elif answer == '\n':
                    if entered_number.count(0) == 0:
                        return entered_number
                elif ord(answer) == 127:   # Backspace
                    z = entered_number.count(0)
                    if z != length:   # check that smth was entered
                        if z == 0:    # if no zeroes left in player-list - delete the last element from list
                            entered_number[-1] = 0
                        else:
                            # delete the first element before first zero element in player list
                            entered_number[entered_number.index(0) - 1] = 0
                        k = entered_number.index(0)       # counter is determined by index of the first zero in list
                        print_there(y, 6 + 2 * (length-1) - 2 * z, ' '*2)
                    continue
                elif answer not in [str(i) for i in range(1, strength + 1)]:
                    print_there(18, 47, colors[0] + 'Only digits or Q')
                    continue
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def game_proc(a, b):
    """Bulls&cows comparing algorithm: first part: count bulls: simply run through the secret and user-entered code
    increasing index, if == then it's bull since index is the same for both codes, if != then add this index
    to empty list 'k' of potential place for cow.
    The second part, it is trickier: for each element in the secret code with appended index in the k-list check
    if there is the corresponding color in user-entered list, if yes, then remove this element from player-list
    to avoid repetition in case there is another such element in the secret code
    """
    k = []
    bulls = 0
    cows = 0
    for i in range(len(a)):
        if a[i] == b[i]:
            bulls += 1
            b[i] = 0
        else:
            k.append(i)  # list of potential cow's position
    for i in k:
        if a[i] in b:
            cows += 1
            del b[b.index(a[i])]     # to avoid repetition when element from the 1st list is being searched in the 2nd
    return bulls, cows


def main():
    if not sys.platform.startswith('linux'):
        print('Unfortunately your OS is not currently supported!')
        sleep(3)
        return
    try:
        while True:
            length, strength, secret_number = preliminaries()
            y = 1                 # x, y - to print at certain coordinates
            while True:
                entered_number = [0 for _ in range(length)]   
                entered_number = get_char(length, strength, entered_number, y)
                bulls, cows = game_proc(secret_number, entered_number)    # the game_procedure
                print_there(y, length + 21, bull * bulls + cow * cows)   # prints result for current combination
                if bulls == len(secret_number):
                    print(colors[0] + '♕ ♕ ♕  You have won! ♔ ♔ ♔ ')
                    break
                y += 1
                if y == 21:
                    print(colors[0] + 'Game over. The correct combination was:')
                    for i, j in enumerate(secret_number):
                        print_there(21, 45 + i*2, colors[j-1] + peg)
                    break
            while True:
                play_again = input(colors[1] + "Would you like to play again? [y,n]\033[0m")
                if play_again in {'n', 'N'}:
                    sys.exit()
                elif play_again in {'y', 'Y'}:
                    break
                else:
                    pass
    finally:
        print('\033[0m')  # reset shell coloring
        os.system('setterm -cursor on')  # return cursor
        os.system('clear')


if __name__ == '__main__':
        main()
