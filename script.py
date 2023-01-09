# Script pour config de tous les routeurs

import getpass
import sys
import telnetlib

HOST = "192.168.122.71"
user = raw_input("Enter your telnet username: ")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until("Username: ")
tn.write(user + "\n")
if password:
    tn.read_until("Password: ")
    tn.write(password + "\n")

tn.write("enable\n")
tn.write("cisco\n")
tn.write("conf t\n")
tn.write("int gigabitEthernet 1/0\n")
tn.write("ip address 192.168.22.2 255.255.255.0\n") #A configurer les addresses ip (surement argv)
tn.write("no shutdown\n")
tn.write("int gigabitEthernet 2/0\n")
tn.write("ip address 192.168.27.1 255.255.255.0\n") #A configurer les addresses ip (surement argv)
tn.write("no shutdown\n")
tn.write("int gigabitEthernet 3/0\n")
tn.write("ip address 192.168.25.2 255.255.255.0\n") #A configurer les addresses ip (surement argv)
tn.write("no shutdown\n")

#OSPF

tn.write("router ospf 1\n")
tn.write("network 192.168.22.2 0.0.0.0 area 0\n")
tn.write("network 192.168.27.1 0.0.0.0 area 0\n")
tn.write("network 192.168.25.2 0.0.0.0 area 0\n")

#BGP

tn.write("router bgp 300\n")

tn.write("end\n")
tn.write("exit\n")
