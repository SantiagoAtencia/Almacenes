## resrt_client.py
# a class whose objects are proxy for remote nodes

import requests

class RESTClient:
    def __init__(self, host, port): 
        "initialize the REST client with the host(dns name or IP) and port of the remote node"
        self.adress = f"http://{host}:{port}"
    
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
        return requests.post(f"{self.adress}/api/items/inc/{item}/{quantity}").json()
    
    def dec_item(self, item, quantity):
        "subtract quantity of item error if not enough"
        return requests.post(f"{self.adress}/api/items/dec/{item}/{quantity}").json()
    
    




