#!/usr/bin/python
import re
import itertools

def mysplit(line):
    groups = itertools.groupby(line, lambda k: k == '\t')
    runs = ["".join(vals) for k,vals in groups]
    fields = [run for run in runs if run[0] != '\t']
    return fields

machines = []
for lnum, line in enumerate(open("servers/2017_machines.txt")):
    if lnum > 1:
        fields = mysplit(line.strip()) # re.split(r"\s+", line.strip())
        if len(fields) >= 7:
            machines.append(fields)


#print( "found", len(machines), "machines")
# NAME		TYPE			CPU	MEM	OS		USE	LOCATION	S/N		MAC ADDRESS
#execfile("usedmachines.py")
NAME = 0
TYPE = 1
CPU = 2
MEM = 3
OS = 4
USE = 5
LOCATION = 6
sn = 7


labs = ['478-storage',
        '475-machine-rm',
        '225-interac-lab',
        '215-interac-lab',
        '120-unix-lab']

morelabs = [    
'478-systems',
'325-hpc-lab',
'215-interac-lab',
'225-interac-lab',
# '315-netsec-lab',
# '478-storage',
# '405-storage',
'120-unix-lab',
'110-open-lab',
'475-machine-rm',
]

STRs = {
    "XeonE5-2650v2" : 1619,
    "XeonE3-1230" : 1823,
    "Xeon3450" : 1168,
    "Xeon5450" : 1274,
    "Xeon5450-SAS" : 1274,
    "X4100-amd254" : 889,
    "AMD-6386SE" : 988,
    "XeonE7-4830" : 1700,
    "AMD-6220" : 1062,
    "XeonE3-1231v3" : 2170,
    "XeonE5-1650v3" : 2116,
    "HP-DL160-G5" : 1149
}    


def get_STR(machine):
    typestring = machine[TYPE]
    "Get the single thread rating as an int"
    for k,v in STRs.items():
        if typestring[-len(k):] == k: return v
    raise Exception("STR not found", str(machine))


CPUs = 0
inset = 0
#goodmachines = set([ 'HP-xw6600-Xeon5450-SAS', 'HP-Z210-XeonE3-1230', 'HP-Z220-XeonE3-12230', 'HP-z420-XeonE5-2650v2'])
if __name__ == '__main':
    for machine in machines:
        if machine[OS] == 'Linux(Fedora)' and machine[NAME][0:len('lattice')] != 'lattice' and  machine[LOCATION] in morelabs:
        #print(machine[CPU], "\t\t", machine[MEM], "\t\t", machine[TYPE], get_STR(machine)) #machine[TYPE],
            print(machine[NAME])
            inset += 1
#     #    print machine[CPU]

#     if machine[NAME] in usedmachines: 
#         touse = int(machine[CPU][0]) - 1
#         inset += touse
#         print "    '" + machine[NAME] + "' : " + str(touse) + ","
#         #print machine[TYPE], machine[CPU], machine[MEM]

            mobj = re.search(r"^(\d+)x", machine[CPU])
            if mobj:
                CPUs += int(mobj.group(1))
#         #if machine[OS] == 'Linux(64)' and machine[USE] == 'general' and "(" not in  machine[NAME] and machine[LOCATION] in labs and machine[TYPE] == 'HP-xw4600-Core2Duo-SATA':# and machine[TYPE] in goodmachines:
#          #print  "    '" + machine[TYPE] + "' : 2," # machine[NAME], "\t\t\t",
#     #     print machine
# #        print machine[LOCATION]




#print( "all available CPUs:", CPUs)
#print( "in set", inset)
