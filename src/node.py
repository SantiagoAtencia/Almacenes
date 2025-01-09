from dataclasses import dataclass
import json
import logging
import os

from rest_client import RESTClient

@dataclass  
class Node:
    name: str=""
    ip: str = ""
    port: int = 0
    inventory: dict = {}
    peers: dict  = {} #Dict[str, Tuple[str, int]]
    version: int =0
    data_path: str = ""

    def init(self, name, port):
        "initialize the node with name, ip and port"
        self.name = name
        self.port = port
        app_path = os.path.dirname(os.path.abspath(__file__))   
        self.data_path= os.path.join(app_path, "data")
        self.load_from_file()

        

    def set_ip(self, ip):
        " set the ip of the node and uptade the peers list"
        self.ip = ip
        self.peers[self.name] = (self.ip, self.port)

    def get_RESTClient_for_peer(self,node_name):
        "return a RESTClient object for the node in the list of peers"
        if node_name in self.peers:
            peer= self.peers[node_name]
            return RESTClient(peer[0], peer[1]) #host, port
        else:
            return None
        
    def get_my_RESTClient(self):
        "return a RESTClient object for the local node"
        return RESTClient(self.ip, self.port)

    def save_to_file(self):
        "save the version and list of peers to a json file"
        filename = os.path.join(self.data_path, "peers.json")
        data = {"version": self.version, "peers": self.peers}
        with open(filename, "w") as f:
            json.dump(data, f)
            logging.debug(f"saved to {filename}")
            
    def load_from_file(self):
        "load the version and list of peers from a json file"
        filename = os.path.join(self.data_path, "peers.json")
        if os.path.exists(filename):    
            with open(filename, "r") as f:
                data = json.load(f)
                self.version = data["version"]
                self.peers = data["peers"]
                logging.debug(f"loaded from {filename}")
        else:
            logging.debug(f"file {filename} not found")

    def add_peer(self, name, ip, port):
        "add a peer to the list of peers"
        self.peers[name] = (ip, port)
        self.save_to_file()

        

# create a global node object, empty   
node = Node()