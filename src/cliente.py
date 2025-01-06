import requests
import os
import argparse
class Inventario:
    def __init__(self, base_url):
        self.base_url = base_url

    def enviar_peticion(self, endpoint, metodo="GET", datos=None):
        url = f"{self.base_url}{endpoint}"
        try:
            if metodo == "GET":
                respuesta = requests.get(url)
            elif metodo == "POST":
                respuesta = requests.post(url, json=datos)
            respuesta.raise_for_status()
            return respuesta.json()
        except requests.RequestException as e:
            print(f"Error: {e}")
            return None

    def añadir_objeto(self, nombre, cantidad):
        datos = {"nombre": nombre, "cantidad": cantidad}
        respuesta = self.enviar_peticion("/inventario/annadir", "POST", datos)
        print(respuesta.get("mensaje", "Error al añadir objeto."))

    def reservar_objeto(self, nombre, cantidad):
        datos = {"nombre": nombre, "cantidad": cantidad}
        respuesta = self.enviar_peticion("/inventario/reservar", "POST", datos)
        print(respuesta.get("mensaje", "Error al reservar objeto."))

    def sacar_objeto(self, nombre, cantidad):
        datos = {"nombre": nombre, "cantidad": cantidad}
        respuesta = self.enviar_peticion("/inventario/sacar", "POST", datos)
        print(respuesta.get("mensaje", "Error al sacar objeto."))

    def sacar_reserva(self, nombre, cantidad):
        datos = {"nombre": nombre, "cantidad": cantidad}
        respuesta = self.enviar_peticion("/inventario/sacar_reserva", "POST", datos)
        print(respuesta.get("mensaje", "Error al sacar reserva."))

    def cancelar_reserva(self, nombre, cantidad):
        datos = {"nombre": nombre, "cantidad": cantidad}
        respuesta = self.enviar_peticion("/inventario/cancelar_reserva", "POST", datos)
        print(respuesta.get("mensaje", "Error al cancelar reserva."))

    def get_item_quantity(self, nombre):
        datos = {"nombre": nombre}
        respuesta = self.enviar_peticion("/inventario/get_item_quantity", "POST", datos)
        if respuesta:
            print(f"La cantidad del objeto '{nombre}' es: {respuesta.get('cantidad', 'Desconocida')}")

    def cambiar_base_datos(self, nombre):
        datos = {"nombre": nombre}
        respuesta = self.enviar_peticion("/inventario/remove_db", "POST", datos)
        print("Base de datos cambiada." if respuesta else "Error al cambiar la base de datos.")
    def get_node_name(self):
        respuesta = self.enviar_peticion("/inventario/get_node_name","GET")
        print(f"El Id del Nodo es: {respuesta.get('node_name','nodo sin ID ¿?¿')}")

    def ver_inventario(self):
        respuesta = self.enviar_peticion("/inventario/ver", "GET")
        if respuesta and isinstance(respuesta.get("inventario"), list):
            print("Inventario actual:")
            for item in respuesta["inventario"]:
                print(f"{item['nombre']}: {item['cantidad']} | Reservados: {item['reservados']}")
        else:
            print("No se pudo obtener el inventario.")


class AlmacenCliente:
    def __init__(self):
        self.inventario = Inventario(f"http://127.0.0.1:{PORT_TCP}")
        print("Cliente de Gestión de Almacén iniciado.")

    def menu(self):
        while True:
            print("\nOpciones:")
            print("1. Añadir objeto")
            print("2. Reservar objeto")
            print("3. Sacar objeto")
            print("4. Sacar reserva")
            print("5. Cancelar reserva")
            print("6. Ver cantidad de objeto")
            print("7. Ver inventario")
            print("8. Cambiar base de datos")
            print("9. Obteber ID del nodo")
            print("10. Salir")

            opcion = input("Selecciona una opción: ")

            if opcion == "1":
                nombre = input("Nombre del objeto: ")
                cantidad = int(input("Cantidad: "))
                self.inventario.añadir_objeto(nombre, cantidad)
            elif opcion == "2":
                nombre = input("Nombre del objeto: ")
                cantidad = int(input("Cantidad: "))
                self.inventario.reservar_objeto(nombre, cantidad)
            elif opcion == "3":
                nombre = input("Nombre del objeto: ")
                cantidad = int(input("Cantidad: "))
                self.inventario.sacar_objeto(nombre, cantidad)
            elif opcion == "4":
                nombre = input("Nombre del objeto: ")
                cantidad = int(input("Cantidad: "))
                self.inventario.sacar_reserva(nombre, cantidad)
            elif opcion == "5":
                nombre = input("Nombre del objeto: ")
                cantidad = int(input("Cantidad: "))
                self.inventario.cancelar_reserva(nombre, cantidad)
            elif opcion == "6":
                nombre = input("Nombre del objeto: ")
                self.inventario.get_item_quantity(nombre)
            elif opcion == "7":
                self.inventario.ver_inventario()
            elif opcion == "8":
                nombre = input("Nuevo nombre de la base de datos: ")
                self.inventario.cambiar_base_datos(nombre)
            elif opcion == "9":
                self.inventario.get_node_name()
            elif opcion == "10":
                print("Saliendo del cliente.")
                break
            else:
                print("Opción inválida. Inténtalo de nuevo.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Iniciar servidor de inventario.")
    parser.add_argument(
        "--port-tcp",
        required=True,
        help="Puerto TCP --port-tcp"
    )
    args = parser.parse_args()
    PORT_TCP = args.port_tcp

    cliente = AlmacenCliente()
    cliente.menu()
