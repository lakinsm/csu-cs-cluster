#!/usr/bin/env python3

import sys

with open(sys.argv[1], 'r') as f:
    data = f.read().split('\n')
    for entry in data:
        if not entry:
            continue
        entry = entry.split()
        try:
            if float(entry[8]) < 3:
                sys.stdout.write(entry[0].split('.')[0]+'\n')
        except IndexError:
            if float(entry[6]) < 3:
                sys.stdout.write(entry[0].split('.')[0]+'\n')


