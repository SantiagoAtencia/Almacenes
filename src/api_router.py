# This file contains the API endpoints for the FastAPI application
import socket
import logging
from fastapi import APIRouter
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

