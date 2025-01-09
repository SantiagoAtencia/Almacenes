

## FastApi + NiceGUI server
#
# 
# UI:  (in UI.py module)
    #  /ui/ main page. Show info: node, peers_list (version). menúfor other pages
    #  /ui/selectIP/ UI select IP
    #  /ui/peer_info/ UI to show info about peer
    #  /ui/items shows list of items and quantity
    #  /ui/item/{item} shows quantity of item. 
    #       Dialog, to select o write a new item (combo box)
    #       Dialog to add or subtract quantity to selected item
    #  /ui/peers/item/{item} shows quantity of item in all peers
    #  /ui/join peer: dialog to join to a group of peers

# REST: (in api_route.py module)  /api/...
    # GET:
    # /info: return info about node, and list of peers
    # /items: return dictionary with items and quantity
    # /items/{item}: return quantity of item
    # POST: 
    # /items/inc/{item}/{quantity}: add quantity of item
    # /items/dec/{item}/{quantity}: subtract quantity of item

## data: Node:(name, ip, port)  IP is the exposed IP. If IP="" no exposed IP
## local_data: dictionary {item,quantity}.

## other modules: 
# remote.py, to manage remote peers: REST client
# local.py, to manage local data: dictionary with items and quantity
# list_manager.py, to manage list of peers


# class node, all local node data, dataclass
import logging
import os
import psutil
from dataclasses import dataclass
import socket
from fastapi import FastAPI
from nicegui import app as nicegui_app, ui
import api_router

from node import node # global node object


# Configure logging
logging.basicConfig(level=logging.DEBUG)




####### startup ##########
# get the NODE_NAME and PORT from environment variables
# get the PEERS from a file

# get environment variables, if not supplied, error and exit
NODE_NAME = os.getenv("NODE_NAME")
if NODE_NAME is None:
    logging.error("NODE_NAME environment variable not set")
    exit(1)

PORT = os.getenv("PORT")
if (PORT is None or PORT==""):
    logging.error("PORT environment variable not set")
    exit(1)
logging.info(f"NODE_NAME={NODE_NAME}, PORT={PORT}")

node.name= NODE_NAME  
node.port= PORT # not IP exposed yet



################# main program  ####################
app = FastAPI()         # Create FastAPI app   

logging.debug("mounting NiceGUI")
       # Mount NiceGUI under a specific path

# Include routers for REST and UI endpoints
#app.include_router(ui_router.router, prefix="/ui", tags=["UI"])
app.include_router(api_router.router, prefix="/api", tags=["API"])
logging.debug("FastAPI app setup complete")
api_router.node = node  # pass node object to api_router

############  auxiliary functions ##########

## list all IP addresses available IPV4 in this OS
def list_ip_addresses():
  return [
        addr.address
        for interface, addrs in psutil.net_if_addrs().items()
        for addr in addrs
        if addr.family == socket.AF_INET
    ]


########################## UI ############################

# Main page
@ui.page('/ui')
def show():
    " Show info: node, peers_list (version). menú for other pages"
    ui.label(f"Node: {node.name}, IP: {node.ip}, Port: {node.port}")
    ui.label(f"Peers: {node.peers}")
    ui.label(f"Version: {node.version}")
    ui.link("Select IP", "/ui/selectIP")  # ui.button("Peer Info", onclick=peer_info)
   # ui.button("All Items inventory", onclick=items)
   
# Select IP page
@ui.page('/ui/selectIP')
def selectIP():
    "UI to select IP"
    selected_ip = "" # selected IP for binding
    ui.label("Select IP")
    current_label = ui.label("Current exported IP: " + node.ip)
    #show all available IP addresses in a list
    ip_list = list_ip_addresses()
    #TODO: if node.ip is previously selected, show it selected
    ui.radio(ip_list, value=ip_list[0],  on_change=lambda e: update(e.value))

    def update(ip):
        global node
        node.ip = ip
        node.peers[node.name] = (node.ip, node.port)
        logging.debug(f"selected_ip={ip}")
        current_label.text = "Current exported IP: " + ip






# Integrate with your FastAPI Application
ui.run_with(
    app=app,
    storage_secret='pick your private secret here',
)