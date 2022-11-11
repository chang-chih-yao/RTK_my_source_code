from __future__ import print_function
from operator import le
import os
import sys
from subprocess import Popen, PIPE, STDOUT
import random

class check_qhost:
    def __init__(self):
        self.find_flag = False
        self.start_idx = 99999
        self.result_server = []
        self.server_rank = []

    def find_queue_type(self, my_str):
        if len(sys.argv) <= 1:
            print('args error')
            exit()
        if sys.argv[1] == 'rtq':
            if my_str.find(' rtq ') != -1:
                return True
        elif sys.argv[1] == 'cpuq':
            if my_str.find(' cpuq ') != -1:
                return True
        elif sys.argv[1] == 'all':
            if my_str.find(' rtq ') != -1 or my_str.find(' cpuq ') != -1:
                return True
        elif sys.argv[1] == 'midq':
            if my_str.find(' midq ') != -1:
                return True
        else:
            print('args error')
            exit()

    def find_host(self):
        p1 = Popen(['qhost', '-q'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        stdout, stderr = p1.communicate()
        # print(stdout)
        lines = stdout.split('\n')
        # print(len(lines))


        for i in range(len(lines)):
            if lines[i].find('BIP') != -1:            # queue info
                if self.find_queue_type(lines[i]):
                    if len(lines[i].split()) == 3:    # len == 4 means that queue has special status
                        now_use_num = int(lines[i].split()[2].split('/')[1])
                        max_use_num = int(lines[i].split()[2].split('/')[2])
                        if max_use_num - now_use_num != 0:
                            self.find_flag = True
            else:                                     # host
                if i - self.start_idx > 1 and self.find_flag:
                    self.result_server.append(lines[self.start_idx])
                    #if lines[i].find('jj') != -1 or lines[i].find('jm') != -1:
                    # for j in range(self.start_idx, i):
                    #     print(lines[j])
                self.start_idx = i
                self.find_flag = False

        p2 = Popen(['qhost', '-F'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        stdout, stderr = p2.communicate()
        # print(stdout)
        qhost_cpu = stdout.split('\n')

        start_flag = False
        pivot_idx = 0
        for a in range(len(self.result_server)):
            for i in range(pivot_idx, len(qhost_cpu)):
                if qhost_cpu[i].find(self.result_server[a].split()[0]) != -1:
                    start_flag = True
                if start_flag:
                    if qhost_cpu[i].find('cpu=') != -1:
                        self.result_server[a] += '  ' + qhost_cpu[i].split('=')[-1]
                        start_flag = False
                        pivot_idx = i
                        break

        for item in self.result_server:
            # if float(item.split()[6]) > 60.0:
            if float(item.split()[11]) > 50.0:
                if len(sys.argv) == 3:
                    if sys.argv[2] == 'qq':
                        print('\033[95m' + item + '\033[0m')
            else:
                if len(sys.argv) == 3:
                    if sys.argv[2] == 'qq':
                        print(item)
                self.server_rank.append(item.split()[0])

        self.server_rank = self.server_rank[::-1]

        if len(sys.argv) == 3:
            if sys.argv[2] == 'qq':
                print('server rank: ')
                for item in self.server_rank:
                    print(item + ' ', end='')
                print()


        return self.server_rank

if __name__ == '__main__':
    my_check = check_qhost()
    rank = my_check.find_host()
    if len(rank) == 0:
        os.system('echo ""')
        exit()

    cpu_6346_list = []
    cpu_6246_list = []
    cpu_6146_list = []

    for i in range(len(rank)):
        if rank[i].find('jj') != -1 or rank[i].find('jm') != -1:
            cpu_6346_list.append(rank[i])
        if rank[i].find('ij') != -1 or rank[i].find('im') != -1 or rank[i].find('hj') != -1:
            cpu_6246_list.append(rank[i])
        if rank[i].find('gj') != -1 or rank[i].find('gm') != -1:
            cpu_6146_list.append(rank[i])

    # good_rank = cpu_6346_list + cpu_6246_list + cpu_6146_list

    if len(sys.argv) == 2:
        if len(cpu_6346_list) >= 2:
            random.shuffle(cpu_6346_list)
            # print(cpu_6346_list)
            os.system('echo ' + cpu_6346_list[0])
        elif len(cpu_6246_list) != 0:
            random.shuffle(cpu_6246_list)
            os.system('echo ' + cpu_6246_list[0])
        else:
            os.system('echo ' + rank[0])
    elif len(sys.argv) == 4:
        if sys.argv[2] == 'regression':
            if len(cpu_6346_list) >= int(sys.argv[3]):
                good_rank = cpu_6346_list
                random.shuffle(good_rank)
                for i in range(int(sys.argv[3])):
                    os.system('echo ' + good_rank[i])
            elif len(cpu_6346_list) + len(cpu_6246_list) >= int(sys.argv[3]):
                good_rank = cpu_6346_list + cpu_6246_list
                random.shuffle(good_rank)
                for i in range(int(sys.argv[3])):
                    os.system('echo ' + good_rank[i])
            elif len(cpu_6346_list) + len(cpu_6246_list) + len(cpu_6146_list) >= int(sys.argv[3]):
                good_rank = cpu_6346_list + cpu_6246_list + cpu_6146_list
                random.shuffle(good_rank)
                for i in range(int(sys.argv[3])):
                    os.system('echo ' + good_rank[i])
            else:
                if len(rank) >= int(sys.argv[3]):
                    for i in range(int(sys.argv[3])):
                        os.system('echo ' + rank[i])
                else:
                    for item in rank:
                        os.system('echo ' + item)