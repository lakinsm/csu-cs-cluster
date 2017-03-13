#!/usr/bin/env bash

shopt -s extglob

# $1 is the current date prefix

rup > servers/rup_machines_${1}.txt

./servers/get_free_machines.py servers/rup_machines_${1}.txt > servers/proposed_machines_${1}.txt

comm -12 <( sort -u servers/2017_general_machines.txt ) <( sort -u servers/proposed_machines_${1}.txt ) > ${1}_machines.txt

echo "/s/chopin/a/grad/lakinsm/uftp-4.9.2/uftp ~/meta-marc/src/HMMs -E ~/meta-marc/src/HMMs -R 50000 -D HMMs" > servers/${1}_send_models.sh

cat servers/${1}_machines.txt | while read mac; do echo "${mac}.cs.colostate.edu '/s/chopin/a/grad/lakinsm/uftp-4.9.2/uftpd -D /s/${mac}/a/tmp'"; done > servers/${mac}_start_servers.sh

cat servers/${1}_machines.txt | while read mac; do echo "${mac}.cs.colostate.edu 'killall uftpd'"; done > servers/${mac}_kill_servers.sh

chmod +x servers/${1}_start_servers.sh
chmod +x servers/${1}_kill_servers.sh

./servers/${1}_start_servers.sh

./servers/${1}_send_models.sh

exit 0

