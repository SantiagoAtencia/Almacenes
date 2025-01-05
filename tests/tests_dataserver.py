import time
import os
import subprocess
import zmq
import pytest

#constants:

NODE_NAME = "node1"
DB_PATH = f"db/{NODE_NAME}/almacen.db"
SOCKET_PATH = f"/tmp/almacen_{NODE_NAME}.sock"
DATASERVER_PATH = "../src/dataserver.py" #dataserver.py path, relative to the test file:

## configure the logging system to print to the console
import logging
import sys
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# This fixture runs once before all tests in the file
@pytest.fixture(scope="module", autouse=True)
def socket():
    print("en setup_once")
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Starting the tests")
    ## Test the dataserver
    logging.debug("Starting the dataserver")
    try:
        child = subprocess.Popen(["python3", DATASERVER_PATH]) # Start the child process
        time.sleep(1)                                   # Wait for the server to start
    except Exception as e:
        logging.debug(f"Error starting the dataserver: {e}")
        logging.error(f"Error starting the dataserver: {e}")
        raise e
    
    
    logging.info("Dataserver launched")
    # Create a ZeroMQ context, create a socket, and connect to the child's UNIX domain socket
    logging.info("Connecting to the dataserver with ZeroMQ")
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    try:
        socket.connect(f"ipc://{SOCKET_PATH}")
        # Set timeouts for send and receive operations
        socket.setsockopt(zmq.SNDTIMEO, 2000)  # 2000 ms = 2 seconds
        socket.setsockopt(zmq.RCVTIMEO, 2000)
    except Exception as e:
        logging.debug(f"Error connecting to the dataserver: {e}")
        logging.error(f"Error connecting to the dataserver: {e}")
        raise e
    
    logging.info(f"Connected to the dataserver ZMQ socket: {socket}")
    yield socket

    # This code runs after all tests have finished:
    logging.info("Stopping the dataserver")
    socket.send_json({"command": "exit"})
    child.wait()                                # Wait for the child process to finish
    logging.info("Dataserver stopped")
    logging.info("Tests finished")
    socket.close()
    context.term()
    logging.info("ZeroMQ context terminated")



# tests:
# test the connection to the server via zmq:
def test_connection(socket):
    logging.debug(f"soket: {socket}")
    socket.send_json({"command": "get_node_name"})
    response = socket.recv_json()
    assert response["node_name"] == NODE_NAME

def test_add_item(socket):
    socket.send_json({"command": "inc", "objeto": "manos", "quantity": 100})
    response = socket.recv_json()
    # correct response: {"resp": "OK", "command": "inc", "objeto": "manos", "quantity": 100}
    assert response["resp"] == "OK"

# test to remove de data base (realy rename it) and 
# and test if the server can handle the error: create a new empty database

def test_remove_db(socket):
    rename_db()
    socket.send_json({"command": "get_node_name"})
    response = socket.recv_json()
    logging.debug(response)
    assert response["node_name"] == NODE_NAME
    assert response["info"] == "New database created"
    

    # test that the database is empty
    socket.send_json({"command": "get_inventory"})
    response = socket.recv_json()
    assert response["inventory"] == []
    
    # test to add an item to the empty database
    socket.send_json({"command": "inc", "objeto": "pies", "quantity": 10})
    response = socket.recv_json()
    assert response["resp"] == "OK"
    socket.send_json({"command": "get_item_quantity", "objeto": "pies"})
    response = socket.recv_json()
    logging.debug(response)
    assert response["quantity"] == 10
    

    # test to add other item and check the inventory has 2 items
    socket.send_json({"command": "inc", "objeto": "manos", "quantity": 100})
    response = socket.recv_json()
    assert response["resp"] == "OK"
    socket.send_json({"command": "get_inventory"})
    response = socket.recv_json()
    logging.debug(response)
    assert len(response["inventory"]) == 2 # inventory is a list of tuples (item, quantity)

    # example of response: {"resp": "OK", "inventory": [("pies", 10), ("manos", 100)]}

# test to remove an item from the inventory
def test_remove_item(socket):
    # read the current quantity of the item
    socket.send_json({"command": "get_item_quantity", "objeto": "pies"})
    response = socket.recv_json()
    current_quantity = response["quantity"]
    # remove the item
    socket.send_json({"command": "dec", "objeto": "pies", "quantity": current_quantity })
    response = socket.recv_json()
    logging.debug(response)
    assert response["resp"] == "OK"
    
    # check that the item is not in the inventory
    socket.send_json({"command": "get_item_quantity", "objeto": "pies"})
    response = socket.recv_json()
    assert response["quantity"] == 0

 # test to remove more items than the inventory has

def test_remove_more_items_than_inventory(socket):
    # add some items to the inventory
    socket.send_json({"command": "inc", "objeto": "cabezas", "quantity": 10})
    response = socket.recv_json()
    logging.debug(response)
    assert response["resp"] == "OK"
    
    # read the current quantity of the item
    socket.send_json({"command": "get_item_quantity", "objeto": "cabezas"})
    response = socket.recv_json()
    current_quantity = response["quantity"]
      
    # remove more items than the inventory has
    socket.send_json({"command": "dec", "objeto": "cabezas", "quantity": current_quantity + 1 })
    response = socket.recv_json()
    logging.debug(response)
    assert response["resp"] == "ERRROR"
    
    # check that the quantity is the same   
    socket.send_json({"command": "get_item_quantity", "objeto": "cabezas"})
    response = socket.recv_json()
    assert response["quantity"] == current_quantity


    


   







# auxilar function to rename the database 
# renames the database to a backup file that does not exist
#  so never overwrite other backup files
def rename_db():
    # find a name that does not exist
    i = 0
    while os.path.exists(f"{DB_PATH}.bak{i}"):
        logging.debug(f"{DB_PATH}.bak{i} exists")
        i += 1
    os.rename(DB_PATH, f"{DB_PATH}.bak{i}")
    logging.debug(f"{DB_PATH} renamed to {DB_PATH}.bak{i}")
