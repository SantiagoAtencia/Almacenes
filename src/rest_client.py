## resrt_client.py
# a class whose objects are proxy for remote nodes

import logging
import requests

class RESTClient:
    def __init__(self, host, port): 
        "initialize the REST client with the host(dns name or IP) and port of the remote node"
        self.adress = f"http://{host}:{port}"
        logging.debug(f"new REST client : {self.adress}")
    
    def get_info(self):
        "return info: node name, ip, port and list of peers"
        return requests.get(f"{self.adress}/api/info").json()
    
    def get_items(self):
        "return dictionary with items and quantity"
        return requests.get(f"{self.adress}/api/items").json()
    
    def get_item(self, item):
        "return quantity of item or 0 if not found"
        return requests.get(f"{self.adress}/api/items/{item}").json()
    
    def inc_item(self, item, quantity):
        "add quantity of item or creates it"
        url=f"{self.adress}/api/items/inc/{item}/{quantity}"
        logging.debug("request post --->"+ url)
        return requests.post(url).json()
    
    def dec_item(self, item, quantity):
        "subtract quantity of item error if not enough"
        return requests.post(f"{self.adress}/api/items/dec/{item}/{quantity}").json()
    
    def join_request(self, peer_name, peer_ip, peer_port):
        "request to a remote peer to the join its group of peers"
        # the self object is a proxy for the REMOTE node
        ## make the POST request with a 2 seconds timeout
        # if timeout, or not reachable, or any other error in HTTP request, return an error
        try:
            res = requests.post(f"{self.adress}/api/join/{peer_name}/{peer_ip}/{peer_port}", timeout=2)
            logging.debug(f"join_request REST response: {res.text}")

        except requests.exceptions.RequestException as e:
            return {"error": f"error joining to peer: {e}"}

        return res.json()
    
    def sync_request(self,node, version, peers_list):
        "sync request to a REMOTE peer"
        # the self object is a proxy for the REMOTE node

        # remote_node = {name, ip, port}
        # remote_peers = {name: (ip, port)}
        logging.debug(f"in sync_rq to {self.adress}")
        my_node_data = {"name": node.name, "ip": node.ip, "port": node.port}
        url=f"{self.adress}/api/sync/"
        data = {
            "remote_node": my_node_data,
            "remote_version": version,
            "remote_peers": peers_list
        }
        logging.debug(f"request post --->"+ url + " data: "+str(data))
        try:
            res = requests.post(url, json=data, timeout=2)
            logging.debug(f"sync_request REST response: {res.text}")
            res.raise_for_status()  # Raise an error for bad status codes
            return res.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return {"error": f"Request failed: {e}"}

    
    
    




