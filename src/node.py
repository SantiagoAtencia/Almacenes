
import json
import logging
import os

from rest_client import RESTClient

class Node:
    def __init__(self):
        self.name = ""
        self.ip = ""
        self.port = 0
        self.inventory = {}
        self.peers = {} #Dict[str, Tuple[str, int]]
        self.version = 0
        self.data_path = ""

    def init(self, name, port):
        "initialize the node with name, ip and port"
        self.name = name
        self.port = port
        app_path = os.path.dirname(os.path.abspath(__file__))   
        self.data_path= os.path.join(app_path, node.name)
        #create the directory if not exists
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        self.load_from_file()
        logging.debug(f"node initialized:     {self}") 

        

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
                # get the ip from the peers list
                self.ip = self.peers.get(self.name, ("",0))[0]
        else:
            logging.debug(f"file {filename} not found")
        #in any case, sync with the peers
        self.broadcast_sync()    

    def add_peer(self, name, ip, port):
        "add a peer to the list of peers, upgrade the version and save to file"
        self.peers[name] = (ip, port)
        self.version +=1
        self.save_to_file()
        self.broadcast_sync()


    def join_to_peer(self, remote_ip, remote_port):
        "join to the list of peers of a remote peer"
        rest_client = RESTClient(remote_ip, remote_port)
        result = rest_client.join_request(self.name, self.ip, self.port)

        if "error" in result:
            logging.debug(f"error joining to peer: {result['error']}")
        else:
            self.peers = result["peers"]
            self.version = result["version"]
            self.save_to_file()    

    def broadcast_sync(self):
        "send the list of peers to all peers, except to the local node"
        for peer_name in self.peers:
            if peer_name != self.name:
                rest_client = self.get_RESTClient_for_peer(peer_name)
                if rest_client is not None:
                    result = rest_client.sync_request(self, self.version, self.peers)
                    #if receiver version is greater, update the local list
                    if "error" in result:
                        logging.debug(f"error syncing with peer: {result['error']}")
                    elif "peers" in result:
                        self.peers = result["peers"]
                        self.version = result["version"]
                        self.save_to_file()
                    else:
                        logging.debug(f"unexpected response: {result}")

                    
  


    def __str__(self):
        return f"Node(name={self.name}, ip={self.ip}, port={self.port}, peers={self.peers}, version={self.version}, data_path={self.data_path})"  

# create a global node object, empty   
node = Node()