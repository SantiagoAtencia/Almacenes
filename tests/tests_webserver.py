#test_webserver.py

## pruebas de la API REST
# probra que el servidor web responde a las peticiones HTTP: / debe dar información del nodo
import logging
import os
import subprocess
import pytest
import requests

#constants:
NODE_NAME = "node1"
DB_PATH = f"db/{NODE_NAME}/almacen.db"
HOST = "localhost"
PORT = 10000
BASE_URL = f"http://{HOST}:{PORT}/"
WEBSERVER_PATH = "../src/webserver.py" #webserver.py path, relative to the test file:





@pytest.fixture(scope="module", autouse=True)
def setup_tests():

    # start the web server
    logging.info("Starting the web server")
 
    try:
        child = subprocess.Popen(["python3", WEBSERVER_PATH]) # Start the child process
        time.sleep(1)                                   # Wait for the server to start
    except Exception as e:
        logging.error(f"Error starting the dataserver: {e}")
        raise e
    web_server_proxy = WebServerClient(BASE_URL)

    yield web_server_proxy
    logging.info("Stopping the web server")
    ## sent a stop REST request
    web_server_proxy.stop()
                         
    child.wait()                                # Wait for the child process to finish



def test_connection(setup_tests):
    server = setup_tests
    assert server.get_info()["node_name"] == NODE_NAME


def test_add_item(setup_tests):
    server = setup_tests
    response = server.increment("manos", 100)
    assert response["resp"] == "OK"
    assert response["quantity"] == 100
    

# test to remove de data base (realy rename it) and 
# and test if the server can handle the error: create a new empty database
def test_remove_db(setup_tests):
    rename_db()
    server = setup_tests
    assert server.get_info()["info"] == "New database created"
      
    # test that the database is empty
    assert server.get_inventory()["inventory"] == []

    # test to add an item to the empty database
    server.increment("pies", 10)
    assert server.get_item_quantity("pies") == 10
    
    # test to add other item and check the inventory has 2 items
    server.increment("manos", 100)
    assert len(server.get_inventory()["inventory"]) == 2
    # example of response: {"inventory": [("pies", 10), ("manos", 100)]}

# test to remove an item from the inventory
def test_remove_item(setup_tests):
    server= setup_tests
    # read the current quantity of the item
    current_quantity = server.get_item_quantity("pies")
    # remove the item
    response = server.decrement("pies", current_quantity)
    assert response["resp"] == "OK"
    # check the item was removed, quantity is 0
    assert server.get_item_quantity("pies") == 0

# test to remove more items than the inventory has
# add some items to the inventory, read the current quantity and try to remove more than that
def test_remove_more_items_than_inventory(setup_tests):
    server = setup_tests
    # add some items to the inventory
    response = server.increment("pies", 10)
    # read the current quantity of the item
    current_quantity = server.get_item_quantity("pies")
    # try to remove more items than the inventory has
    response = server.decrement("pies", current_quantity + 1)
    assert response["resp"] == "ERROR"
    # check the item was not removed, quantity is still the same
    assert server.get_item_quantity("pies") == current_quantity

    

  
    
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

####################################3
## Proxy object:

class WebServerClient:
    def __init__(self, base_url):
        self.base_url = base_url
        
    def get_info(self)->dict:
        "returns a dictionary with the info of the node"
        response = requests.get(self.base_url)
        logging.info(response.json())
        assert response.status_code == 200
        return response.json()
    
    def increment(self, objeto:str, quantity:int)->dict:
        "adds quantity items of the object to the inventory"
        msg = {"command": "inc", "objeto": objeto, "quantity": quantity}
        response = requests.post(f"{self.base_url}command", json=msg)
        logging.info(response.json())
        assert response.status_code == 200
        return response.json()
    
    def decrement(self, objeto:str, quantity:int)->dict:
        "removes quantity items of the object from the inventory"
        msg = {"command": "dec", "objeto": objeto, "quantity": quantity}
        response = requests.post(f"{self.base_url}command", json=msg)
        logging.info(response.json())
        assert response.status_code == 200
        return response.json
    
    def get_inventory(self)->dict:
        "returns a dictionary with the inventory"
        response = requests.get(f"{self.base_url}objetos/")
        logging.info(response.json())
        assert response.status_code == 200
        return response.json()

    def get_item_quantity(self, objeto:str)->int:
        "returns the quantity of the object in the inventory"
        response = requests.get(f"{self.base_url}objetos/{objeto}")
        logging.info(response.json())
        return response.json()["quantity"]

    def stop(self):
        "stops the web server"
        response = requests.get(f"{self.base_url}stop")
        logging.info(response.json())
        assert response.status_code == 200
        return response.json()
  