import time
import os
import subprocess
import zmq
import pytest

# constants:

NODE_NAME = "node1"
SOCKET_PATH = f"tcp://localhost:5555"
DATASERVER_PATH = "../src/dataserver.py"  # dataserver.py path, relative to the test file:

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
        child = subprocess.Popen(["python3", DATASERVER_PATH])  # Start the child process
        time.sleep(1)  # Wait for the server to start
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
        socket.connect(f"{SOCKET_PATH}")
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
    socket.send_json({"accion": "exit"})
    child.wait()  # Wait for the child process to finish
    logging.info("Dataserver stopped")
    logging.info("Tests finished")
    socket.close()
    context.term()
    logging.info("ZeroMQ context terminated")


# tests:
# test the connection to the server via zmq:
def test_connection(socket):
    logging.debug(f"soket: {socket}")
    socket.send_json({"accion": "get_node_name"})
    response = socket.recv_json()
    assert response["node_name"] == NODE_NAME


def test_add_item(socket):
    socket.send_json({"accion": "annadir", "nombre": "manos", "cantidad": 100})
    response = socket.recv_json()
    # correct response: {"status": "success", "accion": "annadir", "nombre": "manos", "cantidad": 100}
    assert response["status"] == "success"


# test to remove de data base (realy rename it) and
# and test if the server can handle the error: create a new empty database

def test_remove_db(socket):
    socket.send_json({"accion": "remove_db", "nombre": "almacen1"})
    response = socket.recv_json()
    assert response["status"] == "success"
    socket.send_json({"accion": "get_node_name"})
    response = socket.recv_json()
    logging.debug(response)
    assert response["node_name"] == NODE_NAME

    # test that the database is empty
    socket.send_json({"accion": "ver"})
    response = socket.recv_json()
    assert response["inventario"] == []

    # test to add an item to the empty database
    socket.send_json({"accion": "annadir", "nombre": "pies", "cantidad": 10})
    response = socket.recv_json()
    assert response["status"] == "success"
    socket.send_json({"accion": "get_item_quantity", "nombre": "pies"})
    response = socket.recv_json()
    logging.debug(response)
    assert response["cantidad"] == 10

    # test to add other item and check the inventory has 2 items
    socket.send_json({"accion": "annadir", "nombre": "manos", "cantidad": 100})
    response = socket.recv_json()
    assert response["status"] == "success"
    socket.send_json({"accion": "ver"})
    response = socket.recv_json()
    logging.debug(response)
    assert response["status"] == "success"  # inventory is a list of tuples (item, cantidad)

    # example of response: {"status": "success", "inventory": [("pies", 10), ("manos", 100)]}


# test to remove an item from the inventory
def test_remove_item(socket):
    # read the current cantidad of the item
    socket.send_json({"accion": "get_item_quantity", "nombre": "pies"})
    response = socket.recv_json()
    current_quantity = response["cantidad"]
    # remove the item
    socket.send_json({"accion": "sacar", "nombre": "pies", "cantidad": current_quantity})
    response = socket.recv_json()
    logging.debug(response)
    assert response["status"] == "success"

    # check that the item is not in the inventory
    socket.send_json({"accion": "get_item_quantity", "nombre": "pies"})
    response = socket.recv_json()
    assert response["cantidad"] == 0


# test to remove more items than the inventory has

def test_remove_more_items_than_inventory(socket):
    # add some items to the inventory
    socket.send_json({"accion": "annadir", "nombre": "cabezas", "cantidad": 10})
    response = socket.recv_json()
    logging.debug(response)
    assert response["status"] == "success"

    # read the current cantidad of the item
    socket.send_json({"accion": "get_item_quantity", "nombre": "cabezas"})
    response = socket.recv_json()
    current_quantity = response["cantidad"]

    # remove more items than the inventory has
    socket.send_json({"accion": "sacar", "nombre": "cabezas", "cantidad": current_quantity + 1})
    response = socket.recv_json()
    logging.debug(response)
    assert response["status"] == "error"

    # check that the cantidad is the same
    socket.send_json({"accion": "get_item_quantity", "nombre": "cabezas"})
    response = socket.recv_json()
    assert response["cantidad"] == current_quantity
