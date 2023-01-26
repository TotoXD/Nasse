import getpass
import telnetlib
import json

if __name__ == "__main__":
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
        with telnetlib.Telnet(HOST, port) as tn :

            # ------------------------------ Config de chaque interface -----------------------------------
            for interface in router['interfaces']:
                if(interface['state'] == 'up'):
                    tn.write(b'configure terminal \r')
                    tn.write(b'interface ' + interface['name'].encode('ascii') + b' \r')
                    
                    if(interface_name == 'Loopback0'):
                        router_id = (router['id']).encode('ascii')
                        tn.write(b'ip address ' + router_id + b'.' + router_id + b'.' router_id + b'.' router_id + b' 255.255.255.255 \r')
                    else :
                        router[id]
                        tn.write(b'ip address' + interface['network-router'].encode('ascii') + b' 255.255.255.0 \r')

                    tn.write(b'no shutdown \r')

                    tn.write(b'end \r')
                    time.sleep(0.1)
                    tn.write(b' \r ')

            # Sauvegarde de la conf
            tn.write(b'copy run start \r')

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
                            tn.write(b'network ' + interface['network-router'].encode('ascii') + b' 0.0.0.0 area ' + router['ospf_area_id'] + b' \r')
                            tn.write(b' \r ')
                            time.sleep(0.1)

            time.sleep(0.1)
            tn.write(b'end \r')

            # Sauvegarde de la conf
            tn.write(b'copy run start \r ')


            # ------------------------------------------ Fin OSPF ------------------------------------------

            # -------------------------------------------- eBGP ---------------------------------------------

            tn.write(b'configure terminal \r')
            tn.write(b'router bgp' + router['as'].encode('ascii') + b'\r')
            tn.write(b'bgp log-neighbor-changes\r')
            for interface in router['interfaces']:
                if(interface['state'] == 'up'):
                    for protocol in interface['protocols']:
                        if (protocol == 'EBGP'):
                            tn.write(b'neighbor ' + interface['neighbor'].encode('ascii') + b' remote-as ' + interface['as'].encode('ascii')+' \r')
                            tn.write(b'address-family ipv4 \r')
                            tn.write(b'redistribute connected \r')
                            tn.write(b'neighbor ' + interface['neighbor'].encode('ascii') + b' activate \r')
                            tn.write(b'exit-address-family \r')
                            time.sleep(0.1)

            time.sleep(0.1)
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
                            tn.write(b'neighbor ' + interface['neighbor'].encode('ascii') + b' remote-as ' + interface['as'].encode('ascii')+' \r')
                            tn.write(b'address-family vpnv4 \r')
                            tn.write(b'neighbor '+ interface['neighbor'].encode('ascii') + b' activate \r')
                            tn.write(b'neighbor ' + interface['neighbor'].encode('ascii') + b' send-community extended \r')
                            tn.write(b'exit \r')
                            
                            for interface_2 in router['interfaces']:
                                if (protocol == 'EBGP'):
                                    tn.write(b'router bgp ' + router['as'].encode('ascii')+b' \r')
                                    tn.write(b'address-family ipv4 vrf vpn' + interface_2['vrf'] + b' \r')
                                    tn.write(b'neighbor '+ interface_2['neighbor'].encode('ascii') + b' activate \r')
                                    tn.write(b'neighbor ' + interface_2['neighbor'].encode('ascii') + b' send-community extended \r')
                                    tn.write(b'exit \r')
                                    
                                    tn.write(b'interface ' + interface_2['name'].encode('ascii') + b' \r')
                                    tn.write(b'ip vrf forwarding vpn1' + interface_2['vrf'] + b' \r')
                            
                            
            # -------------------------------------------- Fin iBGP -----------------------------------------            
            

            # -------------------------------------------- MPLS --------------------------------------------





            # -------------------------------------------- Fin MPLS ----------------------------------------

            # -------------------------------------------- MPLS-VPN ----------------------------------------




            

            # -------------------------------------------- Fin MPLS-VPN ------------------------------------








    print('Fin de la configuration Telnet !\n')
        
