from dataclasses import dataclass

from rest_client import RESTClient

@dataclass  
class Node:
    name: str
    ip: str 
    port: int
    inventory: dict 
    peers: dict  #Dict[str, Tuple[str, int]]
    version: int 

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

# create a global node object, empty   
node = Node(name="", ip="", port=0, inventory={}, peers={}, version=0)