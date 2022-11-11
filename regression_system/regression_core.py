#!/bin/python
from __future__ import print_function
from __future__ import division
import os
from subprocess import Popen, PIPE, STDOUT
import sys
import codecs
import threading
import signal
import multiprocessing as mp
from multiprocessing import Value, Manager
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
        self.key_inter = ''
        self.pattern_dir_absolute_path = ''
        self.cmd = ''
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
        RED   = '\\e[1;31m '
        WHITE = '\\e[1;37m '
        RST   = '\\e[0m '

        color = RED if is_error else WHITE
        os.system('echo -e "' + color + message + RST + '"')

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
                    os.system('mv ' + self.pattern_dir_absolute_path + self.mv_dir_name + ' ' + self.pattern_dir_absolute_path + self.mv_dir_name_)
                    os.system('mv ' + self.pattern_dir_absolute_path + self.ncargs_name + ' ' + self.pattern_dir_absolute_path + self.ncargs_name_)
                    self.moved_file = True

    '''
    def detect_key():
    global key_inter, kill_flag
    while(True):
        key_inter = raw_input()
        print('press crtl-c')
        # if key_inter == '1':
        #   os.system('echo ready to exit')
        #   while(True):
        #     os.system('mv ' + pattern_dir_absolute_path + mv_dir_name + ' ' + pattern_dir_absolute_path + mv_dir_name_)
        #     os.system('mv ' + pattern_dir_absolute_path + ncargs_name + ' ' + pattern_dir_absolute_path + ncargs_name_)
        #     time.sleep(2)
        #     if kill_flag == 1:
        #       break
        if kill_flag == 1:
        break
    '''

    def for_multi(self):
        os.system(self.cmd)

    def check_global(self):
        time.sleep(5)
        while(True):
            time.sleep(1)
            # if os.path.isfile('pyrun_regression.tmpfile'):
            if process_share_value.value == 1:
                if not self.moved_file:
                    print('mv operator')
                    os.system('mv ' + self.pattern_dir_absolute_path + self.mv_dir_name + ' ' + self.pattern_dir_absolute_path + self.mv_dir_name_ + ' > /dev/null 2>&1')
                    os.system('mv ' + self.pattern_dir_absolute_path + self.ncargs_name + ' ' + self.pattern_dir_absolute_path + self.ncargs_name_ + ' > /dev/null 2>&1')
                    self.moved_file = True
                break

    def do(self, my_argv):
        self.reset_var()

        # key_interupt_thread = multiprocessing.Process(target = self.detect_key)
        # key_interupt_thread = threading.Thread(target=self.detect_key)
        # key_interupt_thread.daemon = True
        # key_interupt_thread.start()

        check_thread = threading.Thread(target=self.check_global)
        check_thread.daemon = True
        check_thread.start()

        tc_name = self.DEFAULT_PATTERN
        seed = self.DEFAULT_SEED

        # my_argv = my_str.split()

        cmd_list = my_argv[1:]

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


        cmd_str = ''
        cmd_str += 'make TC_NAME=' + tc_name
        for cmd in cmd_list:
            cmd_str += ' ' + cmd


        # p1 = Popen(['pwd'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        # stdout, stderr = p1.communicate()
        # # print(stdout)
        # new_stdout = stdout.decode('UTF-8')
        new_stdout = os.getcwd()
        # os.system('echo now dir:' + new_stdout)
        if new_stdout.replace('\n', '').split('/')[-1] == 'run':   # if in run/ dir
            self.pattern_dir_absolute_path = new_stdout.replace('\n', '') + '/' + tc_name + '_' + seed
        else:                                                      # in pattern dir
            self.pattern_dir_absolute_path = new_stdout.replace('\n', '')

        # print(self.pattern_dir_absolute_path)

        os.system('echo ' + cmd_str)
        self.cmd = cmd_str
        os.system(cmd_str)
        # key_interupt_thread = multiprocessing.Process(target = self.detect_key)
        # key_interupt_thread.start()
        # time.sleep(10)
        # key_interupt_thread.terminate()



        if os.path.isfile(self.pattern_dir_absolute_path + '/dpic.log'):
            f = codecs.open(self.pattern_dir_absolute_path + '/dpic.log', 'r', errors = 'ignore')
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

        os.system('mv ' + self.pattern_dir_absolute_path + self.mv_dir_name_ + ' ' + self.pattern_dir_absolute_path + self.mv_dir_name + ' > /dev/null 2>&1')
        os.system('mv ' + self.pattern_dir_absolute_path + self.ncargs_name_ + ' ' + self.pattern_dir_absolute_path + self.ncargs_name + ' > /dev/null 2>&1')
        # self.exit_flag = True
        # self.wait_main_thread = True
        # os.system('echo press any key to continue')
        time.sleep(1)
        # key_interupt_thread.join()

        self.reset_var()
        os.system('echo pyrun out')
        # raise KeyboardInterrupt
        # key_interupt_thread.terminate()



class pyrun_regression:
    def __init__(self):
        self.ascii_list = []
        self.exit_flag = False
        self.wait_main_thread = False
        self.moved_file = False
        self.xrun_cmd = ''
        self.key_inter = ''
        self.pattern_dir_absolute_path = ''
        self.pattern_name_seed = ''
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
                    os.system('mv ' + self.pattern_dir_absolute_path + self.mv_dir_name + ' ' + self.pattern_dir_absolute_path + self.mv_dir_name_)
                    os.system('mv ' + self.pattern_dir_absolute_path + self.ncargs_name + ' ' + self.pattern_dir_absolute_path + self.ncargs_name_)
                    self.moved_file = True



    def check_global(self):
        time.sleep(5)
        while(True):
            time.sleep(1)
            # print(process_share_value.value)
            if process_share_value.value == 1:
            # if os.path.isfile('pyrun_regression.tmpfile'):
                if not self.moved_file:
                    # print('mv operator')
                    os.system('mv ' + self.pattern_dir_absolute_path + self.mv_dir_name + ' ' + self.pattern_dir_absolute_path + self.mv_dir_name_ + ' > /dev/null 2>&1')
                    os.system('mv ' + self.pattern_dir_absolute_path + self.ncargs_name + ' ' + self.pattern_dir_absolute_path + self.ncargs_name_ + ' > /dev/null 2>&1')
                    self.moved_file = True
                break


    def do(self, cmd_str, multiprocess_id, value, process_share_list, process_share_dict):
        self.reset_var()
        origin_cmd_str = cmd_str

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

        self.pattern_name_seed = tc_name + '_' + seed

        new_stdout = os.getcwd()
        # print('now_pwd : {}  ({})'.format(new_stdout, multiprocess_id))
        # if new_stdout.replace('\n', '').split('/')[-1] == 'run':   # if in run/ dir
        #     self.pattern_dir_absolute_path = new_stdout.replace('\n', '') + '/' + tc_name + '_' + seed
        # else:                                                      # in pattern dir
        #     print('you are not in run/ dir')
        #     exit()
        self.pattern_dir_absolute_path = new_stdout.replace('\n', '') + '/' + tc_name + '_' + seed   # pattern dir full path

        # print(self.pattern_dir_absolute_path)
        cmd_str += ' python_nogrid'
        # os.system('echo ' + cmd_str)
        # os.system(cmd_str + ' > /dev/null')




        p1 = Popen(cmd_str, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p1.communicate()
        makefile_output = stdout.split('\n')
        dpic_name = ''
        try:
            for i in range(len(makefile_output)):
                if makefile_output[i].startswith('xrun'):
                    self.xrun_cmd = makefile_output[i]
                    dpic_name = makefile_output[i+1]
                    # print(self.xrun_cmd)
                    break
        except:
            print('makefile cmd error')
            exit()

        if self.xrun_cmd == '':
            print('makefile cmd error')
            exit()

        os.chdir(self.pattern_dir_absolute_path)     # go to pattern dir

        find_index = 0
        for i in range(len(process_share_list)):
            if process_share_list[i].find(self.pattern_name_seed) != -1:
                find_index = i
                break
        process_share_list[find_index] = '{:<80s}{:<15s}{:<10s}'.format(self.pattern_name_seed, 'RUNNING', '0h:0m')
        # process_share_list.append('{:<80s}{:<15s}{:<10s}'.format(self.pattern_name_seed, 'RUNNING', '0h:0m'))
        process_share_dict[self.pattern_name_seed] = int(time.time())
        # os.system(self.xrun_cmd + ' | tee ' + dpic_name)
        os.system('stdbuf -oL ' + self.xrun_cmd + ' | tee ' + dpic_name + ' 1>/dev/null 2>&1')




        pattern_result = -1     # 0: pass, 1: fail, 2: compile error, 3: unknown error
        if os.path.isfile(self.pattern_dir_absolute_path + '/dpic.log'):
            f = codecs.open(self.pattern_dir_absolute_path + '/dpic.log', 'r', errors = 'ignore')
            dpic_log = f.read()
            f.close()

            if 'Testcase Status: PASSED' in dpic_log:
                pattern_result = 0
            elif 'Testcase Status: FAILED' in dpic_log or 'UVM_FATAL' in dpic_log or '*F' in dpic_log :
                pattern_result = 1
            elif ': *E' in dpic_log or ': *F' in dpic_log:
                pattern_result = 2
            else:
                pattern_result = 3


        find_index = 0
        for i in range(len(process_share_list)):
            if process_share_list[i].find(self.pattern_name_seed) != -1:
                find_index = i
                break
        t = process_share_list[find_index].split()[2]  # time
        if pattern_result == 0:
            print('{:<80s}{:<15s}'.format(self.pattern_name_seed, 'PASSED'))
            # os.system('echo ' + '"{:<80s}{:<10s}"'.format(self.pattern_name_seed, 'PASSED') + ' >> ../{}regression_report_{}'.format(TMPFILE_DIR, cpu_name))
            process_share_list[find_index] = '{:<80s}{:<15s}{:<10s}'.format(self.pattern_name_seed, 'PASSED', t)
        elif pattern_result == -1:
            print('\033[91m' + '{:<80s}{:<15s}'.format(self.pattern_name_seed, 'NO_DPIC_LOG') + '\033[0m')
            # os.system('echo ' + '"{:<80s}{:<15s}"'.format(self.pattern_name_seed, 'no dpic.log') + ' >> ../{}regression_report_{}'.format(TMPFILE_DIR, cpu_name))
            process_share_list[find_index] = '{:<80s}{:<15s}{:<10s}'.format(self.pattern_name_seed, 'NO_DPIC_LOG', t)
            os.system('echo ' + '"{}"'.format(origin_cmd_str) + ' >> ../rerun.cfg')
        elif pattern_result == 1:
            print('\033[91m' + '{:<80s}{:<15s}'.format(self.pattern_name_seed, 'SIM_FAILED') + '\033[0m')
            # os.system('echo ' + '"{:<80s}{:<10s}"'.format(self.pattern_name_seed, 'SIM_FAILED') + ' >> ../{}regression_report_{}'.format(TMPFILE_DIR, cpu_name))
            process_share_list[find_index] = '{:<80s}{:<15s}{:<10s}'.format(self.pattern_name_seed, 'SIM_FAILED', t)
            os.system('echo ' + '"{}"'.format(origin_cmd_str) + ' >> ../rerun.cfg')
        elif pattern_result == 2:
            print('\033[91m' + '{:<80s}{:<15s}'.format(self.pattern_name_seed, 'COMPILE_FAILED') + '\033[0m')
            # os.system('echo ' + '"{:<80s}{:<10s}"'.format(self.pattern_name_seed, 'COMPILE_FAILED') + ' >> ../{}regression_report_{}'.format(TMPFILE_DIR, cpu_name))
            process_share_list[find_index] = '{:<80s}{:<15s}{:<10s}'.format(self.pattern_name_seed, 'COMPILE_FAILED', t)
            os.system('echo ' + '"{}"'.format(origin_cmd_str) + ' >> ../rerun.cfg')
        elif pattern_result == 3:
            print('\033[91m' + '{:<80s}{:<15s}'.format(self.pattern_name_seed, 'UNKNOWN_FAILED') + '\033[0m')
            # os.system('echo ' + '"{:<80s}{:<10s}"'.format(self.pattern_name_seed, 'UNKNOWN_FAILED') + ' >> ../{}regression_report_{}'.format(TMPFILE_DIR, cpu_name))
            process_share_list[find_index] = '{:<80s}{:<15s}{:<10s}'.format(self.pattern_name_seed, 'UNKNOWN_FAILED', t)
            os.system('echo ' + '"{}"'.format(origin_cmd_str) + ' >> ../rerun.cfg')




        os.system('mv ' + self.pattern_dir_absolute_path + self.mv_dir_name_ + ' ' + self.pattern_dir_absolute_path + self.mv_dir_name + ' > /dev/null 2>&1')
        os.system('mv ' + self.pattern_dir_absolute_path + self.ncargs_name_ + ' ' + self.pattern_dir_absolute_path + self.ncargs_name + ' > /dev/null 2>&1')
        # self.exit_flag = True
        # self.wait_main_thread = True
        # os.system('echo press any key to continue')
        # key_interupt_thread.join()

        self.reset_var()


def key_interupt():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

ascii_list = []
exit_flag = False
DEFAULT_PATTERN = 'i2s_sample_rate_48k_test'
DEFAULT_SEED = '0'
TMPFILE_DIR = 'tmp_file/'

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
            # if os.path.isfile('pyrun_regression.tmpfile') == False:
            #     f = open('pyrun_regression.tmpfile', 'w')
            #     f.close()
            # print(process_share_value.value)
            process_share_value.value = 1

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

'''
check_tmp_file_flag = False
def check_tmp_file(tmp_file, process_id):
    while(True):
        try:
            time.sleep(1)
            if os.path.isfile(tmp_file):
                for item in thread_lst:
                    item.terminate()
                    item.join()
                print('all process join  ({})'.format(process_id))
                break
            if check_tmp_file_flag:
                break
        except Exception as e:
            print(e)
            print('pyrun_py2_test.py got ctrl-c in check_tmp_file   ({})'.format(process_id))

            if not os.path.isfile(tmp_file):
                with open(tmp_file, 'w') as fp:
                    pass
                for t in thread_lst:
                    t.terminate()
                    t.join()
                print('all process join  ({})'.format(process_id))

    print('check_tmp_file  end   ({})'.format(process_id))
'''

ctrl_c_flag = False
def signal_handler(signal, frame):
    global ctrl_c_flag
    print('pyrun_py2_test.py got ctrl-c')
    os_result = os.system('test -f ' + tmp_file)   # if os_result == 0 means file exists
    if os_result != 0 and ctrl_c_flag == False:
        os.system('touch ' + tmp_file)
        ctrl_c_flag = True
        # raise KeyboardInterrupt

def update_regression_report(process_share_list, process_share_dict):
    while(1):
        now_time = int(time.time())
        for i in range(len(process_share_list)):
            if len(process_share_list[i].split()) == 3:
                t0 = process_share_dict[process_share_list[i].split()[0]]
                my_sec = now_time - t0
                my_min = int(my_sec/60)%60
                my_hour = int(my_sec/3600)
                time_log = '{}h:{}m'.format(my_hour, my_min)
                if process_share_list[i].split()[1] == 'RUNNING':   # calculate time on RUNNING status
                    process_share_list[i] = '{:<80s}{:<15s}{:<10s}'.format(process_share_list[i].split()[0], 'RUNNING', time_log)

        with open('{}regression_report_{}'.format(TMPFILE_DIR, cpu_name), 'w')as f:
            for item in process_share_list:
                f.write(item + '\n')
        if exit_flag:
            break
        time.sleep(5)

if __name__=='__main__':
    signal.signal(signal.SIGINT, signal_handler)

    # p1 = Popen(['lscpu'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    # stdout, stderr = p1.communicate()
    # lines = stdout.split('\n')
    # for line in lines:
    #     if line.find('Model name:') != -1:
    #         # print(line)
    #         if line.find('6146') != -1:
    #             print('Intel 6146, core 12')
    #         elif line.find('6246') != -1:
    #             print('Intel 6246R, core 16')
    #         elif line.find('6346') != -1:
    #             print('Intel 6346, core 16')
    #         else:
    #             print(line)
    time.sleep(2)

    manager = Manager()
    process_share_value = Value('i', 0)
    process_share_list = manager.list()
    process_share_dict = manager.dict()

    p2 = Popen(['mpstat'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    stdout, stderr = p2.communicate()
    lines = stdout.split('\n')
    cpu_name = lines[0].split(' ')[2].replace('(', '').replace(')', '')

    p3 = Popen(['printenv', 'JOB_ID'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    stdout, stderr = p3.communicate()
    job_id = stdout.split('\n')[0]

    dump_to_log_msg = '-' + cpu_name + ' ' + job_id
    os.system('echo "===========================================" > {}regression_report_{}'.format(TMPFILE_DIR, cpu_name))
    os.system("sed -i '1 i\\{}' {}regression_report_{}".format(dump_to_log_msg, TMPFILE_DIR, cpu_name))
    # print(cpu_name)
    process_share_list.append(dump_to_log_msg)
    process_share_list.append('===========================================')

    p4 = Popen('top -b -n1 -u root | grep Cpu', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p4.communicate()
    # print(stdout.split())
    cpu_idle_percentage = float(stdout.split()[7])    # idle% = cpu_us% + cpu_sy%
    if cpu_idle_percentage < 15.0:
        limit_process_num = 1   # cpu 85% up
    elif cpu_idle_percentage < 20.0:
        limit_process_num = 2   # cpu 80-85%
    elif cpu_idle_percentage < 30.0:
        limit_process_num = 5   # cpu 70-80%
    elif cpu_idle_percentage < 40.0:
        limit_process_num = 10  # cpu 60-70%
    elif cpu_idle_percentage < 50.0:
        limit_process_num = 15  # cpu 50-60%
    elif cpu_idle_percentage < 60.0:
        limit_process_num = 20  # cpu 40-50%
    elif cpu_idle_percentage < 70.0:
        limit_process_num = 25  # cpu 30-40%
    else:
        limit_process_num = 32  # cpu 0-30%

    # time.sleep(1)

    # print(sys.argv)
    cmd_list = sys.argv[:]
    is_regression = False
    cfg_file = ''
    process_id = ''
    max_process_num = 2
    thread_lst = []
    max_process_num_change = False

    if cmd_list[1] == 'single':
        # print('single mode')
        cmd_list.remove('single')
    elif cmd_list[1] == 'multi':
        # print('regression mode')
        cfg_file = cmd_list[2]
        process_id = cmd_list[3]
        max_process_num = int(cmd_list[4])
        if max_process_num > limit_process_num:
            max_process_num = limit_process_num
            max_process_num_change = True
        tmp_file = cfg_file.split('.')[0] + '.tmpfile'
        is_regression = True



    # t1 = threading.Thread(target=for_thread)
    # t1.start()
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
        # print('Scheduled cmd list:')
        # for item in result_cmd_list:
        #     print('    ' + item)

        if max_process_num_change:
            print('\033[91m' + '\n====================== Running On Grid {}  cpu_core_usage:{} ======================'.format(cpu_name, max_process_num) + '\033[0m')
        else:
            print('\n====================== Running On Grid {}  cpu_core_usage:{} ======================'.format(cpu_name, max_process_num))

        for item in result_cmd_list:
            print(item)
            name = item.split()[1].split('=')[-1]
            seed = item.split()[2].split('=')[-1]
            process_share_list.append('{:<80s}{:<15s}{:<10s}'.format(name + '_' + seed, 'WAITING', cpu_name))
            process_share_dict[name + '_' + seed] = int(time.time())

        check_regression_report_thread = threading.Thread(target=update_regression_report, args=(process_share_list, process_share_dict))
        check_regression_report_thread.start()

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
            # if process_share_value.value == 1:
            #     break
            os_result = os.system('test -f ' + tmp_file)
            if os_result == 0:
                break
            new_class = pyrun_regression()
            thread_lst.append(mp.Process(target=new_class.do, args=(result_cmd_list[i] + ' NOGRID=1', i, process_share_value, process_share_list, process_share_dict, )))
            thread_lst[i].daemon = True
            thread_lst[i].start()
            time.sleep(1)

        # detector = mp.Process(target=check_tmp_file, args=(tmp_file, process_id))
        # detector.start()

        # try:
        while(True):
            time.sleep(1)
            # print('pyrun_py2 while loop waiting   ({})'.format(process_id))
            os_result = os.system('test -f ' + tmp_file)
            if os_result == 0:
            # if os.path.isfile(tmp_file):
                for t in thread_lst:
                    t.terminate()
                # print('detect file. all process terminate  ({})'.format(process_id))
                break

            cnt = 0
            for proc in thread_lst:
                if proc.is_alive():
                    cnt += 1
            if cnt == 0:
                # print('all process success join  ({})'.format(process_id))
                break

        exit_flag = True
        check_regression_report_thread.join()

        # except (KeyboardInterrupt, IOError):
        #     print('pyrun_py2_test.py got ctrl-c  ({})'.format(process_id))
        #     if not os.path.isfile(tmp_file):
        #         with open(tmp_file, 'w') as fp:
        #             pass
        #         for t in thread_lst:
        #             t.terminate()
        #         print('all process join  ({})'.format(process_id))
            # raise KeyboardInterrupt

        # check_tmp_file_flag = True
        # detector.join()
        # print('detector join   ({})'.format(process_id))

    else:
        new_class = pyrun_run()
        # new_class.do(cmd_list)
        new_thread = mp.Process(target=new_class.do, args=(cmd_list,))
        new_thread.start()
        new_thread.join()


    # print('press any key to continue')

    # print('pyrun_py2_test.py  done  {}'.format(cpu_name))

    # t1.join()
    # t2.join()