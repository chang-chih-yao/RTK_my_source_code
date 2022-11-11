from __future__ import print_function
from __future__ import division
from subprocess import Popen, PIPE
import sys
import os
import time
import multiprocessing as mp
import threading
import tty, termios
import signal
import math

QUEUE_NAME = 'cpuq'
TMPFILE_DIR = 'tmp_file/'

ascii_list = []
exit_flag = False
ctrl_c_flag = False

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
    #global ctrl_c_flag
    while(1):
        k = key_interupt()
        if k != '':
            break

    ascii_list.append(ord(k))
    # print(ascii_list)

    if len(ascii_list) == 1 and ascii_list[0] == 3:    # press ctrl+c
        ascii_list.pop(0)
        # if ctrl_c_flag == False:
        #     print('got ctrl-c, please wait')
        #     p1.terminate()
        #     print('all process terminated')
        #     ctrl_c_flag = True

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




def signal_handler(signal, frame):
    global ctrl_c_flag
    print('wait all grid out')
    os_result = os.system('test -f ' + tmp_file)   # if os_result == 0 means file exists
    if os_result != 0 and ctrl_c_flag == False:
        os.system('touch ' + tmp_file)
        ctrl_c_flag = True
        raise KeyboardInterrupt

def detect_ctrl_c():
    global ctrl_c_flag
    os_result = os.system('test -f ' + tmp_file)
    if os_result == 0:
        ctrl_c_flag = True
        return True
    else:
        return False

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def run_regression(cfg_file, id, max_process_num, grid_name):
    if grid_name == 'auto':
        cmd = 'qrsh -q {} -now N -pty y -l m_mem_free=2g -cwd "python {}python_src/qrsh_regression.py multi {} {} {}"'.format(QUEUE_NAME, verification_dir, cfg_file, id, max_process_num)    
        # cmd = 'qrsh -q cpuq -now N -pty y -l m_mem_free=2g -cwd "python ' + verification_dir + 'python_src/qrsh_regression.py multi ' + cfg_file + ' ' + id + ' ' + max_process_num + '"'   
        os.system(cmd + ' 2> /dev/null')
    else:
        # cmd = 'qrsh -now N -pty y -cwd "python ' + verification_dir + 'python_src/pyrun_py2_test.py multi ' + cfg_file + ' ' + id + ' ' + max_process_num + '"'
        # os.system(cmd + ' 1> /dev/null 2>&1')

        cmd = 'qrsh -q {}@{} -now N -pty y -l m_mem_free=2g -cwd "python {}python_src/qrsh_regression.py multi {} {} {}"'.format(QUEUE_NAME, grid_name, verification_dir, cfg_file, id, max_process_num)
        # cmd = 'qrsh -q cpuq@' + grid_name + ' -now N -pty y -l m_mem_free=2g -cwd "python ' + verification_dir + 'python_src/qrsh_regression.py multi ' + cfg_file + ' ' + id + ' ' + max_process_num + '"'
        # print(cmd)
        os.system(cmd + ' 2> /dev/null')
        # os.system(cmd)

        # print(cmd)
        # os.system(cmd)

        # os.system(cmd + ' 2>/dev/null')
        # os.system(cmd + ' > /dev/null 2>&1')

def is_comment(my_str):
    if my_str.replace('\t', '').strip().startswith('//'):
        return True
    elif my_str.replace('\t', '').strip().startswith('#'):
        return True
    else:
        return False

def merge_sub_regression_report():
    all_sub_regression_report = os.listdir(TMPFILE_DIR)
    all_pattern_status = []
    all_pattern_status_sort = []
    all_pattern_grid_status = []
    for regression_report in all_sub_regression_report:
        p2 = Popen(['cat',  TMPFILE_DIR+regression_report], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        stdout, stderr = p2.communicate()
        pattern_status_start = False
        for item in stdout.split('\n'):
            if pattern_status_start and item != '':
                all_pattern_status.append(item)
            else:
                if item.startswith('-'):
                    all_pattern_grid_status.append(item)
                elif item.startswith('='):
                    pattern_status_start = True

    for item in all_pattern_status:
        if item.find('RUNNING') != -1:
            all_pattern_status_sort.append(item)
    for item in all_pattern_status:
        if item.find('WAITING') != -1:
            all_pattern_status_sort.append(item)
    for item in all_pattern_status:
        if item.find('PASSED') != -1:
            all_pattern_status_sort.append(item)
    for item in all_pattern_status:
        if item.find('NO_DPIC_LOG') != -1:
            all_pattern_status_sort.append(item)
    for item in all_pattern_status:
        if item.find('UNKNOWN_FAILED') != -1:
            all_pattern_status_sort.append(item)
    for item in all_pattern_status:
        if item.find('COMPILE_FAILED') != -1:
            all_pattern_status_sort.append(item)
    for item in all_pattern_status:
        if item.find('SIM_FAILED') != -1:
            all_pattern_status_sort.append(item)


    with open('regression_report', 'w') as f:
        for item in all_pattern_grid_status:
            f.write(item + '\n')

        f.write('===========================================' + '\n')

        for item in all_pattern_status_sort:
            f.write(item + '\n')


def gen_running_pattern(all_pattern_name_list):
    merge_sub_regression_report()
    with open('regression_report', 'r') as fp:
        report_str = fp.read()
    f_write = open('running_pattern', 'w')
    for item in all_pattern_name_list:
        if item not in report_str:
            f_write.write(item + '\n')
    f_write.close()

def check_qrsh_on_grid():
    all_on_grid_pass = False
    now_grid_list = []
    now_job_id_list = []
    not_on_grid_list = []
    for a in range(6):
        time.sleep(20)
        merge_sub_regression_report()
        print('------------------------------')
        p2 = Popen(['cat', 'regression_report'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        stdout, stderr = p2.communicate()
        now_grid_list = []
        now_job_id_list = []
        not_on_grid_list = []
        all_on_grid = True
        for item in stdout.split('\n'):
            if item.startswith('-'):
                now_grid_list.append(item.split(' ')[0].replace('-', ''))
                now_job_id_list.append(item.split(' ')[1])
        for i in range(len(divide_pattern_cmd)):
            if grid_name_list[i] not in now_grid_list:
                print('{} not on grid'.format(grid_name_list[i]))
                not_on_grid_list.append(grid_name_list[i])
                all_on_grid = False

        if all_on_grid:
            print('all qrsh on grid')
            print('------------------------------')
            all_on_grid_pass = True
            break
    return all_on_grid_pass, not_on_grid_list

def find_grid_jb_ID_list():
    grid_jb_ID_list = []
    not_on_grid_job_ID_list = []
    while(True):
        p3 = Popen(['grid', '--sj'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        stdout, stderr = p3.communicate()
        stdout_lines = stdout.split('\n')
        grid_jb_ID_list = []
        start_flag = False
        for i in range(len(stdout_lines)):
            if start_flag == True and stdout_lines[i].startswith('-') == False:
                if len(stdout_lines[i].split()) == 7:
                    # stdout_lines[i]  str format is like this -> "143233030 xrun_regression.py  R7227   r   10/05/2022 15:53:36  rtq@jj057"
                    if stdout_lines[i].split()[6] == '1':                   # grid --sj [6] is queue name
                        not_on_grid_job_ID_list.append(stdout_lines[i].split()[0])
                grid_jb_ID_list.append(stdout_lines[i].split()[0])
            if stdout_lines[i].startswith('-'):
                if start_flag == True:
                    break
                else:
                    start_flag = True
        # print(grid_jb_ID_list)
        if len(grid_jb_ID_list) == 1 and grid_jb_ID_list[0].startswith('No'):
            print('retry grid --sj')
        else:
            break

    return grid_jb_ID_list, not_on_grid_job_ID_list

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('args error')
        exit()

    signal.signal(signal.SIGINT, signal_handler)

    process_list = []        # for multi process list

    cfg_file = sys.argv[1]
    tmp_file = cfg_file.split('.')[0] + '.tmpfile'

    print('read cfg_file name =', cfg_file)
    with open(cfg_file, 'r') as f:
        lines = f.readlines()

    try:
        now_pwd = os.getcwd()
        pwd_list = now_pwd.split('/')
        rtl_sim_position = 0
        for i in range(len(pwd_list)):
            if pwd_list[i].find('rtl_sim') != -1:
                rtl_sim_position = i
        # print(rtl_sim_position)
        now_dir_to_rtl_sim_len = len(pwd_list) - rtl_sim_position -1
        rtl_sim_dir = '../' * now_dir_to_rtl_sim_len

        os.chdir(rtl_sim_dir)
        # print(os.getcwd())
        if os.path.isdir('regression_' + cfg_file.split('.')[0]):
            print('folder exists, do you want to overwrite(rm -rf)? (y/n)')
            c = raw_input()
            if c == 'y' or c == 'Y':
                print('rm -rf regression_' + cfg_file.split('.')[0] + '/    please wait...')
                r = os.system('rm -rf regression_' + cfg_file.split('.')[0])
                if r != 0:
                    exit()
                os_cmd = 'mkdir regression_' + cfg_file.split('.')[0]
                # print(os_cmd)
                os.system(os_cmd)
            else:
                exit()
        else:
            os_cmd = 'mkdir regression_' + cfg_file.split('.')[0]
            # print(os_cmd)
            os.system(os_cmd)

        os.chdir('regression_' + cfg_file.split('.')[0])
        # print(os.getcwd())
        os.system('cp ../run/Makefile .')
        os.system('mkdir {}'.format(TMPFILE_DIR))
        os.system('ln -sf ../regression/coverage coverage') # no link?
        os.system('ln -sf ../regression/template template')
        os.system('echo "===========================================" > regression_report')

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


        # t1 = threading.Thread(target=for_thread)
        # t1.start()

        grid_num = 0
        for line in lines:
            if line.find('grid') != -1 and is_comment(line) == False:
                # print('|'+line.split('=')[-1].replace('\t', '').strip()+'|')
                grid_num = int(line.split('=')[-1].replace('\t', '').strip())
                print('grid_num =', grid_num)
                break

        max_process_num = 0
        for line in lines:
            if line.find('max_process_num') != -1 and is_comment(line) == False:
                # print('|'+line.split('=')[-1].replace('\t', '').strip()+'|')
                max_process_num = int(line.split('=')[-1].replace('\t', '').strip())
                print('max_process_num =', max_process_num)
                break

        NOFSDB = -1
        for line in lines:
            if line.find('NOFSDB') != -1 and is_comment(line) == False:
                # print('|'+line.split('=')[-1].replace('\t', '').strip()+'|')
                NOFSDB = int(line.split('=')[-1].replace('\t', '').strip())
                if NOFSDB != 0 and NOFSDB != 1:
                    print('NOFSDB variable set error, must be 0 or 1')
                    exit()
                print('NOFSDB =', NOFSDB)
                break

        COV_ENABLE = -1
        for line in lines:
            if line.find('COV_ENABLE') != -1 and is_comment(line) == False:
                # print('|'+line.split('=')[-1].replace('\t', '').strip()+'|')
                COV_ENABLE = int(line.split('=')[-1].replace('\t', '').strip())
                if COV_ENABLE != 0 and COV_ENABLE != 1:
                    print('COV_ENABLE variable set error, must be 0 or 1')
                    exit()
                print('COV_ENABLE =', COV_ENABLE)
                break

        pattern_cmd = []
        all_pattern_name_list = []
        find_flag = False
        for line in lines:
            if find_flag:
                if len(line.replace('\t', '').strip().split(',')) == 4 and is_comment(line) == False:
                    pattern_name = line.replace('\t', '').strip().split(',')[0].replace('\t', '').strip()
                    pattern_seed = line.replace('\t', '').strip().split(',')[1].replace('\t', '').strip()
                    pattern_nofsdb = line.replace('\t', '').strip().split(',')[2].replace('\t', '').strip()
                    pattern_cov = line.replace('\t', '').strip().split(',')[3].replace('\t', '').strip()
                    if NOFSDB != -1:                           # if user set global control
                        pattern_nofsdb = str(NOFSDB)
                    if COV_ENABLE != -1:                       # if user set global control
                        pattern_cov = str(COV_ENABLE)
                    my_cmd = 'make TC_NAME=' + pattern_name + ' SEED=' + pattern_seed + ' NOFSDB=' + pattern_nofsdb + ' COV=' + pattern_cov
                    pattern_cmd.append(my_cmd)
                    all_pattern_name_list.append(pattern_name + '_' + pattern_seed)
            if line.find('testcase') != -1 and is_comment(line) == False:
                find_flag = True

        # print(all_pattern_name_list)

        each_grid_cmd_len = int(math.ceil(len(pattern_cmd) / grid_num))           # the number of commands per grid
        divide_pattern_cmd = list(divide_chunks(pattern_cmd, each_grid_cmd_len))
        # ex:  6 commands, 2 grid
        # divide_pattern_cmd = [[cmd_1, cmd_2, cmd_3], [cmd_4, cmd_5, cmd_6]]
        # print(divide_pattern_cmd)



        p1 = Popen(['python', '/rsc/R7227/.local/open/check_qhost.py', QUEUE_NAME, 'regression', str(len(divide_pattern_cmd))], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        stdout, stderr = p1.communicate()
        grid_name_list = stdout.split('\n')
        print(grid_name_list)
        if len(grid_name_list)-1 != len(divide_pattern_cmd) or grid_name_list[0] == '':
            print('cpus are busy')
            exit()

        # exit()
    except KeyboardInterrupt:
        os.system('rm -rf ' + tmp_file)
        exit()


    if ctrl_c_flag == False:
        try:
            sub_cfg_name_list = []
            for i in range(len(divide_pattern_cmd)):         # len(divide_pattern_cmd) is grid num
                sub_cfg_name = sys.argv[1].split('.')[0] + '.grid_' + grid_name_list[i]
                sub_cfg_name_list.append(sub_cfg_name)
                with open(sub_cfg_name, 'w') as f:
                    for item in divide_pattern_cmd[i]:
                        f.write(item + '\n')

                p1 = mp.Process(target=run_regression, args=(sub_cfg_name, str(i), str(max_process_num), grid_name_list[i]))
                p1.daemon = True
                process_list.append(p1)
                p1.start()
                time.sleep(1)


            all_on_grid_pass, not_on_grid_list = check_qrsh_on_grid()

            if not all_on_grid_pass:
                print('GG')

                grid_jb_ID_list, not_on_grid_job_ID_list = find_grid_jb_ID_list()

                qdel_list = 'qdel'
                for item in not_on_grid_job_ID_list:
                    qdel_list += ' ' + item
                os.system(qdel_list + ' 1> /dev/null 2>&1')

                while(1):

                    grid_jb_ID_list, not_on_grid_job_ID_list = find_grid_jb_ID_list()
                    if len(not_on_grid_job_ID_list) == 0:
                        print('qdel finished')
                        break
                    else:
                        print('wait qdel finish')
                    time.sleep(5)

                for j in range(len(not_on_grid_list)):
                    sub_cfg_name = sys.argv[1].split('.')[0] + '.grid_' + not_on_grid_list[j]
                    sub_cfg_name_list.remove(sub_cfg_name)
                    new_sub_cfg_name = sys.argv[1].split('.')[0] + '.grid_auto_' + str(j)
                    os.system('mv ' + sub_cfg_name + ' ' + new_sub_cfg_name)
                    sub_cfg_name_list.append(new_sub_cfg_name)

                    p1 = mp.Process(target=run_regression, args=(new_sub_cfg_name, str(i), str(max_process_num), 'auto'))
                    p1.daemon = True
                    process_list.append(p1)
                    p1.start()
                    time.sleep(1)

            # os.system('touch rerun.cfg')

            time_cou = 0
            while(True):
                time.sleep(1)
                if detect_ctrl_c():
                    break

                if time_cou == 0:          # 5sec check one time
                    gen_running_pattern(all_pattern_name_list=all_pattern_name_list)
                time_cou = (time_cou+1)%5

                cnt = 0
                for proc in process_list:
                    if proc.is_alive():
                        cnt += 1
                # print(cnt)
                if cnt == 0:
                    print('all processes successfully join in main thread')
                    break

        except KeyboardInterrupt:
            ctrl_c_flag = True



    # except (KeyboardInterrupt, IOError):
    if ctrl_c_flag == True:
        print("caught Ctrl-C!!!  clear up threads")

        t2 = threading.Thread(target=for_thread)   # cancel ctrl+c effect
        t2.start()

        grid_jb_ID_list, not_on_grid_job_ID_list = find_grid_jb_ID_list()

        for item in process_list:
            item.terminate()

        merge_sub_regression_report()
        p4 = Popen(['cat', 'regression_report'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        stdout, stderr = p4.communicate()
        if stderr == '':    # no error (regression_report exist)
            now_job_id_list = []
            # all_on_grid = True
            for item in stdout.split('\n'):
                if item.startswith('-'):
                    now_job_id_list.append(item.split(' ')[1])
            # print(now_job_id_list)

            qdel_list = 'qdel'
            for item in grid_jb_ID_list:
                if item in now_job_id_list:
                    qdel_list += ' ' + item

        if qdel_list != 'qdel':
            print(qdel_list)
            os.system(qdel_list + ' 1> /dev/null 2>&1')


        for item in sub_cfg_name_list:
            os.system('rm -rf ' + item)

        gen_running_pattern(all_pattern_name_list=all_pattern_name_list)

        exit_flag = True
        print('press any key')
        t2.join()

        print('all threads terminated')
    else:
        gen_running_pattern(all_pattern_name_list=all_pattern_name_list)
        # merge_sub_regression_report()   # gen_running_pattern() will merge_sub_regression_report
        with open('regression_report', 'r') as f:
            regression_report_lines = f.readlines()

        find_sim_failed_and_nofsdb = False
        all_pattern_pass = True
        sim_failed_pattern_name_and_seed = ''
        sim_failed_pattern_name = ''
        for item in regression_report_lines:
            if item.find('PASSED') == -1:
                all_pattern_pass = False
                if item.find('SIM_FAILED') != -1:
                    sim_failed_pattern_name_and_seed = item.split()[0]
                    # print('sim_failed_pattern_name_and_seed', sim_failed_pattern_name_and_seed)
                    for sub_cfg_item in sub_cfg_name_list:
                        with open(sub_cfg_item, 'r') as fp:
                            sub_cfg_lines = fp.readlines()
                        for sub_cfg_line in sub_cfg_lines:
                            sub_cfg_pattern_name_and_seed = sub_cfg_line.split()[1].split('=')[-1] + '_' + sub_cfg_line.split()[2].split('=')[-1]
                            if sub_cfg_pattern_name_and_seed == sim_failed_pattern_name_and_seed and sub_cfg_line.find('NOFSDB=1') != -1:
                                find_sim_failed_and_nofsdb = True
                                # print('find!!', sub_cfg_line)
                                sim_failed_pattern_name = sub_cfg_line.split()[1].split('=')[-1]
                                break
                        if find_sim_failed_and_nofsdb:
                            break
                    if find_sim_failed_and_nofsdb:
                        break


        for item in sub_cfg_name_list:
            os.system('rm -rf ' + item)


        if sim_failed_pattern_name_and_seed == '' and all_pattern_pass:
            print('all patterns PASSED !!!')
        else:
            print('\033[91m' + 'some patterns FAILED' + '\033[0m')
            if find_sim_failed_and_nofsdb:
                pass
                # print('make TC_NAME=' + sim_failed_pattern_name + ' SEED=auto_dump_fsdb NOFSDB=0 COV=0')
                # os.system('make TC_NAME=' + sim_failed_pattern_name + ' SEED=auto_dump_fsdb NOFSDB=0 COV=0' + ' 1>/dev/null 2>&1')
                # print('make done!')



    os.system('rm -rf ' + tmp_file)
    print('main thread finish')
