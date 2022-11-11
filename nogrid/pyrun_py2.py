#!/bin/python
from __future__ import print_function
import os
from subprocess import Popen, PIPE, STDOUT
import sys
import codecs
import threading
import multiprocessing as mp
from multiprocessing import Value
import time
import tty, termios
import glob
import re
# import configparser


class pyrun_run:
    def __init__(self):
        self.ascii_list = []
        self.exit_flag = False
        self.wait_main_thread = False
        self.moved_file = False
        self.in_run_dir = True
        self.key_inter = ''
        self.pattern_filename = ''
        self.cmd = ''
        self.xrun_cmd = ''
        self.mv_dir_name = '/xcelium.d/'
        self.mv_dir_name_ = '/xcelium.tmp/'
        self.ncargs_name = '/ncargs'
        self.ncargs_name_ = '/ncargs_tmp'
        self.DEFAULT_PATTERN = 'i2s_sample_rate_48k_test'
        self.DEFAULT_SEED = '0'

    def reset_var(self):
        self.ascii_list = []
        self.exit_flag = False
        self.wait_main_thread = False
        self.moved_file = False

    def print_message_on_terminal(self, message, is_error = False):
        HEADER = '\033[95m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'

        if is_error:
            print(FAIL + BOLD + message + ENDC)
        else:
            print(BOLD + message + ENDC)

    def func(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def get(self):
        while(1):
            k = self.func()
            # print(k)
            if k != '':
                break

        if not self.exit_flag:
            self.ascii_list.append(ord(k))
            # print(self.ascii_list)

            if len(self.ascii_list) == 1 and self.ascii_list[0] == 3:    # press ctrl+c
                self.ascii_list.pop(0)
                self.exit_flag = True
            else:
                # for item in self.ascii_list:
                #   print(item)
                for i in range(len(self.ascii_list)):
                    self.ascii_list.pop(0)

    def detect_key(self):
        self.ascii_list = []
        while(True):
            self.get()
            if self.exit_flag:
                # if self.wait_main_thread:
                #     self.reset_var()
                #     break
                if not self.moved_file:
                    # print('mv operator')
                    os.system('mv ' + self.pattern_filename + self.mv_dir_name + ' ' + self.pattern_filename + self.mv_dir_name_)
                    os.system('mv ' + self.pattern_filename + self.ncargs_name + ' ' + self.pattern_filename + self.ncargs_name_)
                    self.moved_file = True

    def check_global(self):
        time.sleep(5)
        while(True):
            time.sleep(0.5)
            # if os.path.isfile('pyrun_regression.tmpfile'):
            if process_share_value.value == 1:
                if not self.moved_file:
                    print('mv operator')
                    os.system('mv ' + self.pattern_filename + self.mv_dir_name + ' ' + self.pattern_filename + self.mv_dir_name_ + ' > /dev/null 2>&1')
                    os.system('mv ' + self.pattern_filename + self.ncargs_name + ' ' + self.pattern_filename + self.ncargs_name_ + ' > /dev/null 2>&1')
                    self.moved_file = True
                break

    def show_status(self):
        while(True):
            time.sleep(0.5)
            if process_share_press_s.value == 1:
                print('{} : {}'.format(cpu_name, self.cmd))
                process_share_press_s.value = 0

    def do(self, my_argv):
        self.reset_var()

        # key_interupt_thread = multiprocessing.Process(target = self.detect_key)
        # key_interupt_thread = threading.Thread(target=self.detect_key)
        # key_interupt_thread.daemon = True
        # key_interupt_thread.start()

        check_thread = threading.Thread(target=self.check_global)
        check_thread.daemon = True
        check_thread.start()

        show_status_thread = threading.Thread(target=self.show_status)
        show_status_thread.daemon = True
        show_status_thread.start()

        tc_name = self.DEFAULT_PATTERN
        seed = self.DEFAULT_SEED

        # my_argv = my_str.split()




        cmd_str = ''
        cmd_list = my_argv[1:]


        # p1 = Popen(['pwd'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        # stdout, stderr = p1.communicate()
        # # print(stdout)
        # new_stdout = stdout.decode('UTF-8')
        new_stdout = os.getcwd()
        if new_stdout.replace('\n', '').split('/')[-1] == 'run':   # if in run/ dir
            for arg in my_argv[1:]:
                if arg.find('=') == -1:  # dont find '='
                    tc_name = arg.split('/')[-1].split('.')[0]
                    cmd_list.remove(arg)
                else:
                    if arg.startswith('TC_NAME='):
                        tc_name = arg[len('TC_NAME='):]
                        cmd_list.remove(arg)
                    elif arg.startswith('SEED='):
                        seed = arg[len('SEED='):]

            cmd_str += 'make TC_NAME=' + tc_name + ' '
            for cmd in cmd_list:
                cmd_str += cmd + ' '

            self.pattern_filename = new_stdout.replace('\n', '') + '/' + tc_name + '_' + seed
            # print('in run/ dir: ' + self.pattern_filename)

        else:                                                      # in pattern dir
            self.in_run_dir = False
            cmd_str += 'make '
            for cmd in cmd_list:
                cmd_str += cmd + ' '

            self.pattern_filename = new_stdout.replace('\n', '')
            # print('in pattern dir: ' + self.pattern_filename)

        # print(self.pattern_filename)
        cmd_str += ' python_nogrid'
        print(cmd_str)
        print('------------------------------------------------')
        self.cmd = cmd_str
        p1 = Popen(cmd_str, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p1.communicate()
        makefile_output = stdout.split('\n')
        dpic_name = ''
        try:
            for i in range(len(makefile_output)):
                if makefile_output[i].startswith('xrun'):
                    self.xrun_cmd = makefile_output[i]
                    dpic_name = makefile_output[i+1]
                    print(self.xrun_cmd)
                    break
        except:
            print('makefile cmd error')
            exit()

        if self.xrun_cmd == '':
            print('makefile cmd error')
            exit()

        if self.in_run_dir:
            os.chdir(self.pattern_filename)     # go to pattern dir
        # os.system(self.xrun_cmd + ' | tee ' + dpic_name)
        os.system('stdbuf -oL ' + self.xrun_cmd + ' | tee ' + dpic_name + ' 2> /dev/null')

        # key_interupt_thread = multiprocessing.Process(target = self.detect_key)
        # key_interupt_thread.start()
        # time.sleep(10)
        # key_interupt_thread.terminate()



        if os.path.isfile(self.pattern_filename + '/dpic.log'):
            f = codecs.open(self.pattern_filename + '/dpic.log', 'r', errors = 'ignore')
            lines = f.readlines()
            f.close()

            err_cou = 0
            err_position = 1
            uvm_err_cou = 0
            uvm_err_position = 1
            for i in range(len(lines)):
                if lines[i].find('*E') != -1:
                    if lines[i].find('xrun:') != -1 and lines[i].find('VLGERR') != -1:
                        break
                    err_cou += 1
                    if err_cou == 1:
                        err_position = i+1
                        self.print_message_on_terminal('\ndisplay up to 3 compile errors:', is_error=True)
                        self.print_message_on_terminal('-------------------------------------------------------------------')
                    self.print_message_on_terminal(lines[i-3].replace('\n', ''), is_error=True)
                    self.print_message_on_terminal(lines[i-2].replace('\n', ''), is_error=True)
                    self.print_message_on_terminal(lines[i-1].replace('\n', ''), is_error=True)
                    self.print_message_on_terminal(lines[i].replace('\n', ''), is_error=True)
                    self.print_message_on_terminal('-------------------------------------------------------------------')
                elif lines[i].find('[final_phase]') != -1:
                    break

                if err_cou == 3:
                    break



            for i in range(len(lines)):
                if lines[i].find('UVM_ERROR') != -1 or lines[i].find('UVM_FATAL') != -1:
                    uvm_err_cou += 1
                    if uvm_err_cou == 1:
                        uvm_err_position = i+1
                        self.print_message_on_terminal('\ndisplay up to 3 uvm errors:', is_error=True)
                        self.print_message_on_terminal('-------------------------------------------------------------------')
                    self.print_message_on_terminal(lines[i-3].replace('\n', ''), is_error=True)
                    self.print_message_on_terminal(lines[i-2].replace('\n', ''), is_error=True)
                    self.print_message_on_terminal(lines[i-1].replace('\n', ''), is_error=True)
                    self.print_message_on_terminal(lines[i].replace('\n', ''), is_error=True)
                    self.print_message_on_terminal('-------------------------------------------------------------------')
                elif lines[i].find('[final_phase]') != -1:
                    break

                if uvm_err_cou == 3:
                    break

        else:
            self.print_message_on_terminal('no dpic.log', is_error=True)

        os.system('mv ' + self.pattern_filename + self.mv_dir_name_ + ' ' + self.pattern_filename + self.mv_dir_name + ' > /dev/null 2>&1')
        os.system('mv ' + self.pattern_filename + self.ncargs_name_ + ' ' + self.pattern_filename + self.ncargs_name + ' > /dev/null 2>&1')
        # self.exit_flag = True
        # self.wait_main_thread = True
        # os.system('echo press any key to continue')
        # key_interupt_thread.join()

        self.reset_var()
        os.system('echo pyrun_run out')
        # raise KeyboardInterrupt
        # key_interupt_thread.terminate()



class pyrun_regression:
    def __init__(self):
        self.ascii_list = []
        self.exit_flag = False
        self.wait_main_thread = False
        self.moved_file = False
        self.key_inter = ''
        self.pattern_filename = ''
        self.mv_dir_name = '/xcelium.d/'
        self.mv_dir_name_ = '/xcelium.tmp/'
        self.ncargs_name = '/ncargs'
        self.ncargs_name_ = '/ncargs_tmp'
        self.DEFAULT_PATTERN = 'i2s_sample_rate_48k_test'
        self.DEFAULT_SEED = '0'

    def reset_var(self):
        self.ascii_list = []
        self.exit_flag = False
        self.wait_main_thread = False
        self.moved_file = False


    def func(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def get(self):
        while(1):
            k = self.func()
            if k != '':
                break

        if not self.exit_flag:
            self.ascii_list.append(ord(k))
            # print(self.ascii_list)

            if len(self.ascii_list) == 1 and self.ascii_list[0] == 3:    # press ctrl+c
                self.ascii_list.pop(0)
                self.exit_flag = True
                if os.path.isfile('pyrun_regression.tmpfile') == False:
                    f = open('pyrun_regression.tmpfile', 'w')
                    f.close()
            else:
                # for item in self.ascii_list:
                #   print(item)
                for i in range(len(self.ascii_list)):
                    self.ascii_list.pop(0)

    def detect_key(self):
        self.ascii_list = []
        while(True):
            self.get()
            if self.exit_flag:
                # if self.wait_main_thread:
                #     self.reset_var()
                #     break
                if not self.moved_file:
                    print('mv operator')
                    os.system('mv ' + self.pattern_filename + self.mv_dir_name + ' ' + self.pattern_filename + self.mv_dir_name_)
                    os.system('mv ' + self.pattern_filename + self.ncargs_name + ' ' + self.pattern_filename + self.ncargs_name_)
                    self.moved_file = True



    def check_global(self):
        time.sleep(5)
        while(True):
            time.sleep(0.5)
            # print(process_share_value.value)
            if process_share_value.value == 1:
            # if os.path.isfile('pyrun_regression.tmpfile'):
                if not self.moved_file:
                    # print('mv operator')
                    os.system('mv ' + self.pattern_filename + self.mv_dir_name + ' ' + self.pattern_filename + self.mv_dir_name_ + ' > /dev/null 2>&1')
                    os.system('mv ' + self.pattern_filename + self.ncargs_name + ' ' + self.pattern_filename + self.ncargs_name_ + ' > /dev/null 2>&1')
                    self.moved_file = True
                break


    def do(self, cmd_str, multiprocess_id, value):
        self.reset_var()

        # key_interupt_thread = threading.Thread(target=self.detect_key)
        # key_interupt_thread.daemon = True
        # key_interupt_thread.start()

        check_thread = threading.Thread(target=self.check_global)
        check_thread.daemon = True
        check_thread.start()

        tc_name = self.DEFAULT_PATTERN
        seed = self.DEFAULT_SEED

        for item in cmd_str.split(' '):
            if item.startswith('SEED='):
                seed = item[len('SEED='):]
            if item.startswith('TC_NAME='):
                tc_name = item[len('TC_NAME='):]



        # p1 = Popen(['pwd'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        # stdout, stderr = p1.communicate()
        # # print(stdout)
        # new_stdout = stdout.decode('UTF-8')
        new_stdout = os.getcwd()
        # os.system('echo now dir:' + new_stdout)
        if new_stdout.replace('\n', '').split('/')[-1] == 'run':   # if in run/ dir
            self.pattern_filename = new_stdout.replace('\n', '') + '/' + tc_name + '_' + seed
        else:                                                      # in pattern dir
            self.pattern_filename = new_stdout.replace('\n', '')

        # print(self.pattern_filename)

        os.system('echo ' + cmd_str)
        os.system(cmd_str + ' > /dev/null')


        os.system('mv ' + self.pattern_filename + self.mv_dir_name_ + ' ' + self.pattern_filename + self.mv_dir_name + ' > /dev/null 2>&1')
        os.system('mv ' + self.pattern_filename + self.ncargs_name_ + ' ' + self.pattern_filename + self.ncargs_name + ' > /dev/null 2>&1')
        # self.exit_flag = True
        # self.wait_main_thread = True
        # os.system('echo press any key to continue')
        # key_interupt_thread.join()

        self.reset_var()
        os.system('touch ' + str(multiprocess_id) + '_dont_touch.tmpfile')




ascii_list = []
exit_flag = False
DEFAULT_PATTERN = 'i2s_sample_rate_48k_test'
DEFAULT_SEED = '0'


def key_interupt():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def get_key():
    while(1):
        k = key_interupt()
        if k != '':
            break

    ascii_list.append(ord(k))
    # print(ascii_list)

    if len(ascii_list) == 1 and ascii_list[0] == 3:    # press ctrl+c
        ascii_list.pop(0)
        if process_share_value.value == 0:
            print('got ctrl-c, please wait')
            process_share_value.value = 1
            # if os.path.isfile('pyrun_regression.tmpfile') == False:
            #     f = open('pyrun_regression.tmpfile', 'w')
            #     f.close()
            # print(process_share_value.value)

    elif len(ascii_list) == 1 and ascii_list[0] == 115:    # press s
        ascii_list.pop(0)
        if process_share_press_s.value == 0:
            process_share_press_s.value = 1
    else:
        # for item in self.ascii_list:
        #   print(item)
        for i in range(len(ascii_list)):
            ascii_list.pop(0)

def for_thread():
    while(True):
        get_key()
        if exit_flag:
            break

def show_mpstat():
    while(True):
        if exit_flag:
            break
        p2 = Popen(['mpstat'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        stdout, stderr = p2.communicate()
        lines = stdout.split('\n')
        print(lines[2])
        print(lines[3])
        # os.system('ps -ef > ps.tmp')
        time.sleep(10)

if __name__=='__main__':

    process_share_value = Value('i', 0)
    process_share_press_s = Value('i', 0)

    p2 = Popen(['mpstat'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    stdout, stderr = p2.communicate()
    lines = stdout.split('\n')
    cpu_name = lines[0].split(' ')[2]

    # print(sys.argv)
    cmd_list = sys.argv[:]
    is_regression = False
    cfg_file = ''

    if cmd_list[1] == 'single':
        # print('single mode')
        cmd_list.remove('single')
    elif cmd_list[1] == 'multi':
        # print('regression mode')
        cfg_file = cmd_list[2]
        is_regression = True

    t1 = threading.Thread(target=for_thread)
    t1.start()
    # t2 = threading.Thread(target=show_mpstat)
    # t2.start()

    if is_regression:
        cmd_lst    = []
        with open(cfg_file, 'r') as cfg_f:
            cmd_lst = cfg_f.readlines()

        cmd_dict = {}

        cmd_key_list    = []
        result_cmd_list = []

        for item in cmd_lst[::-1]:
            tc_name = DEFAULT_PATTERN
            seed = DEFAULT_SEED

            argv = item.split()
            argv = [x for x in argv if x != 'make']
            # argv.remove('make')

            cmd_list = argv[:]
            # print(cmd_list)

            for arg in argv[:]:
                if arg.find('=') == -1:  # dont find '='
                    tc_name = arg.split('/')[-1].split('.')[0]
                    cmd_list.remove(arg)
                else:
                    if arg.startswith('TC_NAME='):
                        tc_name = arg[len('TC_NAME='):]
                        cmd_list.remove(arg)
                    elif arg.startswith('SEED='):
                        seed = arg[len('SEED='):]

            cmd_dict_key = tc_name + '_' + seed
            cmd_str = ''
            cmd_str += 'make TC_NAME=' + tc_name + ' SEED=' + seed
            for cmd in cmd_list:
                if cmd.startswith('SEED='):
                    pass
                else:
                    cmd_str += ' ' + cmd

            if cmd_dict_key not in cmd_key_list:
                cmd_key_list.append(cmd_dict_key)
                result_cmd_list.append(cmd_str)
            # print(cmd_dict_key)
            # print(cmd_str)
            # print(cmd_dict)

        result_cmd_list = result_cmd_list[::-1]
        print('Scheduled cmd list:')
        for item in result_cmd_list:
            print('    ' + item)
        print('\n====================== Running ======================\n')

        thread_lst = []
        max_process_num = 2
        for i in range(len(result_cmd_list)):
            if i >= max_process_num:
                while(True):
                    time.sleep(1)
                    cnt = 0
                    for proc in thread_lst:
                        if proc.is_alive():
                            cnt += 1
                    if cnt < max_process_num:
                        break
            if process_share_value.value == 1:
                break
            new_class = pyrun_regression()
            # new_thread = threading.Thread(target=new_class.do, args=('useless_str ' + command + ' NOGRID=1', ))
            thread_lst.append(mp.Process(target=new_class.do, args=(result_cmd_list[i] + ' NOGRID=1', i, process_share_value, )))
            thread_lst[i].start()


        for t in thread_lst:
            t.join()
    else:
        new_class = pyrun_run()
        # new_class.do(cmd_list)
        new_thread = mp.Process(target=new_class.do, args=(cmd_list,))
        new_thread.start()
        new_thread.join()

    exit_flag = True
    print('press any key to continue')

    t1.join()
    # t2.join()