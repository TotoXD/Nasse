# Nasse

# I. Configurer MPLS à la main sur tout le réseau
	
	1. Ajouter des routers et des links

	2. Ajouter des switchs avec des PC derriere chaque CE/CS (peut être plus tard)

	3. Configurer une IP sur chacune des interfaces des routeurs

- Config pour chaque router
--------------------------------
configure terminal
interface gigabitEthernet 2/0
ip address 192.168.21.1 255.255.255.0
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
network 192.168.22.2 0.0.0.0 area 0
network 192.168.27.1 0.0.0.0 area 0
network 192.168.25.2 0.0.0.0 area 0
exit
exit
copy run start

area (numéro de l'AS)
router ospf x (process-id, même pour un réseau)

(show ospf interfaces)
show ip ospf interface brief

	5. Ajouter BGP entre CE-PE

Config BGP sur les routeurs CE
------------------------------
configure terminal
router bgp 300
neighbor 192.168.30.1 remote-as 500
neighbor 192.168.30.1 activate
address-family ipv4
redistribute connected
neighbor 192.168.30.1 activate
neighbor 192.168.30.1 advertisement-interval 5
no auto-summary
no synchronization
exit-address-family
exit
exit
copy run start


(Pour montrer voisin)
conf t
do sho ip bgp neighbors

Config BGP sur les routeurs PE
------------------------------
configure terminal
router bgp 500
ip vrf vpn1
rd 500:3
route-target export 500:1
route-target import 500:1
exit
router bgp 500
ip vrf vpn2
rd 500:4
route-target export 500:2
route-target import 500:2
exit
router bgp 500
no bgp default ipv4-unicast
neighbor 192.168.31.1 remote-as 500
address-family vpnv4
neighbor 192.168.30.2 activate
neighbor 192.168.30.2 send-community extended
neighbor 192.168.31.2 activate
neighbor 192.168.31.2 send-community extended
exit
router bgp 500
address-family ipv4 vrf vpn2
neighbor 192.168.11.2 send-community extended
exit
router bgp 500
address-family ipv4 vrf vpn1
neighbor 192.168.10.2 send-community extended
exit
exit
conf t
interface gigabitEthernet 3/0
ip vrf forwarding vpn1
ip address .... ...
copy run start

----------------------
Configuring Multiprotocol BGP Connectivity on the PE Devices and Route Reflectors

SUMMARY STEPS
1.    enable

2.    configure terminal

3.    router bgp as-number

4.    no bgp default ipv4-unicast

5.    neighbor {ip-address | peer-group-name} remote-as as-number

6.    neighbor {ip-address | peer-group-name} activate

7.    address-family vpnv4 [unicast]

8.    neighbor {ip-address | peer-group-name} send-community extended

9.    neighbor {ip-address | peer-group-name} activate

10.    end
-------------------------

(Pour montrer voisin)
conf t
do sho ip bgp neighbors



	6. Ajouter MPLS

Config MPLS sur les routeurs (a faire sur toutes les interfaces du backbone)
------------------------------
configure terminal
interface gigabitEthernet 1/0
ip cef
exit
conf terminal
interface gigabitEthernet 1/0
ip route-cache cef
mpls mtu 1500
mpls ip
mpls label protocol ldp
exit
exit
configure terminal
interface gigabitEthernet 2/0
ip cef
exit
conf terminal
interface gigabitEthernet 2/0
ip route-cache cef
mpls mtu 1500
mpls ip
mpls label protocol ldp
exit
exit
copy run start


(CEF = cisco express forwarding)


	7. Ajouter des routes MPLS-VPN entre différents AS du même client (ex: CE1 et CE4)
	(=> C ce que je disais PL du coup, c'est bien des AS différents mais juste le mm client)

- Pour faire des tests (pings)

* Sur les CE
ping
ip
address

* Sur les PE
ping vrf vpn1 ip address



	8. Automatiser l'ajout de client dans le réseaux

	9. Favoriser certaines routes, comme des Peers, pour payer moins

	10. Pouvoir mettre des règles sur les nouveaux AS (customer/peer/provider?), en fonction de son rôle, la config BGP des poids sera différente


# II. Ecrire un script python qui permet de rajouter un CE dans le réseau facilement






