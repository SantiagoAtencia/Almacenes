# This file contains the API endpoints for the FastAPI application
import socket
import logging
from fastapi import APIRouter, Body, Request
#from webserver import node  # Import the global node object from the main module

router = APIRouter()

from node import node # global node object



#####  API endpoints #####

@router.get("/info")    
def get_info():
    " return info: node name, ip, port and list of peers"
    logging.debug("in get_info")
    return {"name": node.name, "ip": node.ip, "port": node.port, "peers": node.peers}

@router.get("/items")
def get_items():
    "return dictionary with items and quantity"
    logging.debug("in get_items")
    return node.inventory   #dict converted to json

@router.get("/items/{item}")
def get_item(item: str):
    "return quantity of item or 0 if not found"
    logging.debug(f"in get_item {item}")
    return {"item": item, "quantity": node.inventory.get(item, 0)}


@router.post("/items/inc/{item}/{quantity}")
def inc_item(item: str, quantity: int):
    "add quantity of item or creates it"
    logging.debug(f"in inc_item {item} {quantity}")
    node.inventory[item] = node.inventory.get(item, 0) + quantity
    return {"item": item, "quantity": node.inventory[item]}


@router.post("/items/dec/{item}/{quantity}")
def dec_item(item: str, quantity: int):
    "subtract quantity of item error if not enough"
    logging.debug(f"in dec_item {item} {quantity}")
    if node.inventory.get(item, 0) < quantity:
        return {"error": "not enough items", "item": item, "quantity": node.inventory.get(item, 0)}
    node.inventory[item] -= quantity
    return {"item": item, "quantity": node.inventory[item]}


@router.post("/join/{peer_name}/{peer_ip}/{peer_port}")
def join_request(peer_name: str, peer_ip: str, peer_port: int):
    "request from a new peer to the join my group of peers"
    logging.debug(f"in join_rq {node.name} <-- {peer_name} {peer_ip}:{peer_port}")
    node.add_peer(peer_name, peer_ip, peer_port)
    node.save_to_file()
    response = {"peers": node.peers, "version": node.version}
    logging.debug(f"join_rq handler response: {response}")
    return response


## sync version: get the list of peers from the peer and update the local list
##  if remote version is equal : do nothing
##  if remote version is greater: update the local list
##  if remote version is lower: send the local list to the peer as response
@router.post("/sync/")
def sync_request(
    remote_node: dict = Body(...),
    remote_version: int = Body(...),
    remote_peers: dict = Body(...)
):
    "sync request to a peer"
    # remote_node = {name, ip, port}
    # remote_peers = {name: (ip, port)}
    logging.debug(f"in sync_rq {node.name} <-- {remote_node['name']}")
    if remote_version == node.version:
        return {"version": remote_version}
    
    elif remote_version > node.version: # update local list#
        node.peers = remote_peers
        node.version = remote_version
        node.save_to_file()
        return {"version": remote_version}
    else:
        return {"peers": node.peers, "version": node.version} # send local list to peer