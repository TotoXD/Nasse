# Nasse

I. Configurer MPLS à la main sur tout le réseau
	
	1. Ajouter des routers et des links

	2. Ajouter des switchs avec des PC derriere chaque CE/CS (peut être plus tard)

	3. Configurer une IP sur chacune des interfaces des routeurs

configure terminal
interface gigabitEthernet 1/0
ip address 192.168.21.2 255.255.255.0
no shutdown
exit

	4. Configure OSPF sur les routeurs et ajouter les routes
	5. ...

II. Ecrire un script python qui permet de rajouter un CE dans le réseau facilement