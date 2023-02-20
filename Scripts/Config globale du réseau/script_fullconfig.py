import getpass
import telnetlib
import json
import time

if __name__ == "__main__":


    list=[]
    print('Configuration Telnet\n')


    # Le modèle de input data que j'ai fait est certainement à améliorer
    # Faudra faire un fichier .gns3 vide sans aucune config, juste avec les routers

    HOST = '127.0.0.1'
    print(HOST, '\n')

    # Récupération de la config
    with open('network_config.json', 'r') as file:
        network_config = json.load(file)

    # Application de la config sur chaque router
    for router in network_config['routers']:
        port = router['port']

        # Connexion au router en telnet
        print(HOST, port)
        with telnetlib.Telnet(HOST, port) as tn :

            # ------------------------------ Config de chaque interface -----------------------------------
            for interface in router['interfaces']:
                if(interface['state'] == 'up'):
                    tn.write(b'configure terminal \r')
                    tn.write(b'interface ' + interface['name'].encode('ascii') + b' \r')
                    
                    if(interface['name'] == 'Loopback0'):
                        router_id = (router['id']).encode('ascii')
                        tn.write(b'ip address ' + router_id + b'.' + router_id + b'.' + router_id + b'.' + router_id + b' 255.255.255.255 \r')
                    else :
                        if interface['link'] in list:
                            tn.write(b'ip address 192.168.' + interface['link'].encode('ascii') + b'.2 255.255.255.0 \r')
                        else :
                            tn.write(b'ip address 192.168.' + interface['link'].encode('ascii') + b'.1 255.255.255.0 \r')

                    tn.write(b'no shutdown \r')

                    tn.write(b'end \r')
                    time.sleep(0.1)
                    tn.write(b' \r ')

            tn.write(b'end \r')
            # Sauvegarde de la conf
            print("Writing config \n")
            tn.write(b'copy run start \r')
            time.sleep(0.1)
            tn.write(b' \r')
            tn.write(b' \r')
            time.sleep(0.2)
            tn.write(b' \r')
            tn.write(b'end \r')

            # ------------------------- Fin de la première config de chaque interface ----------------------


            # -------------------------------------------- OSPF --------------------------------------------

            # On rentre en mode ospf même s'il n'y avait pas de liens ospf, c'est pas grave
            tn.write(b'configure terminal \r')
            tn.write(b'router ospf 1 ' + b' \r')

            # Pour chaque interface en OSPF
            for interface in router['interfaces']:
                if(interface['state'] == 'up'):
                    for protocol in interface['protocols']:
                        if (protocol == 'OSPF'):
                            if interface['link'] in list:
                                tn.write(b'network 192.168.' + interface['link'].encode('ascii') + b'.2 0.0.0.0 area ' + router['ospf_area_id'].encode('ascii') + b' \r')
                            else :
                                tn.write(b'network 192.168.' + interface['link'].encode('ascii') + b'.1 0.0.0.0 area ' + router['ospf_area_id'].encode('ascii') + b' \r')
                            tn.write(b' \r ')
                            time.sleep(0.1)

            time.sleep(0.1)
            tn.write(b'end \r')

            # Sauvegarde de la conf
            print("Writing config \n")
            tn.write(b'copy run start \r')
            time.sleep(0.1)
            tn.write(b' \r')
            tn.write(b' \r')
            time.sleep(0.2)
            tn.write(b' \r')
            tn.write(b'end \r')


            # ------------------------------------------ Fin OSPF ------------------------------------------

            # -------------------------------------------- eBGP ---------------------------------------------

            tn.write(b'configure terminal \r')
            
            for interface in router['interfaces']:
                if(interface['state'] == 'up'):
                    for protocol in interface['protocols']:
                        if (protocol == 'EBGP'):
                            tn.write(b'router bgp ' + router['as'].encode('ascii') + b'\r')
                            tn.write(b'bgp log-neighbor-changes\r')
                            if interface['link'] in list:
                                tn.write(b'neighbor 192.168.' + interface['link'].encode('ascii') + b'.1 remote-as ' + interface['as'].encode('ascii')+b' \r')
                            else :
                                tn.write(b'neighbor 192.168.' + interface['link'].encode('ascii') + b'.2 remote-as ' + interface['as'].encode('ascii')+b' \r')
                            tn.write(b'address-family ipv4 \r')
                            tn.write(b'redistribute connected \r')
                            if interface['link'] in list:
                                tn.write(b'neighbor 192.168.' + interface['link'].encode('ascii') + b'.1 activate \r')
                            else :
                                tn.write(b'neighbor 192.168.' + interface['link'].encode('ascii') + b'.2 activate \r')
                            tn.write(b'exit-address-family \r')
                            time.sleep(0.1)

            tn.write(b'end \r')
            # Sauvegarde de la conf
            print("Writing config \n")
            tn.write(b'copy run start \r')
            time.sleep(0.1)
            tn.write(b' \r')
            tn.write(b' \r')
            time.sleep(0.2)
            tn.write(b' \r')
            tn.write(b'end \r')
            
            # -------------------------------------------- Fin eBGP -----------------------------------------
            
            # -------------------------------------------- iBGP ---------------------------------------------
            tn.write(b'configure terminal \r')
            for interface in router['interfaces']:
                if(interface['state'] == 'up'):
                    for protocol in interface['protocols']:
                        if (protocol == 'iBGP'):
                            for vrf in router['vrf']:
                                tn.write(b'ip vrf vpn'+vrf.encode('ascii')+b' \r')
                                tn.write(b'rd 500:'+vrf.encode('ascii')+b' \r')
                                tn.write(b'route-target export 500:'+vrf.encode('ascii')+b' \r')
                                tn.write(b'route-target import 500:'+vrf.encode('ascii')+b' \r')
                                tn.write(b'exit \r')
                                
                            tn.write(b'router bgp ' + router['as'].encode('ascii')+b' \r')
                            tn.write(b'neighbor ' + interface['neighbor'].encode('ascii') + b' remote-as ' + interface['as'].encode('ascii')+b' \r')
                            tn.write(b'address-family vpnv4 \r')
                            for interface_2 in router['interfaces']:

                                for protocol_2 in interface_2['protocols']:
                                    if (protocol_2 == 'EBGP'):
                                        if router['name'] == "PE1":

                                            tn.write(b'neighbor 192.168.' + interface_2['link'].encode('ascii') + b'.1 activate \r')
                                            tn.write(b'neighbor 192.168.' + interface_2['link'].encode('ascii') + b'.1 send-community extended \r')
                                        else :
                                            tn.write(b'neighbor 192.168.' + interface_2['link'].encode('ascii') + b'.2 activate \r')
                                            tn.write(b'neighbor 192.168.' + interface_2['link'].encode('ascii') + b'.2 send-community extended \r')
                                tn.write(b'exit \r')
                            
                            for interface_2 in router['interfaces']:
                                for protocol_2 in interface_2['protocols']:
                                    if (protocol_2 == 'EBGP'):


                                        tn.write(b'router bgp ' + router['as'].encode('ascii')+b' \r')
                                        tn.write(b'address-family ipv4 vrf vpn' + interface_2['vrf'].encode('ascii') + b' \r')

                                        #TROUVER UN MOYEN DE CHECK QUEL NUMERO POUR LA FIN DE L'IP
                                        if router['name'] == "PE1":
                                            tn.write(b'neighbor 192.168.' + interface_2['link'].encode('ascii') + b'.1 activate \r')
                                            tn.write(b'neighbor 192.168.' + interface_2['link'].encode('ascii') + b'.1 send-community extended \r')
                                        else :
                                            tn.write(b'neighbor 192.168.' + interface_2['link'].encode('ascii') + b'.2 activate \r')
                                            tn.write(b'neighbor 192.168.' + interface_2['link'].encode('ascii') + b'.2 send-community extended \r')

                                        tn.write(b'exit \r')
                                        
                                        tn.write(b'interface ' + interface_2['name'].encode('ascii') + b' \r')
                                        tn.write(b'ip vrf forwarding vpn' + interface_2['vrf'].encode('ascii') + b' \r')
                                        tn.write(b'end \r')
                                        # Sauvegarde de la conf
                                        print("Writing config \n")
                                        tn.write(b'copy run start \r')
                                        time.sleep(0.1)
                                        tn.write(b' \r')
                                        tn.write(b' \r')
                                        time.sleep(0.2)
                                        tn.write(b' \r')
                                        tn.write(b'end \r')
                                    
            for interface in router['interfaces']:
                if(interface['state'] == 'up'):
                    tn.write(b'configure terminal \r')
                    tn.write(b'interface ' + interface['name'].encode('ascii') + b' \r')
                    
                    if(interface['name'] == 'Loopback0'):
                        router_id = (router['id']).encode('ascii')
                        tn.write(b'ip address ' + router_id + b'.' + router_id + b'.' + router_id + b'.' + router_id + b' 255.255.255.255 \r')
                    else :
                        if interface['link'] in list:
                            tn.write(b'ip address 192.168.' + interface['link'].encode('ascii') + b'.2 255.255.255.0 \r')
                        else :
                            tn.write(b'ip address 192.168.' + interface['link'].encode('ascii') + b'.1 255.255.255.0 \r')

                    tn.write(b'no shutdown \r')

                    tn.write(b'end \r')
                    time.sleep(0.1)
                    tn.write(b' \r ')

            tn.write(b'end \r')
            # Sauvegarde de la conf
            print("Writing config \n")
            tn.write(b'copy run start \r')
            time.sleep(0.1)
            tn.write(b' \r')
            tn.write(b' \r')
            time.sleep(0.2)
            tn.write(b' \r')
            tn.write(b'end \r')
                            
                            
            # -------------------------------------------- Fin iBGP -----------------------------------------            
            

            # -------------------------------------------- MPLS --------------------------------------------
            for interface in router['interfaces']:
                if(interface['state'] == 'up'):
                    for protocol in interface['protocols']:
                        if (protocol == 'MPLS'):
                            tn.write(b'configure terminal \r')
                            tn.write(b'interface ' + interface['name'].encode('ascii') + b' \r')
                            if interface['link'] in list:
                                tn.write(b'ip address 192.168.' + interface['link'].encode('ascii') + b'.2 255.255.255.0 \r')
                            else :
                                tn.write(b'ip address 192.168.' + interface['link'].encode('ascii') + b'.1 255.255.255.0 \r')

                            tn.write(b'ip cef \r')
                            tn.write(b'exit \r')
                            tn.write(b'configure terminal \r')
                            tn.write(b'interface ' + interface['name'].encode('ascii') + b' \r')
                            tn.write(b'ip route-cache cef \r')
                            tn.write(b'mpls mtu 1500\r')
                            tn.write(b'mpls ip \r')
                            tn.write(b'mpls label protocol ldp \r')
                            tn.write(b'exit \r')
                            tn.write(b'exit \r')
                            tn.write(b'end \r')
                            # Sauvegarde de la conf
                            print("Writing config \n")
                            tn.write(b'copy run start \r')
                            time.sleep(0.1)
                            tn.write(b' \r')
                            tn.write(b' \r')
                            time.sleep(0.2)
                            tn.write(b' \r')
                            tn.write(b'end \r')

            # -------------------------------------------- Fin MPLS ----------------------------------------

            # -------------------------------------------- MPLS-VPN ----------------------------------------




            

            # -------------------------------------------- Fin MPLS-VPN ------------------------------------

        for interface in router['interfaces']:
            list.append(interface['link'])
        





    print('Fin de la configuration Telnet !\n')
        
