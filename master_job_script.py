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
import random
import time
import itertools
import machines
from collections import deque

cpu_info = {}
jobs = deque()
workers = []
worker_status = {}
available_workers = []
POLL_INTERVAL = 30  # seconds
UPPER_BOUND = 15
JOB_SECS = 3600 * 8 * 2 # FIXME: make sensible!

def parse_cores(cpu_str): return int(cpu_str.split("x")[0])

def num_virt_cores(machine_name):
    ht_scale_factor = 2 if "Xeon" in cpu_info[machine_name][machines.TYPE] else 1
    virt_cpu_num = parse_cores(cpu_info[machine_name][machines.CPU]) * ht_scale_factor
    return virt_cpu_num

def invoke(worker, job, randsleep):
    print('{}, {} started'.format(worker, job))
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect(worker+'.cs.colostate.edu')
        cmd = '/s/chopin/a/grad/lakinsm/cs_cluster/cs_env/bin/python3 /s/chopin/a/grad/lakinsm/cs_cluster/jobs.py {} {} {}'.format(job, randsleep, num_virt_cores(worker))
        stdin, stdout, stderr = c.exec_command(cmd)
        return c, stdin, stdout, stderr
    except (paramiko.ssh_exception.NoValidConnectionsError, TimeoutError, paramiko.ssh_exception.SSHException):
        return False


def is_complete(filename):
    if len(filename) == 1:
        filename = filename[0]
    if not os.path.isfile(filename):
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
        return deque((x for x in j.read().split() if x and not \
            is_complete('/home/lakinsm/hmm_testing/cs_cluster_files/output/project7/groupIII/{}'.format(x.replace('.fasta', '.tblout.scan')))))


def init_workers(job_queue):
    for w in workers:
        if job_queue:
           job = job_queue.popleft()
           try:
               c, stdin, stdout, stderr = invoke(w, job, UPPER_BOUND)
           except (ValueError, TypeError):
               job_queue.append(job)
               continue
           worker_status[w] = [job, c, stdin, stdout, stderr, time.time()]


if __name__ == '__main__':
    cpu_info = {entry[0]: entry for entry in machines.machines}
    initjobs = load_initial_jobs(sys.argv[2])
    workers = load_workers(sys.argv[1])
    workers = [x for x in workers if x in cpu_info]
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
                if not is_complete('/home/lakinsm/hmm_testing/cs_cluster_files/output/project7/groupIII/{}'.format(v[0].replace('.fasta', '.tblout.scan'))):
                    print('{} error: {}'.format(k, v[4].readlines()))
                    print('{} not completed successfully in {:.3f} seconds on {} cores, requeuing...'.format(v[0], time.time() - v[5], num_virt_cores(k)))
                    jobs.append(v[0])
                else:
                    print('{} completed successfully in {:.3f} seconds on {} cores.'.format(v[0], time.time() - v[5], num_virt_cores(k)))
                print('{}, {} job finished'.format(k, v[0]))
                worker_status[k] = []
                available_workers.append(k)
            elif w_status and k not in available_workers:
                worker_status[k] = []
                available_workers.append(k)
        random.shuffle(available_workers)
        while jobs and available_workers:
            job = jobs.popleft()
            worker = available_workers.pop()
            try:
                c, stdin, stdout, stderr = invoke(worker, job, 0)
                worker_status[worker] = [job, c, stdin, stdout, stderr, time.time()]
            except (ValueError, TypeError):
                jobs.append(job)
                continue
        time.sleep(POLL_INTERVAL)
