from __future__ import print_function
import os
import sys
from subprocess import PIPE, Popen
import time

pyrun_script_dir = sys.argv[0].split('qrsh_regression')[0]
cmd = 'python {}regression_core.py {} {} {} {}'.format(pyrun_script_dir, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])


# p2 = Popen(['mpstat'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
# stdout, stderr = p2.communicate()
# lines = stdout.split('\n')
# cpu_name = lines[0].split(' ')[2]

# p3 = Popen(['printenv', 'JOB_ID'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
# stdout, stderr = p3.communicate()
# job_id = stdout.split('\n')[0]

# dump_to_log_msg = cpu_name + ' ' + job_id

# print(dump_to_log_msg)
# time.sleep(999)

# print(cmd)
os.system(cmd + ' 2> /dev/null')
# os.system(cmd)