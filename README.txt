# Nasse

Doc:
https://www.cisco.com/c/en/us/support/docs/multiprotocol-label-switching-mpls/mpls/13733-mpls-vpn-basic.html
https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_l3_vpns/configuration/15-s/mp-l3-vpns-15-s-book/mp-bgp-mpls-vpn.html
https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/117567-technote-ibgp-00.html

# I. Configuration initiale du réseau:
	
	1. Ajouter des routers et des links

	2. Ajouter des switchs avec des PC derriere chaque CE/CS

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


	4. Configurer OSPF sur les routeurs et ajouter les routes

Config ospf sur les routeurs
------------------------------
configure terminal
router ospf 1
network 192.168.22.2 0.0.0.0 area 0
network 192.168.27.1 0.0.0.0 area 0
network 192.168.25.2 0.0.0.0 area 0
network 1.1.1.1 0.0.0.0 area 0
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
router bgp 100
bgp log-neighbor-changes
neighbor 192.168.10.2 remote-as 500
address-family ipv4
redistribute connected
neighbor 192.168.10.2 activate
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
ip vrf vpn1
rd 500:1
route-target export 500:1
route-target import 500:1
exit
ip vrf vpn2
rd 500:2
route-target export 500:2
route-target import 500:2
exit
router bgp 500
no bgp default ipv4-unicast
neighbor 192.168.31.1 remote-as 500
neighbor 192.168.10.1 remote-as 100
neighbor 192.168.11.1 remote-as 200
address-family vpnv4
neighbor 2.2.2.2 activate
neighbor 2.2.2.2 send-community extended
exit
router bgp 500	
address-family ipv4 vrf vpn2
neighbor 192.168.11.2 activate
neighbor 192.168.11.2 send-community extended
exit
router bgp 500
address-family ipv4 vrf vpn1
neighbor 2.2.2.2 remote-as 500
neighbor 2.2.2.2 activate
neighbor 2.2.2.2 send-community extended
exit
exit
conf t
interface gigabitEthernet 3/0
ip vrf forwarding vpn1
ip address 192.168.10.2 255.255.255.0
copy run start
----------------------
(Pour montrer voisin)
conf t
do sho ip bgp neighbors
----------------------


	6. Ajouter MPLS

Config MPLS sur les routeurs (a faire sur toutes les interfaces du backbone)
------------------------------
configure terminal
interface Loopback 1
ip cef
exit
conf terminal
interface Loopback 1
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
------------------------------

(CEF = cisco express forwarding)

- Pour faire des tests (pings)

* Sur les CE
ping
ip
address

* Sur les PE
ping vrf vpn1 ip address


	7. Ajouter des routes MPLS-VPN entre différents AS du même client (ex: CE1 et CE4)

!--- Enables the VPN routing and forwarding (VRF) routing table.  
!--- Route distinguisher creates routing and forwarding tables for a VRF. 
!--- Route targets creates lists of import and export extended communities for the specified VRF.

Pour vérifs:

PE to CE Verification Commands
------------------------------
show ip vrf  — Verifies that the correct VRF exists.
show ip vrf interfaces  — Verifies the activated interfaces.
show ip route vrf <VRF name>  —Verifies the routing information on the PE routers.
traceroute vrf  <VRF name> <IP address>  — Verifies the routing information on the PE routers.
show ip cef vrf <VRF name> <IP address> detail  — Verifies the routing information on the PE routers.
------------------------------

Pour rendre plus logique, faudrait que CE3/4 aient les memes addresses

Access lists:
MPLS Access lists enables filtering of MPLS packets based on MPLS label and sending filtered packets to
configured redirect interfaces.

show mpls ldp neighbor (montre voisins)
show ip bgp neighbors x.x.x.x advertised-routes (routes bgp)

Les routeurs ont des tables de routage globales, ainsi que des VRF (virtual routing) qui permettent
d'être appliqué à certaines destinations pour faire une action particulière

Commandes pour CE
------------------------------
conf t
ip route 192.168.31.0 255.255.255.0 192.168.11.1
exit
------------------------------

Commandes pour PE
------------------------------
conf t
interface gigabitEthernet 1/0
ip vrf forwarding vpn1
ip address 192.168.10.2 255.255.255.0
exit
interface gigabitEthernet 3/0
ip vrf forwarding vpn2
ip address 192.168.10.1 255.255.255.0
exit
------------------------------
RD = distinguish routes that belong to different vpn's
RT = control distribution of routes
AS:COMMUNITY

pour check routes
show ip bgp vpnv4 vrf vpn1
show ip route vrf vpn1
now on PE2 i do a vpn route to go to 30.2 through 30.1

	8. Ajouter encryption sur les routes vpn

Commandes sur router
------------------------------
conf t
crypto isakmp policy 10
encryption aes
hash sha
authentication pre-share
group 5
exit
crypto isakmp key vpnuser address 192.168.10.2
crypto ipsec transform-set myset esp-aes esp-sha-hmac
exit
access-list 100 permit ip 192.168.30.0 0.0.0.255 192.168.10.0 0.0.0.255
crypto map mymap 10 ipsec-isakmp
set peer 192.168.10.2
set transform-set myset
match address 100
exit
interface GigabitEthernet 1/0
crypto map mymap
exit
exit
copy run start
------------------------------

Troubleshooting
------------------------------
show crypto ipsec sa
show crypto isakmp sa
show crypto map
show crypto session remote 192.168.11.2 detail
------------------------------

	9. Ajouter VOip, filtrage par access-lists, Qos BGP...

	10. Favoriser certaines routes, comme des Peers, pour payer moins

	11. Pouvoir mettre des règles sur les nou	veaux AS (customer/peer/provider?), en fonction de son rôle, la config BGP des poids sera différente

	12. Automatiser l'ajout de client dans le réseaux

# II. Ecrire un script python qui permet de rajouter un CE dans le réseau facilement

- Scripts pour ajouter des clients
- Différent s'ils sont des transporteurs, des pairs, des clients, (pour payer plus ou moins)
=> Transporteurs utilisés en 'dernier recours',
=> Clients peuvent nous demander des connexions vpn
=> 




