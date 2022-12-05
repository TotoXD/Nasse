# Nasse

# I. Configurer MPLS à la main sur tout le réseau
	
	1. Ajouter des routers et des links

	2. Ajouter des switchs avec des PC derriere chaque CE/CS (peut être plus tard)

	3. Configurer une IP sur chacune des interfaces des routeurs

- Config pour chaque router
--------------------------------
configure terminal
interface gigabitEthernet 4/0
ip address 192.168.11.1 255.255.255.0
no shutdown
exit
exit
copy run start
-------------------------------- (Exemple pour plusieurs interfaces à la fois)
configure terminal
interface gigabitEthernet 1/0
ip address 192.168.22.2 255.255.255.0
no shutdown
exit
interface gigabitEthernet 2/0
ip address 192.168.27.1 255.255.255.0
no shutdown
exit
interface gigabitEthernet 3/0
ip address 192.168.25.2 255.255.255.0
no shutdown
exit
exit
copy run start
--------------------------------

- Commandes utiles:

(show neighbours)
configure terminal
do sho cdp nei

show running-config

(reset interface)
default interface gi 1/1

(save config)
copy run start


	4. Configure OSPF sur les routeurs et ajouter les routes

Config ospf sur les routeurs
------------------------------
configure terminal
router ospf 1
network 192.168.26.2 0.0.0.0 area 0
network 192.168.31.1 0.0.0.0 area 0
network 192.168.30.1 0.0.0.0 area 0
network 192.168.27.2 0.0.0.0 area 0
exit
exit
copy run start

area (numéro de l'AS)
router ospf x (process-id, même pour un réseau)


(show ospf interfaces)
show ip ospf interface brief

	5. ...

# II. Ecrire un script python qui permet de rajouter un CE dans le réseau facilement






