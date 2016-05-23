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



import Queue
import paramiko
import sys
import os
import re
import time

jobs = Queue.Queue()
workers = []
worker_status = {}
POLL_INTERVAL = 300  # seconds


def invoke(worker, job):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(worker)
    _, stdout, _ = c.exec_command('python3 job.py {}'.format(job))
    return stdout


def is_completed(job):
    """Check output file for existence then completion"""
    pass


def load_initial_jobs(jobdefs):
    """Load the intiial jobs"""
    with open(jobdefs, 'r') as j:
        return initlist = j.read().split()


def init_workers(job_queue):
    for w in workers:
        if not job_queue.empty():
           job = job_queue.get()
           stdout = invoke(w, job)
           worker_status[w] = (job, stdout)


if __name__ == '__main__':
    initjobs = load_initial_jobs(sys.argv[1])
    for i in initjobs:
        if not is_completed(i):
            jobs.put(i)
    
    init_workers(jobs)

    ## While there are jobs not finished; in queue or associated with worker
    while not jobs.empty() or worker_status:
        for k, v in worker_status.items():
            w_status = v[1].channel.exit_status_ready()
            if w_status:
                if not is_completed(v[0]):
                    jobs.put(v[0])
                del worker_status[k]
            if not jobs.empty():
                job = jobs.get()
                worker_status[k] = (job, invoke(k, job))
        time.sleep(POLL_INTERVAL)
