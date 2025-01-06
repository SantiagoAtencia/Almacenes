

HTTP_TIMEOUT = 5

## gropup object
#  - group_state: alone, grouped



## broadcast a message to all group peers.  
    ##  return the list of group peers,
   #         the list is a list, each item is a tuple of (nodename, timeout:bool, response)

## perdiodic task:
    # if i am in agrup, broadcast a ping message (the response to the ping is the node_name)
    # if i am alone, change to connection_state: disconnected
    # when not disconnected, change state to connected, and ask for the group info again




## at shutdown (ctrl-c or ordered exit),: save the group info to a JSON file




import logging
import os
import requests
import json


class Group:
    def __init__(self, localnode,exposed_local_IP):
        self.my_name = localnode.name
        self.exposed_local_IP = exposed_local_IP
        self.port = localnode.port
        self.group_state = "alone"                      # alone, grouped
        self.group_info = {"version": 0, "peers": {}}   # version 0 = alone
            ## peers: dict of {name: {IP, port}}
        self.group_info_file = localnode.path + "/group_info.json"
        
    def create(self):
        """create a new group with only the local node"""
        self.group_info = {"version": 1, "peers": {self.my_name: {"IP": self.exposed_local_IP, "port": self.port}}}
        self.group_state = "grouped"
        self.save_to_file()

    ### get group info: just read group.group_info
    
    def version_up(self):
        """increment the group version"""
        self.group_info["version"] += 1
        

    def add_peer(self, new_name, new_IP, new_port):
        """add or update a new peer to the group"""
        self.group_info["peers"][new_name] = {"IP": new_IP, "port": new_port}
        self.version_up()
        self.save_to_file()

    def remove_peer(self, peer_name):
        """remove a peer from the group"""
        self.group_info["peers"].pop(peer_name)
        self.version_up()
        self.save_to_file()

    def save_to_file(self):
        """save the group info to a json file"""
        with open(self.group_info_file, "w") as f:
            json.dump(self.group_info, f)

    def load_from_file(self):
        """load the group info from a json file"""
        if os.path.exists(self.group_info_file):
            with open(self.group_info_file, "r") as f:
                self.group_info = json.load(f)
                self.group_state = "grouped"
                return True
        else:
            return False
    
    
    def on_startup(self):
        """check the group state at startup"""
        if self.load_from_file():
            self.group_state = "grouped"
            return True
        else:
            self.group_state = "alone"
            return False
        
    def on_shutdown(self):
        """save the group info at shutdown"""
        self.save_to_file()

    #### actions with remotes:

    def ping_host(self, remote_host, remote_port):
        """ping a remote host to get its name or None if not reachable"""
        remote_host= REST_server_proxy(remote_host, remote_port)
        return remote_host.ping()


    def join_to(self, remote_host, remote_port):
        """ask for Enter to a group to a remote host

        remote_host, remote_port: the host and port of a existing group peer
        """
        remote_host= REST_server_proxy(remote_host, remote_port)
        group_info = remote_host.request_join(self.my_IP, self.port, self.my_name)
        
        if group_info:
            self.group_info = group_info
            self.group_state = "grouped"
            return True
        else:
            return False
        
    def leave(self):
        """leave the group"""
        #broadcast the leave message, 
        # and return to state:alone
        for peer_name, peer_info in self.group_info["peers"].items():
            remote_host = REST_server_proxy(peer_info["IP"], peer_info["port"])
            remote_host.request_leave(self.my_name)

        self.group_info = {"version": 0, "peers": {}}
        self.group_state = "alone"
        self.save_to_file()    


    def broadcast_group_info(self):
        """broadcast the group info to all group peers"""
        for peer_name, peer_info in self.group_info["peers"].items():
            remote_host = REST_server_proxy(peer_info["IP"], peer_info["port"])
            remote_host.send_group_info(self.group_info)

    
        
        


######################
class REST_server_proxy:
    "proxy to a remote REST API server"
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.timeout = HTTP_TIMEOUT

#   ping returns the node_name of the remote server
#   if the server is not reachable, returns None (timeout)
#   log the errors to DEBUG
def ping(self):
    """ping the remote server"""
    url = f"{self.base_url}/ping"
    try:
        logging.debug(f"pinging {url}")
        response = requests.get(url, timeout=self.timeout)
        logging.debug(f"ping response: {response}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.debug(f"ping error: {e}")
        return None
    
def request_join(self, new_host, new_port, new_name):
    """ask for enter to a group
    
    returns the group hosts info if accepted, None if not
    """
    url = f"{self.base_url}/join_request"
    data = {"name": new_name, "host": new_host, "port": new_port}
    try:
        logging.debug(f"asking enter_group to {url}")
        response = requests.post(url, json=data, timeout=self.timeout)
        logging.debug(f"enter_group response: {response}")
        # if acepted, returns the group hosts info
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.debug(f"enter_group error: {e}")
        return None
    
def send_group_info(self, group_info):
    """send the group info to a remote server"""
    url = f"{self.base_url}/update_group_info"
    try:
        logging.debug(f"sending group_info to {url}")
        response = requests.post(url, json=group_info, timeout=self.timeout)
        # no response expected
    except requests.exceptions.RequestException as e:
        logging.debug(f"group_info error: {e}")
        # if not reachable, do nothing

def request_leave(self,node_name):
    """ask for leave the group"""
    url = f"{self.base_url}/leave_request"
    data = {"node": node_name}   # my name
    try:
        logging.debug(f"asking leave_group to {url}")
        response = requests.post(url, json=data, timeout=self.timeout)
        logging.debug(f"leave_group response: {response}")
        # no response expected
    except requests.exceptions.RequestException as e:
        logging.debug(f"leave_group error: {e}")
        # if not reachable, do nothing

    