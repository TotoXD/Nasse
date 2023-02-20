import getpass
import telnetlib
import json
import time

if __name__ == "__main__":
    print('Configuration Telnet\n')

    # Le modèle de input data que j'ai fait est certainement à améliorer
    # Faudra faire un fichier .gns3 vide sans aucune config, juste avec les routers

    HOST = '127.0.0.1'
    print(HOST, '\n')

    # Récupération de la config
    with open('network_config.json', 'r') as file:
        network_config = json.load(file)

    # Récupération de l'input data
    with open('input_data.json', 'r') as file:
        input_data = json.load(file)

    # Pour chaque lien existant, on va devoir modifier la config d'au moins un de nos routeurs
    for link in input_data['links']:
        router1 = link['router1']
        router2 = link['router2']

        for router in input_data['routers']:
            router_to_config = "None"
            name_interface = "None"
            network_router = "None"

            if router1 == router['name']:
                router_to_config = "router1"
                name_interface = "name_interface_router1"
                network_router = "network_router1"
            elif router2 == router['name']:
                router_to_config = "router2"
                name_interface = "name_interface_router2"
                network_router = "network_router2"

            if router_to_config != "None":
                port = router['port']

                # Connexion au router en telnet pour le configurer
                with telnetlib.Telnet(HOST, port) as tn :
                    print("Configuration du routeur : \n", router['name'])

                    # Config de l'interface
                    interface = link[name_interface]

                    for interf in router['interfaces']:

                        if(interf['name'] == 'Loopback1'):
                            tn.write(b'end \r')
                            tn.write(b'configure terminal \r')
                            tn.write(b'interface ' + interf['name'].encode('ascii') + b' \r')
                            router_id = (router['id']).encode('ascii')
                            tn.write(b'ip address ' + router_id + b'.' + router_id + b'.' + router_id + b'.' + router_id + b' 255.255.255.255 \r')
                            tn.write(b'end \r')

                        if interf['name'] == interface or interf['name'] == "Loopback1":

                            print("Interface trouvée \n")

                            if interf['state'] == "up":

                                tn.write(b'configure terminal \r')
                                tn.write(b'interface ' + interface.encode('ascii') + b' \r')

                                tn.write(b'ip address ' + link[network_router].encode('ascii') + b' 255.255.255.0 \r')
                                tn.write(b'no shutdown \r')

                                tn.write(b'end \r')
                                time.sleep(0.1)
                                tn.write(b' \r')

                                # Sauvegarde de la conf
                                print("Writing config \n")
                                tn.write(b'copy run start \r')
                                time.sleep(0.1)
                                tn.write(b' \r')
                                tn.write(b' \r')
                                time.sleep(0.4)

                                print(interf['protocols'])

                                # Depending the protocol
                                for protocol in interf['protocols']:
                                    if protocol == "OSPF":
                                        print("Adding OPSF config \n")

                                        tn.write(b'configure terminal \r')
                                        tn.write(b'router ospf 1 \r')
                                        if interf['name'] == "Loopback1":
                                            tn.write(b'network ' + router['id'].encode('ascii') + b'.' + router['id'].encode('ascii') + b'.' + router['id'].encode('ascii') + b'.' + router['id'].encode('ascii') + b' 0.0.0.0' + b' area 0 \r')
                                        else:
                                            tn.write(b'network ' + link[network_router].encode('ascii') + b' 0.0.0.0' + b' area 0 \r')
                                        tn.write(b'end \r')
                                        time.sleep(0.1)
                                        tn.write(b' \r')

                                        # Sauvegarde de la conf
                                        print("Writing config \n")
                                        tn.write(b'copy run start \r')
                                        time.sleep(0.1)
                                        tn.write(b' \r')
                                        tn.write(b' \r')
                                        time.sleep(0.4)

                                    if protocol == "MPLS":
                                        print("Adding MPLS config \n")

                                        tn.write(b'configure terminal \r')
                                        tn.write(b'interface ' + interface.encode('ascii') + b' \r')
                                        tn.write(b'ip cef \r')
                                        tn.write(b'exit \r') 
                                        tn.write(b'conf terminal \r')
                                        
                                        tn.write(b'interface ' + interface.encode('ascii') + b' \r')
                                        tn.write(b'ip route-cache cef \r')
                                        tn.write(b'mpls mtu 1500 \r')
                                        tn.write(b'mpls ip \r')
                                        tn.write(b'mpls label protocol ldp \r')

                                        tn.write(b'end \r')
                                        time.sleep(0.1)
                                        tn.write(b' \r')

                                        # Sauvegarde de la conf
                                        print("Writing config \n")
                                        tn.write(b'copy run start \r')
                                        time.sleep(0.1)
                                        tn.write(b' \r')
                                        tn.write(b' \r')
                                        time.sleep(0.4)

                                    if protocol == "IBGP":
                                        print("Adding IBGP config \n")

                                        tn.write(b'configure terminal \r')
                                        tn.write(b'router bgp ' + b'500' + b' \r')
                                        tn.write(b'neighbor ' + interf['neighbor_loopback'].encode('ascii') +  b' remote-as 500 \r')
                                        tn.write(b'neighbor ' + interf['neighbor_loopback'].encode('ascii') +  b' update-source Loopback1 \r')
                                        tn.write(b'address-family vpnv4 \r')
                                        tn.write(b'neighbor ' + interf['neighbor_loopback'].encode('ascii') + b' activate \r')
                                        tn.write(b'neighbor ' + interf['neighbor_loopback'].encode('ascii') + b' send-community extended \r')
                                        tn.write(b'exit-address-family \r')

                                        tn.write(b'address-family ipv4 \r')
                                        tn.write(b'neighbor ' + interf['neighbor_loopback'].encode('ascii') + b' activate \r')
                                        tn.write(b'exit-address-family \r')

                                        tn.write(b'end \r')                                 

                                   

                                    if protocol == "EBGP":
                                        print("Adding EBGP config \n")

                                        rt = input_data['vpns'][0]['route_target']

                                        as_router = link['as']
                                        print("as route\n")
                                        print(as_router)

                                        if router['as'] == link['as']:
                                            as_router = "500"
                                        as_real = router['as']
                                        tn.write(b'configure terminal \r')
                                        print(as_real)
                                        print(as_real)
                                        tn.write(b'router bgp ' + as_real.encode('ascii') + b' \r')
                                        tn.write(b'bgp log-neighbor-changes \r')
                                        if 'network_router1' == network_router:
                                            other_network = link['network_router2']
                                        else:
                                            other_network = link['network_router1']

                                        tn.write(b'neighbor ' + other_network.encode('ascii') + b' remote-as ' + as_router.encode('ascii') + b' \r')
                                        tn.write(b'address-family ipv4 \r')
                                        tn.write(b'redistribute connected \r')
                                        tn.write(b'neighbor ' + other_network.encode('ascii') +  b' activate \r')
                                        tn.write(b'exit-address-family \r')
                                        tn.write(b'end \r')


                                        tn.write(b'end \r')

                                        if router['name'][0:1] != "C":
                                            tn.write(b'configure terminal \r')
                                            tn.write(b'router bgp ' + as_real.encode('ascii') + b' \r')
                                            tn.write(b'address-family ipv4 vrf vpn' + rt.encode('ascii') + b' \r')
                                            tn.write(b'neighbor ' + other_network.encode('ascii') + b' remote-as ' + as_router.encode('ascii') + b' \r')
                                            tn.write(b'neighbor ' + other_network.encode('ascii') + b' activate \r')
                                            tn.write(b'neighbor ' + other_network.encode('ascii') + b' send-community extended \r')
                                            tn.write(b'no synchronization\r')

                                            tn.write(b'end \r')

                                            tn.write(b'configure terminal \r')
                                            tn.write(b'ip vrf vpn' + rt.encode('ascii') + b' \r')

                                            if router1 == router_to_config:
                                                other_name = router2
                                            else:
                                                other_name = router1

                                            if input_data['vpns'][0]['router1'] == other_name:

                                                rd = input_data['vpns'][0]['route_distinguisher1']
                                            else:
                                                rd = input_data['vpns'][0]['route_distinguisher2']

                                            tn.write(b'rd 500:' + rd.encode('ascii') + b' \r')
                                            tn.write(b'route-target export 500:'+rt.encode('ascii') + b' \r')
                                            tn.write(b'route-target import 500:'+rt.encode('ascii') + b' \r')
                                            tn.write(b'end \r')

                                            tn.write(b'conf t \r')
                                            tn.write(b'interface ' + interface.encode('ascii') + b' \r')
                                            tn.write(b'ip vrf forwarding vpn' + rt.encode('ascii') + b' \r')
                                            tn.write(b'ip address ' + link[network_router].encode('ascii') + b' 255.255.255.0 \r')



                                        #####################

                                        tn.write(b'end \r')
                                        time.sleep(0.1)
                                        tn.write(b' \r')

                                        # Sauvegarde de la conf
                                        print("Writing config \n")
                                        tn.write(b'copy run start \r')
                                        time.sleep(0.1)
                                        tn.write(b' \r')
                                        tn.write(b' \r')
                                        time.sleep(0.4)



                                tn.write(b'end \r')
                                time.sleep(0.1)

                                # Sauvegarde de la conf
                                print("Writing config \n")
                                tn.write(b'copy run start \r')
                                time.sleep(0.1)
                                tn.write(b' \r')
                                tn.write(b' \r')
                                time.sleep(0.4)




            name_interface = "None"
            router_to_config = "None"
            network_router = "None"




    print('Fin de la configuration Telnet !\n')
        
