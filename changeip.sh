#!/bin/sh
#Simple script that remove the default address and set the one send by param: $1 should be CIDR EX: 10.61.116.56/24
# Syntax: ./changeip.sh 192.168.1.1/24 192.168.1.254
ip addr del 172.16.1.200/24 dev ens33
ip route del default
ip addr add $1 dev ens33
ip route add default via $2
