import time
import os
import subprocess
import zmq
import pytest

# Constants:
NODE_NAME = "nodo1"
DB_PATH = "../AlmacenesPruebas/src/almacen.db"
DATASERVER_PATH = "../AlmacenesPruebas/src/dataserver.py"  # dataserver.py path, relative to the test file

# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@pytest.fixture(scope="module", autouse=True)
def socket():
    logging.info("Starting the tests")
    try:
        child = subprocess.Popen(["python3", DATASERVER_PATH])  # Start the child process
        time.sleep(1)  # Wait for the server to start
    except Exception as e:
        logging.error(f"Error starting the dataserver: {e}")
        raise e

    logging.info("Dataserver launched")
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    yield socket

    logging.info("Stopping the dataserver")
    socket.send_string("salir")  # Send exit command
    child.wait()
    socket.close()
    context.term()


def test_connection(socket):
    socket.send_string("get_node_name")
    response = socket.recv_string()
    assert response == NODE_NAME


def test_add_item(socket):
    socket.send_string("añadir:manos:100")
    response = socket.recv_string()
    assert "Objeto manos añadido con cantidad 100" in response


def test_remove_db(socket):
    socket.send_string("remove_db")
    response = socket.recv_string()
    assert response == "New database almacen1"

    socket.send_string("ver")
    response = socket.recv_string()
    assert "Contenido del almacén:" in response and "manos" not in response

    socket.send_string("añadir:pies:10")
    response = socket.recv_string()
    assert "Objeto pies añadido con cantidad 10" in response

    socket.send_string("añadir:manos:100")
    response = socket.recv_string()
    assert "Objeto manos añadido con cantidad 100" in response


def test_remove_item(socket):
    socket.send_string("sacar:pies:10")
    response = socket.recv_string()
    assert "Objeto pies retirado con cantidad 10" in response

    socket.send_string("ver")
    response = socket.recv_string()
    assert "pies" not in response


def test_remove_more_items_than_inventory(socket):
    socket.send_string("añadir:cabezas:10")
    response = socket.recv_string()
    assert "Objeto cabezas añadido con cantidad 10" in response

    socket.send_string("sacar:cabezas:11")
    response = socket.recv_string()
    assert "Error: Cantidad insuficiente de cabezas en el inventario" in response

    socket.send_string("ver")
    response = socket.recv_string()
    assert "cabezas: 10" in response
