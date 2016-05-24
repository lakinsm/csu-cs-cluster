#!/usr/bin/env python3

import os
import sys
import subprocess
import random
import time
import psutil
import socket
import paramiko
import scp
import shutil
import multiprocessing
import sh
import resource


def is_complete(filename):
    if len(filename) == 1:
        filename = filename[0]
    if not os.path.isfile(filename):
        return False
    with open(filename, 'rb') as f:
        f.seek(-5, 2)
        status = f.read(5)
    return True if status.rstrip() == b'[ok]' else False


# CPU, dirname, outputfile, dirname, dirname, inputfile
HMMER_CMD = '/s/chopin/a/grad/lakinsm/cs_cluster/hmmer/binaries/nhmmer --dna --notextw --cpu {} --tblout {}/outputfiles/{} {}HMMs/mmarc_groupI.hmm {}inputfiles/{} > /dev/null'

#resource.setrlimit(resource.RLIMIT_CPU, 3600)

os.nice(19)
psutil.Process().ionice(psutil.IOPRIO_CLASS_IDLE)

_, fastafile, randsleep = sys.argv

time.sleep(random.randint(0,int(randsleep)))

outname = fastafile.replace('.fasta', '.tblout.scan')
cpu = int(sys.argv[3])
dirname = '/s/{}/a/tmp/'.format(socket.gethostname())

shutil.rmtree(dirname+'inputfiles', ignore_errors=True)
os.makedirs(dirname+'inputfiles')

shutil.rmtree(dirname+'outputfiles', ignore_errors=True)
os.makedirs(dirname+'outputfiles')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('abdoserver2.cvmbs.colostate.edu')

scp = scp.SCPClient(c.get_transport())
scp.get('/home/lakinsm/hmm_testing/cs_cluster_files/parts/pediatric/{}'.format(fastafile), dirname+'inputfiles/{}'.format(fastafile))

## FIXME: check to see if models are intact/present

p = subprocess.Popen(HMMER_CMD.format(cpu, dirname, outname, dirname, dirname, fastafile), stderr=subprocess.PIPE, shell=True)

stderrlines = list(p.stderr)
sys.stderr.write('\n'.join(stderrlines)+'\n')
p.wait()

if is_complete(dirname+'outputfiles/{}'.format(outname)):
    scp.put(dirname+'outputfiles/{}'.format(outname), '/home/lakinsm/hmm_testing/cs_cluster_files/output/pediatric/{}'.format(outname))

scp.close()
c.close()





