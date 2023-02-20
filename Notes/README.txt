# Nasse

https://docs.google.com/document/d/1YrTGvD-wjp-fUsvg6h7gWs9O9SO0MnUrrUnIVttYbR8/edit?usp=sharing

Doc:
https://www.cisco.com/c/en/us/support/docs/multiprotocol-label-switching-mpls/mpls/13733-mpls-vpn-basic.html
https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_l3_vpns/configuration/15-s/mp-l3-vpns-15-s-book/mp-bgp-mpls-vpn.html
https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/117567-technote-ibgp-00.html
https://web.eecs.umich.edu/~sugih/courses/eecs489/lectures/18-PolicyRouting.pdf

# I. Configuration initiale du réseau:
	
	1. Ajouter des routers et des links

	2. Ajouter des switchs avec des PC derriere chaque CE/CS

	3. Configurer une IP sur chacune des interfaces des routeurs

- Config pour chaque router
--------------------------------
configure terminal
interface gigabitEthernet 4/0
ip address 192.168.40.1 255.255.255.0
no shutdown
exit
exit
copy run start
-------------------------------- (Exemple pour plusieurs interfaces à la fois)
configure terminal
interface gigabitEthernet 5/0
ip address 192.168.33.1 255.255.255.0
no shutdown
exit
interface gigabitEthernet 2/0
ip address 192.168.41.2 255.255.255.0
no shutdown
exit
interface gigabitEthernet 3/0
ip address 192.168.48.2 255.255.255.0
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
network 192.168.45.1 0.0.0.0 area 0
network 192.168.42.2 0.0.0.0 area 0
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
neighbor 192.168.11.2 remote-as 400
neighbor 192.168.11.2 activate
neighbor 192.168.11.2 send-community extended
exit
exit
conf t
interface gigabitEthernet 3/0
ip vrf forwarding vpn1
ip address 192.168.10.2 255.255.255.0
exit
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
interface gigabitEthernet 1/0
ip address 192.168.41.1 255.255.255.0
no shutdown
ip cef
exit
conf terminal
interface gigabitEthernet 2/0
ip address 192.168.42.1 255.255.255.0
no shutdown
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
crypto isakmp key vpnuser2 address 192.168.10.1
crypto ipsec transform-set myset2 esp-aes esp-sha-hmac
exit
access-list 101 permit ip 192.168.30.0 0.0.0.255 192.168.10.0 0.0.0.255
crypto map mymap2 20 ipsec-isakmp
set peer 192.168.10.1
set transform-set myset2
match address 101
exit
interface GigabitEthernet 1/0
negotiation auto
crypto map mymap2
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

Il faut se rappeler que le but du projet est de simuler que nous sommes un internet provider,
on veut donner un service simple à nos clients et payer le moins possible, et jamais avoir de panne/problèmes...

QoS:

Le but de MPLS est d'une part de pouvoir faire des labels pour forward les paquets
sans utiliser des adresses et gagner en efficacité, mais ce n'est pas son plus grand atout.

Le plus grand intérêt de MPLS est de pouvoir faire de la Quality of Service, notamment en
implémentantant du PBR (Policy Based Routing) ainsi que du TE (Traffic Engineering).
Cela permet non seulement de préférer certaines routes (providers plutot que peers) ou de rediriger
le traffic comme bon nous semble: pour payer moins, pour éviter de l'overload, pour résister à la panne, etc.

On peut notamment faire ça en ajoutant des route-map (partager certaines routes à certaines personnes), des
access-lists (refuser/accepter du traffic), mettre un "poids" sur des routeurs pour passer par eux/les éviter,
ajouter du RSVP (pour allouer des ressources sur certains liens), faire du segment-routing (allouer des SID pour
rediriger le traffic vers une certaine partie du réseau)

On fait aussi du class based marking, en priorisant le traffic VoIP qui ne peut pas attendre d'être delivered
au dessus du traffic normal sur le réseau.

Dans la config, on va simuler : (bien configuré)
	- L'implémentation de clients qui ont besoin de QoS
	- Des peers en rab
	- Des transporteurs en rab
	- Que un des liens est surchargé

	10. Pouvoir mettre des règles sur les nouveaux AS (customer/peer/provider?), en fonction de son rôle, la config BGP des poids sera différente

On peut avoir différents types de routeurs à rajouter et configurer quand on est un provider:

- Un nouveau routeur Provider (P)
- Un nouveau routeur Provder Edge (PE)
- Un nouveau routeur Customer (CE)
- Un transporteur (PT)

Différents types de situations:
- Un client veut rajouter deux nouveaux sites à notre réseaux sur un site qui n'existe pas chez nous
- Un client veut rajouter des sites en VPN sur des VRF déjà existantes
- Un client déjà existant veut rajouter un site à une de ces VRF sur un nouveau site PE
- Un peer se rajoute à notre réseau
- On a un nouveau PE ou un nouveau P qui s'ajoute
- Un client peut vouloir du VPN ou non
- Un transporteur (qu'on voit pas trop utiliser)
...

Il faut pouvoir s'adapter à toute type de situation, ajouter des routeurs, les configurer,
mais surtout appliquer de la PBR et du TE pour gagner en efficacité, en argent, etc.


12. Automatiser l'ajout de client dans le réseaux

# II. Ecrire un script python qui permet de rajouter un CE dans le réseau facilement

Pour un nouveau CE:
------------------------------
configure terminal
interface gigabitEthernet 1/0
ip address 192.168.33.2 255.255.255.0
no shutdown
exit
exit
configure terminal
router bgp 500
neighbor 192.168.40.2 remote-as 800
address-family ipv4
neighbor 192.168.40.2 activate
exit-address-family
exit
exit
copy run start
------------------------------


Pour un nouveau PE:
------------------------------
configure terminal
interface gigabitEthernet 1/0
ip address 192.168.46.2 255.255.255.0
no shutdown
exit
interface gigabitEthernet 2/0
ip address 192.168.46.2 255.255.255.0
no shutdown
exit
interface gigabitEthernet 3/0
ip address 192.168.46.2 255.255.255.0
no shutdown
exit
exit
configure terminal
router ospf 1
network 192.168.45.1 0.0.0.0 area 0
network 192.168.42.2 0.0.0.0 area 0
exit
exit
configure terminal
router bgp 500
neighbor 192.168.42.2 remote-as 700
neighbor 192.168.41.2 remote-as 800
address-family ipv4
redistribute connected
neighbor 192.168.42.2 activate
neighbor 192.168.41.2 activate
exit-address-family
exit
exit
copy run start


- Est ce que nos transporteurs et nos peers routent en MPLS ou en simple OSPF?


- Qui partage les routes à qui?
Faut pas donner les routes entre peer ou transporteurs
Parce que s'il y a une meilleure route ils passent plus par nous
Faire attention de pas rediriger le traffic PAR le client
On veut jamais donner des routes qui passent pas par nous et qui sont plus forts que nous (la taille de l'ISP)
Les clients on les advertise a tout le monde meme si c un gros isp
On va pas advertise des routes qui vont d'isp à isp sinon ils nous volent
Les gros peers vont nous donner une grosse charge de traffic
Tout ce qui est plus petit que nous on les annonce
On annonce pas depuis P1 que pp peut passer par nous pour aller chez PT

- Où on met des access list	

- Moyen facile de simuler du VOip? 
=> Simuler téléphonie
=> Réserver ressources sur un tunnel (ex: 10% pour du VOiP)

- RSVP
=> marche avec mpls
=> file d'attente spécifique a chaque classe
=> garantie que la voie peut passer plus vite
=> de source à destination
=> sans configurer
=> mettre a jour rsvp pour pas réserver des ressources là ou il faut pas

Diffserv
=> Pour ne pas réserver les classes de facon permanente
=> Pouvoir mettre des conditions sur les classes
=> Et allocation selon les classes (priorité)
=> Pas limiter a 2 classes comme rsvp

Load balancing pour traffic engineering sur ibgp mpls
https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus3600/sw/92x/label-switching/b-cisco-nexus-3600-series-nx-os-label-switching-configuration-guide-92x/b-cisco-nexus-3600-series-nx-os-label-switching-configuration-guide-92x_chapter_0101.pdf
=> Pour décharger des liens
=> Multipath
=> Mettre des couts sur certains liens (plutot a l'intérieur du meme AS)

Segment routing
=> Pq pas regarder comment ca marche et le faire marcher et c un peu overkill
=> Vérifier que c compatible
=
=> Forces les paquets a passer par certains segments du réseau
=> Pour pas que des routes soient annoncés (plus courtes) et qu'on passe par la
=> Routage fait par la source et pas à chaque hop + en precisant quel type de traffic

Poids
=> Mettre des poids (weight) sur les liens pour passer par plus une route que l'autre
=> Local pref dans des route maps (préféré des routes) n'est pas absolu (peut etre configurer selon les traffics)
peut etre configuré selon la source alors que weight est pour tout le monde
=> Puis appliqué route map au neighbor bgp ou access list


--------------------------------------
• AS	exports	only	customer	routes	to	a	peer
• AS	exports	a	peer’s	routes	only	to	its	customers
• provider	tells	all	its	neighbors	how	to	reach	the	customer	
• customer	does	not	let	its	providers	route	through	it

An	AS’s	export	policy	(which	routes	it	will	advertise):	
• to	a	customer:	all	routes	
• to	a	peer	or	service	provider:	
• routes	to	all	its	own	APs	and	to	its	customers’	APs,	
• but	not to	APs	learned	from	other	providers	or	peers	
• internal	routing	of	an	AS	is	effected	by	its	neighbors’	route	
export	policy	


Utilité?
C'est bon pour moi d'aller vers CE6, pourtant, je veux pas passer en général par PT pour aller vers CE5 ou CE7, je passe donc par là que si je suis obligé 



 neighbor 2.2.2.2 remote-as 500
 neighbor 2.2.2.2 activate
 neighbor 2.2.2.2 next-hop-self

configure terminal
interface gigabitEthernet 5/0
ip vrf forwarding vpn11
ip address 192.168.33.1 255.255.255.0
no shutdown
exit
router bgp 500
address-family ipv4 vrf vpn11
neighbor 192.168.33.2 remote-as 400
neighbor 192.168.33.2 activate
neighbor 192.168.33.2 send-community extended
exit



route-map denypp permit 1
match ip address prefix-list listpp
exit
ip prefix-list listpp seq 1 deny 192.168.41.0/24
router bgp 500
neighbor 192.168.42.2 remote-as 700
neighbor 192.168.42.2 route-map denypp in
no neighbor 192.168.42.2 distribute-list 1 out

route-map denypt permit 3
match ip address prefix-list listpt
exit
ip prefix-list listpt seq 3 deny 192.168.42.0/24
router bgp 500
neighbor 192.168.41.2 remote-as 700
neighbor 192.168.41.2 route-map denypt in
no neighbor 192.168.41.2 distribute-list 3 out


* Adj-RIBs-In. The unedited routing information sent by neighboring routers.

* Loc-RIB. The actual routing information the router uses, developed from Adj-RIBs-In.

* Adj-RIBs-Out. The information the router chooses to send to neighboring routers.

i redistribute everywhere, but when its a peer or a pt, i make sure i deny all the routes from peer or pts



redistribute connected => redistribute one hop further
redistribute (protocol) redistribute all routes from this protocol.

neighbor 192.168.40.1 remote-as 500
no neighbor 192.168.40.1 ebgp-multihop 3
neighbor 192.168.41.1 remote-as 500
no neighbor 192.168.41.1 ebgp-multihop 3
neighbor 192.168.48.1 remote-as 600
no neighbor 192.168.48.1 ebgp-multihop 3
