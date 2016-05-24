#!/usr/bin/env python3

## Load a list of worker machines from valid_machines.txt
## Load a list of job definitions (file, start, stop)

## Need: check function -> take job description, return whether completed successfully
## Need: control function, jobs placed in queue, if jobs not complete, put back in queue


## To do list:
# Write the is_completed function (the check function)
# Write print status in various locations
# Write jobs.py for the local job spinup
# (For later) write a module for statuses and check functions



import paramiko
import sys
import os
import re
import time
from collections import deque

jobs = deque()
workers = []
worker_status = {}
POLL_INTERVAL = 10  # seconds
UPPER_BOUND = 0

def invoke(worker, job, randsleep):
    print('{}, {} started'.format(worker, job))
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(worker+'.cs.colostate.edu')
    cmd = '/s/chopin/a/grad/lakinsm/cs_cluster/cs_env/bin/python3 /s/chopin/a/grad/lakinsm/cs_cluster/jobs.py {} {}'.format(job, randsleep)
    print(cmd)
    stdin, stdout, stderr = c.exec_command(cmd)
    return c, stdin, stdout, stderr


def is_complete(filename):
    if len(filename) == 1:
        filename = filename[0]
    if not os.path.isfile(filename):
        print('file not found, {}'.format(filename))
        return False
    with open(filename, 'rb') as f:
        f.seek(-5, 2)
        status = f.read(5)
    return True if status.rstrip() == b'[ok]' else False


def load_workers(workerdefs):
    """Load in list of workers"""
    with open(workerdefs, 'r') as w:
        return [x for x in w.read().split() if w]


def load_initial_jobs(jobdefs):
    """Load the intiial jobs"""
    with open(jobdefs, 'r') as j:
        return deque((x for x in j.read().split() if x and not is_complete(x)))


def init_workers(job_queue):
    for w in workers:
        if job_queue:
           job = job_queue.popleft()
           c, stdin, stdout, stderr = invoke(w, job, UPPER_BOUND)
           worker_status[w] = [job, c, stdin, stdout, stderr]


if __name__ == '__main__':
    initjobs = load_initial_jobs(sys.argv[2])
    workers = load_workers(sys.argv[1])
    for i in initjobs:
        if not is_complete(i):
            jobs.append(i)
    
    init_workers(jobs)

    ## While there are jobs not finished; in queue or associated with worker
    while jobs or any(x for x in worker_status.values()):
        for k, v in worker_status.items():
            ## FIXME: Timeout inside jobs file; if job hangs, exit
            try:
                w_status = v[2].channel.closed
            except IndexError:
                w_status = True
            if w_status and v:
                #print(w_status, v[1])
                if not is_complete('/home/lakinsm/hmm_testing/cs_cluster_files/output/pediatric/{}'.format(v[0].replace('.fasta', '.tblout.scan'))):
                    print('{} error: {}'.format(k, v[3].readlines()))
                    print('{} not completed, requeuing...'.format(v[0]))
                    jobs.append(v[0])
                print('{}, {} complete'.format(k, v[0]))
                worker_status[k] = []
                if jobs:
                    job = jobs.popleft()
                    c, stdin, stdout, stderr = invoke(k, job, 0)
                    worker_status[k] = [job, c, stdin, stdout, stderr]
            elif w_status and jobs:
                    job = jobs.popleft()
                    c, stdin, stdout, stderr = invoke(k, job, 0)
                    worker_status[k] = [job, c, stdin, stdout, stderr]
        time.sleep(POLL_INTERVAL)
