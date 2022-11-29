# Etapes du projet:

- I. Configurer MPLS à la main sur tout le réseau
	
	=> Ajouter des routers et des links (Fait)

	=> Ajouter des switchs avec des PC derriere chaque CE/CS (peut être plus tard)

	=> Configurer une IP sur chacune des interfaces des routeurs (Fait)

	=> Exemples de config pour chaque router (pensez à save les config avec copy run start)

	configure terminal
	interface gigabitEthernet 4/0
	ip address 192.168.11.1 255.255.255.0
	no shutdown
	exit
	exit
	copy run start

(Exemple pour plusieurs interfaces à la fois)
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

	=> Commandes utiles:

(show neighbours)
configure terminal
do sho cdp nei

(show everything)
show running-config

(reset interface)
default interface gi x/x

(save config)
copy run start


	=> Configurer OSPF sur les routeurs et ajouter les routes

	=> Bgp...Mpls....

# II. Ecrire un script python qui permet de rajouter un CE dans le réseau facilement






