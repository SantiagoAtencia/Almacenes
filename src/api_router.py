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
    return {"name": node.name, "ip": node.ip, "port": node.port, "peers": node.inventory}