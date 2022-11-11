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
from verilog_checker import verilog_check as verilog_check
# import configparser

class pyrun_run_compile_check:
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


    def check_global(self):
        time.sleep(5)
        while(True):
            time.sleep(1)
            if process_share_value.value == 1:
                if not self.moved_file:
                    print('mv operator')
                    os.system('mv ' + self.pattern_filename + self.mv_dir_name + ' ' + self.pattern_filename + self.mv_dir_name_ + ' > /dev/null 2>&1')
                    os.system('mv ' + self.pattern_filename + self.ncargs_name + ' ' + self.pattern_filename + self.ncargs_name_ + ' > /dev/null 2>&1')
                    self.moved_file = True
                break

    def do(self, my_argv):
        self.reset_var()

        check_thread = threading.Thread(target=self.check_global)
        check_thread.daemon = True
        check_thread.start()

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
        # print('------------------------------------------------')
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
                    # print(self.xrun_cmd)
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
        os.system('stdbuf -oL ' + self.xrun_cmd + ' | tee ' + dpic_name + ' > /dev/null 2>&1')


        err_cou = 0
        err_position = 1
        uvm_err_cou = 0
        uvm_err_position = 1
        if os.path.isfile(self.pattern_filename + '/dpic.log'):
            f = codecs.open(self.pattern_filename + '/dpic.log', 'r', errors = 'ignore')
            lines = f.readlines()
            f.close()

            for i in range(len(lines)):
                if lines[i].find('*F') != -1:
                    err_cou += 1
                elif lines[i].find('*E') != -1:
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
            process_share_value_fail.value = 1


        if err_cou > 0 or uvm_err_cou > 0:
            process_share_value_fail.value = 1


        os.system('mv ' + self.pattern_filename + self.mv_dir_name_ + ' ' + self.pattern_filename + self.mv_dir_name + ' > /dev/null 2>&1')
        os.system('mv ' + self.pattern_filename + self.ncargs_name_ + ' ' + self.pattern_filename + self.ncargs_name + ' > /dev/null 2>&1')
        # self.exit_flag = True
        # self.wait_main_thread = True
        # os.system('echo press any key to continue')
        time.sleep(1)
        # key_interupt_thread.join()

        self.reset_var()
        # os.system('echo pyrun out')
        # raise KeyboardInterrupt
        # key_interupt_thread.terminate()




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

def get_key():
    global ctrl_c_flag
    while(1):
        k = key_interupt()
        if k != '':
            break

    ascii_list.append(ord(k))
    # print(ascii_list)

    if len(ascii_list) == 1 and ascii_list[0] == 3:    # press ctrl+c
        ascii_list.pop(0)
        if process_share_value.value == 0:
            print('\ngot ctrl-c, please wait')
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


def check_svn():
    p1 = Popen(['svn', 'info', trunk_dir], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    stdout, stderr = p1.communicate()
    current_ver = 0
    # print(stdout)
    for line in stdout.split('\n'):
        if line.find('Revision') != -1:
            # print(line.replace(' ', '').split(':')[-1])
            current_ver = int(line.replace(' ', '').split(':')[-1])

    p2 = Popen(['svn', 'log', 'http://cadinfo/svn/PC/' + project_name, '-l', '1'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    svn_log, stderr = p2.communicate()
    newest_svn_log = svn_log.split('\n')[1]
    newest_ver = int(newest_svn_log.split('|')[0].replace(' ', '').replace('r', ''))
    t0 = time.time()
    t1 = t0 + 60*60*8
    GMT8_time = time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(t1))
    print_log = 'current svn version: {}  |  newest svn version: {}  |  {} '.format(current_ver, newest_ver, GMT8_time)
    sys.stdout.write('\r'+print_log)
    sys.stdout.flush()
    # print(print_log)
    current_ver_to_newest_ver_len = newest_ver - current_ver
    # print(current_ver_to_newest_ver_len)


    target_svn_log = ''
    if current_ver_to_newest_ver_len >= 1:
        print('\n')
        p3 = Popen(['svn', 'log', 'http://cadinfo/svn/PC/' + project_name, '-l', str(current_ver_to_newest_ver_len)], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        svn_log, stderr = p3.communicate()
        for line in svn_log.split('\n'):
            line_split = line.split('|')
            if len(line_split) == 4:
                if line_split[0].replace('r', '').replace(' ', '') == str(current_ver+1):
                    target_svn_log = line_split[1].ljust(30) + ' ' + line_split[2]

    return current_ver, current_ver_to_newest_ver_len, target_svn_log

if __name__=='__main__':
    # print(sys.argv)
    cmd_list = sys.argv[:]

    backward_dir = '../'

    pwd = os.getcwd()
    # print(pwd)
    if pwd.find('/project/') == -1:
        print('this directory is not project/')
        exit()
    project_name = pwd.split('/project/')[-1].split('/')[0]
    # print(project_name)

    t1 = threading.Thread(target=for_thread)
    t1.start()

    process_share_value = Value('i', 0)
    process_share_value_fail = Value('i', 0)


    pwd = os.getcwd()
    pwd_list = pwd.split('/')
    # print(pwd_list)
    trunk_position = 0
    for i in range(len(pwd_list)):
        if pwd_list[i].find('trunk') != -1:
            trunk_position = i
    # print(trunk_position)
    now_dir_to_trunk_len = len(pwd_list) - trunk_position -1
    trunk_dir = backward_dir * now_dir_to_trunk_len
    # print(now_dir_to_trunk_len)


    while(True):
        try:
            current_ver, current_ver_to_newest_ver_len, target_svn_log = check_svn()
        except:
            time.sleep(30)
            continue


        if current_ver_to_newest_ver_len >= 1:
            svn_up_cmd = 'svn up -r ' + str(current_ver+1) + ' ' + trunk_dir
            print(svn_up_cmd)
            os.system(svn_up_cmd)
            time.sleep(1)

            # exit()

            new_class = pyrun_run_compile_check()
            new_thread = mp.Process(target=new_class.do, args=(cmd_list,))
            new_thread.start()
            new_thread.join()


            write_file_msg = ''
            if process_share_value_fail.value == 0:
                write_file_msg = str(current_ver+1) + '  PASS  ' + target_svn_log
                # print('PASS')
            else:
                write_file_msg = str(current_ver+1) + '  FAIL  ' + target_svn_log
                # print('FAIL')

            print('\033[95m' + write_file_msg + '\033[0m')
            # print("sed -i '1 i\\{}' {}".format(write_file_msg, '/project/'+project_name+'/.workshop/R7227/compile_check.txt'))
            os.system("sed -i '1 i\\{}' {}".format(write_file_msg, '/project/'+project_name+'/.workshop/R7227/compile_check.txt'))
            if process_share_value_fail.value == 0:
                #verilog_check project_name,   current_ver,      dv, work_dir_name, svn_dir_name)
                verilog_check(project_name, current_ver+1, 'R7227',       'R7227', 'RL6903_compile_check')
            time.sleep(1)
        else:
            time.sleep(20)

        if process_share_value.value == 1:
            break

        process_share_value_fail.value = 0
        process_share_value.value = 0


    exit_flag = True
    print('press any key to continue')
    t1.join()
    process_share_value_fail.value = 0
    process_share_value.value = 0
    exit_flag = False

