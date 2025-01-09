from dataclasses import dataclass

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

# create a global node object, empty   
node = Node(name="", ip="", port=0, inventory={}, peers={}, version=0)