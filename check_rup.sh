#/usr/bin/env bash

rup > temp_rup.txt
cat 12June2016_machines.txt | while read n; do grep "$n" temp_rup.txt; done
exit 0

