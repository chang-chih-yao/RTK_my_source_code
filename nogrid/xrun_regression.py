from __future__ import print_function
from subprocess import Popen, PIPE
import sys
import os
import threading
import time
import tty, termios
import glob
# from pyrun_py2 import pyrun_run, pyrun_regression

history_size  = 20
history_cmd   = []
ascii_list    = []
cmd_char_list = ''
tmp_cmd       = ''
now_cursor    = 0
his_pos       = 0
cmd_finish    = False
exit_flag     = False



class _Getch:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def light_cursor_move(number, earse_right = True):
    if number > 0:
        print("\033[%dD" % number, end='')     ## move  left
    elif number < 0:
        print("\033[%dC" % abs(number), end='')     ## move  left
    else:
        return
    if earse_right:
        print("\033[K",            end='') ## erase right

def get_keyboard():
    global ascii_list, cmd_char_list, cmd_finish, exit_flag, now_cursor, his_pos, tmp_cmd
    inkey = _Getch()
    while(1):
        k = inkey()
        if k != '':
            break

    ascii_list.append(ord(k))

    if len(ascii_list) == 1 and ascii_list[0] >= 32 and ascii_list[0] <= 126:            # keyboard input normal symbol
        if now_cursor != len(cmd_char_list):                                             # if cursor move backward
            cmd_char_list = cmd_char_list[:now_cursor] + (chr(ascii_list[0])) + cmd_char_list[now_cursor:]
        else:
            cmd_char_list += (chr(ascii_list[0]))
        now_cursor += 1
        sys.stdout.write('\r'+cmd_char_list)
        sys.stdout.flush()
        if now_cursor != len(cmd_char_list):
            light_cursor_move(len(cmd_char_list) - now_cursor, earse_right = False)
            #print("\033[%dD" % (len(cmd_char_list) - now_cursor), end='')
        ascii_list.pop(0)
    elif len(ascii_list) == 1 and ascii_list[0] == 127:                                  # press backspace
        ascii_list.pop(0)
        if len(cmd_char_list) >= 1:
            if now_cursor >= 1:
                cmd_char_list = cmd_char_list[:now_cursor-1] + cmd_char_list[now_cursor:]
                now_cursor -= 1
                light_cursor_move(1, earse_right = True)
                #print("\033[1D", end='')
                #print("\033[K", end='')
                sys.stdout.write('\r'+cmd_char_list)
                sys.stdout.flush()
                if now_cursor != len(cmd_char_list):
                    light_cursor_move(len(cmd_char_list) - now_cursor, earse_right = False)
                    #print("\033[%dD" % (len(cmd_char_list) - now_cursor), end='')
    elif len(ascii_list) == 1 and ascii_list[0] == 13:                                   # press enter
        ascii_list.pop(0)
        cmd_finish = True
    elif len(ascii_list) == 1 and ascii_list[0] == 3:                                    # press ctrl-c
        ascii_list.pop(0)
        exit_flag = True
        print_message_on_terminal('Please enter your cmd or exit to leave: ')
    elif len(ascii_list) == 3 and ascii_list[0] == 27 and ascii_list[1] == 91:
        # arrow key ascii:
        # up: 27, 91, 65
        # down: 27, 91, 66
        # right: 27, 91, 67
        # left: 27, 91, 68
        if ascii_list[2] == 65 and len(history_cmd) >= 1 and his_pos < len(history_cmd): # press up
            if his_pos == 0:
                tmp_cmd = cmd_char_list
            light_cursor_move(len(cmd_char_list), earse_right = True)
            #print("\033[%dD" % (len(cmd_char_list)), end='')
            #print("\033[K", end='')
            his_pos += 1
            cmd_char_list = history_cmd[-his_pos]
            now_cursor = len(cmd_char_list)
            sys.stdout.write('\r'+cmd_char_list)
            sys.stdout.flush()

        elif ascii_list[2] == 66 and his_pos > 0:                               # press down
            light_cursor_move(len(cmd_char_list), earse_right = True)
            #print("\033[%dD" % (len(cmd_char_list)), end='')
            #print("\033[K", end='')
            his_pos -= 1
            if his_pos == 0:
                cmd_char_list = tmp_cmd
            else:
                cmd_char_list = history_cmd[-his_pos]
            now_cursor = len(cmd_char_list)
            sys.stdout.write('\r'+cmd_char_list)
            sys.stdout.flush()

        elif ascii_list[2] == 67:                                               # press right
            if now_cursor < len(cmd_char_list) and len(cmd_char_list) >= 1:
                light_cursor_move(-1, earse_right = False)
                #print("\033[1C", end='')
                now_cursor += 1
        elif ascii_list[2] == 68:                                               # press left
            if now_cursor >= 1 and len(cmd_char_list) >= 1:
                light_cursor_move(1, earse_right = False)
                #print("\033[1D", end='')
                now_cursor -= 1
        # pop 3 ascii code
        ascii_list.pop(0)
        ascii_list.pop(0)
        ascii_list.pop(0)
    elif ascii_list[0] == 27 and len(ascii_list) == 1:                          # on going capture arrow key
        pass
    elif ascii_list[0] == 27 and ascii_list[1] == 91 and len(ascii_list) == 2:  # on going capture arrow key
        pass
    else:
        #print('capture unkown key')
        #for item in ascii_list:
        #    print(item)
        for i in range(len(ascii_list)):
            ascii_list.pop(0)

def get_cmd():
    global cmd_finish, exit_flag, ascii_list, cmd_char_list, now_cursor, his_pos
    cmd_finish = False
    exit_flag = False
    ascii_list = []
    cmd_char_list = ''
    now_cursor = 0
    his_pos = 0
    while(True):
        get_keyboard()
        if cmd_finish:
            print()
            return cmd_char_list, cmd_finish
        #if exit_flag:
        #    return cmd_char_list, cmd_finish


def show_history_cmd():
    global history_cmd

    print_message_on_terminal('cmd history: ')
    for cmd in history_cmd:
        print_message_on_terminal('    ' + cmd)

def record_history_cmd(cmd):
    global history_cmd

    if len(history_cmd) == history_size:
        history_cmd = history_cmd[1:]

    if len(history_cmd) > 0:
        if history_cmd[-1] != cmd:
            history_cmd.append(cmd)
    else:
        history_cmd.append(cmd)


def print_message_on_terminal(message, is_error = False):
    HEADER = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    if is_error:
        print(FAIL + BOLD + message + ENDC)
    else:
        print(BOLD + message + ENDC)

def do_cmd_on_terminal(cmd):
    global history_cmd

    record_history_cmd(cmd)
    # print_message_on_terminal('do this now: ' + cmd)
    os.system(cmd)

def do_cd_on_terminal(cmd):
    global history_cmd

    record_history_cmd(cmd)

    # print_message_on_terminal('do this now: ' + cmd)
    try:
        path = cmd.replace('cd ', '')
        os.chdir(path)
    except:
        print_message_on_terminal('no such directory: ' + path, is_error = True)


def run_regression(cmd_a, cmd_b):
    try:
        path = cmd.replace('cd ', '')
        os.chdir(cmd_a)
    except:
        print_message_on_terminal('no such directory: ' + path, is_error = True)
    time.sleep(1)
    os.system(cmd_b)

def regression_cmd_list(cmd):
    t_lst = []
    for tuple in cmd:
        a = tuple[0]
        b = tuple[1]
        t1 = threading.Thread(target=run_regression, args=(a, b,))
        t_lst.append(t1)
    for t in t_lst:
        t.start()
    for t in t_lst:
        t.join()

time.sleep(1)
print_message_on_terminal('******************** We are on Grid now ********************')
pwd_name = ''
cpu_name = ''

p1 = Popen(['lscpu'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
stdout, stderr = p1.communicate()
lines = stdout.split('\n')
for line in lines:
    if line.find('Model name:') != -1:
        # print(line)
        if line.find('6146') != -1:
            print('Intel 6146, core 12')
        elif line.find('6246') != -1:
            print('Intel 6246R, core 16')
        elif line.find('6346') != -1:
            print('Intel 6346, core 16')
        else:
            print(line)

p2 = Popen(['mpstat'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
stdout, stderr = p2.communicate()
lines = stdout.split('\n')
cpu_name = lines[0].split(' ')[2].replace('(', '').replace(')', '')
# print(cpu_name)

# while(1):
#     qstat_list = []
#     p1 = Popen(['qstat'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
#     stdout, stderr = p1.communicate()
#     # print(stdout)
#     tmp = stdout.split('\n')
#     for i in range(len(tmp)):
#         # print(i, tmp[i])
#         tmp_ = tmp[i].split(' ')
#         for item in tmp_:
#             if item.find('grid_occu') != -1:
#                 for gg in tmp_:
#                     if gg != '':
#                         qstat_list.append(gg)
#                 break

#     if len(qstat_list) != 9:
#         print('wait grid ready')
#         # print(qstat_list)
#         time.sleep(3)
#     else:
#         cpu_name = qstat_list[7].split('@')[-1]
#         print('grid ok, on', cpu_name)
#         break

print_message_on_terminal('Please enter your cmd or exit to leave: ')

while(True):
    pwd_name = cpu_name + ': ' + os.getcwd() + '>'
    print(pwd_name)
    cmd, cmd_finish = get_cmd()

    if cmd_finish:
        now_pwd = os.getcwd()
        pwd_list = now_pwd.split('/')
        # print(pwd_list)
        verification_position = 0
        for i in range(len(pwd_list)):
            if pwd_list[i].find('verification') != -1:
                verification_position = i
        # print(verification_position)
        now_dir_to_verification_len = len(pwd_list) - verification_position -1
        verification_dir = '../' * now_dir_to_verification_len
        # print(verification_dir)

        if cmd.startswith('make'):
            record_history_cmd(cmd)
            cmd = cmd[len('make'):]  # remove 'make' char
            os.system('python ' + verification_dir + 'python_src/pyrun_py2.py single ' + cmd + ' NOGRID=1 2> /dev/null')
            print('make done')
            # os.system('rm -rf pyrun_regression.tmpfile')

        elif cmd.startswith('batch CFG='):
            record_history_cmd(cmd)
            cfg_file = cmd.replace('batch CFG=', '')
            os.system('python ' + verification_dir + 'python_src/pyrun_py2.py multi ' + cfg_file)
            print('batch done')
            # os.system('rm -rf pyrun_regression.tmpfile')

        elif cmd.startswith('compile_check'):
            record_history_cmd(cmd)
            os.system('python ' + verification_dir + 'python_src/pyrun_py2_compile_check.py' + ' compile_check' + ' NOGRID=1 2> /dev/null')

        elif cmd.startswith('my_top'):
            record_history_cmd(cmd)
            os.system('top -b -n1 -u root | grep Cpu')

        elif cmd.startswith('cd'):
            do_cd_on_terminal(cmd)

        elif cmd == "h":
            show_history_cmd()

        elif cmd == 'help':
            print_message_on_terminal('Please enter your cmd or exit to leave: ')

        elif cmd == 'exit':
            break

        elif cmd == '':
            pass

        else:
            do_cmd_on_terminal(cmd)

print_message_on_terminal('******************** We are out of Grid now ********************')