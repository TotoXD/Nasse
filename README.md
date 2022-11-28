# Nasse

# I. Configurer MPLS à la main sur tout le réseau
	
	1. Ajouter des routers et des links

	2. Ajouter des switchs avec des PC derriere chaque CE/CS (peut être plus tard)

	3. Configurer une IP sur chacune des interfaces des routeurs

# Config pour chaque router
--------------------------------
configure terminal

interface gigabitEthernet X/0

ip address 192.168.XX.X 255.255.255.0

no shutdown

exit

exit

copy run start
--------------------------------

# Commandes utiles:

do sho cdp nei (show neighbours)

show running-config

default interface gi 1/1 (reset interface)

copy run start (save config)



	4. Configure OSPF sur les routeurs et ajouter les routes

	5. ...

# II. Ecrire un script python qui permet de rajouter un CE dans le réseau facilement

