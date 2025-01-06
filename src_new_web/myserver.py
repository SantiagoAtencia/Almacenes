# REST server with FastAPI
# echo server


# to run the server from Makefile: NODE_NAME=$(NODE_NAME) PORT=$(PORT) fastapi dev $(SRC)/myserver.py --reload --port $(PORT)
#
# it must accep 2 command line arguments: -n node_name -p port
# it must return, in json, the node_name and the port in the response to <URL>/info or <URL>
# it must return the echo in json of the request in the response to <URL>/echo/<text>,
#    where <text> is the text to be echoed ans the node_name in the response


# to run the server: fastapi run myserver:app --reload
from dataclasses import dataclass
import os
import logging
import socket
import threading
import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import psutil

   ## import the group class
from group import Group


logging.basicConfig(level=logging.INFO)

#################### global variables ####################

@dataclass
class Nodeserver:
    name: str
    port: int
    path: str   ## full path to the directory where save the group info, socket, etc

# Check for the environment variable NODE_NAME at startup
NODE_NAME = os.getenv("NODE_NAME")
if NODE_NAME is None or NODE_NAME == "":
    logging.error("NODE_NAME is not set")
    exit(1)

# Get the tcp port from the fastapi framework:
port = os.getenv("PORT")
logging.info("-NODE_NAME: %s", NODE_NAME)
logging.info("-PORT: %s", port)

localnode = Nodeserver(NODE_NAME, port, "temp") ## the path is not known yet

group = Group(localnode, "") ## the IP is not known yet

#################### FastAPI (MAIN) ####################
async def lifespan(app: FastAPI):
    # Startup phase
    localnode = Nodeserver(NODE_NAME, port, get_nodeserver_dir(NODE_NAME))
    print("App is starting up...")
    ## launch a periodic task in a daemon thread
    threading.Thread(target=periodic_task, daemon=True).start()
    
    ## group startup:
    group.on_startup()

    
    yield  # FastAPI runs until shutdown
    # Shutdown phase
    print("App is shutting down...")
    group.on_shutdown()

app = FastAPI(lifespan=lifespan)



   


 ################### REST API ####################
@app.get("/")
@app.get("/info")
def read_root():
    return {"node_name": NODE_NAME, "port": port}


@app.get("/echo/{text}")
def read_item(text: str):
    return {"node_name": NODE_NAME, "echo": text}


@app.get("/local_ips")
def local_ips():
    return {"ips": get_local_ips()}

@app.get("/group_info")
def group_info():
    return group.get_group_info()

@app.post("/join_request")  #a request to join to a group from a new peer
def join_request(new_name: str, new_IP: str, new_port: int):
    #check if i am not in a group: return error
    if group.group_state == "alone":
        return {"error": "I am not alone"}
    # add or update the new peer in the group list

    #check if the new peer answers:
    answer_name = group.ping_host(new_IP, new_port)
    # if the new peer answers the same name as the request, add it to the group
    #    if ok, add the peer to the group list, increment the version, and return the group hosts info
    #      and broadcast the new group info to all group peers
    # if fails, return error message
    if answer_name == new_name:         #accept the new peer
        group.add_peer(new_name, new_IP, new_port)
        group.broadcast_group_info()
        return group.group_info
    else:
        return {"error": "The peer did not answer"}


@app.get("/leave_request")
def leave_request(node_name: str):
    #remove a peer from the group list (updates version and saves to file)
    group.remove_peer(node_name)
    group.broadcast_group_info()
    #no return expected


@app.get("/update_group_info")
def update_group_info(new_group_info):
    """receives a version of the group info from a peer"""
    # if the version is equal: do nothing
    #  else
    #     if the version is greater: update the group info
    #  broadcast the new group info to all group peers if 
    if new_group_info["version"] != group.group_info["version"]:
        if new_group_info["version"] > group.group_info["version"]:  #update
            group.group_info = group_info
            group.save_to_file()
        group.broadcast_group_info()
    else:
        pass ## do nothing, the group info is the same

      
    
### UI: User Interface

#this entry point renders html. shows all the possible IPs. And the user can click and select one
# also shows the current exported IP that is in the group
# the selected will be the Exported IP in the group.
# so another entry point is needed to set the exported IP
@app.get("/ui/select_IP")
def select_IP():
    ip_list= get_local_ips()
    #create the html template:
    html= "<html><body>"
    html+= "<h1> The current exposed IP is:</h1>"
    html+= "<h2>"+group.exposed_local_IP+"</h2>"
    html+= "<h1> Select the IP to be exposed:</h1>"
    for ip in ip_list:
        html+= "<a href='/set_exposed_IP/"+ip+"'>"+ip+"</a><br>"
    html+= "</body></html>"
    return HTMLResponse(content=html)

#this entry point sets the exposed IP in the group
@app.get("/set_exposed_IP/{IP}")
def set_exposed_IP(IP: str):
    group.exposed_local_IP = IP
    return {"node_name": NODE_NAME, "exposed_IP": IP}

@app.get("/purge_node/{node_to_purge}")
def purge_node(node_to_purge: str):
    # removes the node from the group, updates the version, and broadcast the new group info
    group.remove_peer(node_to_purge)
    group.broadcast_group_info()
    return group.group_info


#user interface. Shows the group info, the status of the group, and the group peers
# also shows the exposed IP and the version of the group

# an option to set the exposed IP
# an option to leave the group
# an option to join to a group
@app.get("/ui")
def UI():
    group_info= group.get_group_info()
    logging.info("Group Info: %s", group_info)
    html= "<html><body>"
    html+= "<h1> Group Info:</h1>"
    html+= "<h2> Group State: "+group.group_state+"</h2>"
    html+= "<h2> Group Version: "+str(group_info["version"])+"</h2>"
    html+= "<h2> Group Peers:</h2>"
    for peer in group_info["peers"]:
        html+= "<h3>"+peer+"</h3>"
    html+= "<h1> Exposed IP:</h1>"
    html+= "<h2>"+group.exposed_local_IP+"</h2>"
    html+= "<a href='/ui/select_IP'>Select Exposed IP</a><br>"
    html+= "<a href='/ui/join_group'>Join Group</a><br>"
    html+= "<a href='/ui/leave_group'>Leave Group</a><br>"
    html+= "</body></html>"
    return HTMLResponse(content=html)



################### Helper functions ####################
def get_local_ips():
    ip_addresses = []
    # Iterate over all network interfaces and get the IPs
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            # Check if the address family is AF_INET (IPv4)
            if addr.family == socket.AF_INET:
                ip_addresses.append(addr.address)
    return ip_addresses


def periodic_task():
    while True:
        # Your periodic function logic here
        logging.debug("Doing something every 10 seconds...")
        time.sleep(10)

def get_nodeserver_dir(node_name):
    """Get or create the directory for the node server"""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    # Create a directory for the node server if it doesn't exist
    node_dir = os.path.join(app_dir, node_name)
    if not os.path.exists(node_dir):
        os.makedirs(node_dir)
    return node_dir
    