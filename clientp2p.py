# cliente_p2p.py

import requests
import tkinter as tk
from tkinter import messagebox
import threading
import time

class ClienteP2P:
    def __init__(self, nodo_url):
        self.nodo_url = nodo_url
        self.nodos_descubiertos = set([nodo_url])  # Almacena nodos descubiertos
        self.ventana = tk.Tk()
        self.ventana.title("Cliente P2P - Gestión de Inventario")
        self.crear_interfaz()
        self.shutdown_flag = False  # Flag to stop threads gracefully
        threading.Thread(target=self.descubrir_nodos_periodicamente, daemon=True).start()

    def crear_interfaz(self):
        tk.Label(self.ventana, text="Nombre del objeto:").pack(pady=5)
        self.entrada_nombre = tk.Entry(self.ventana, width=50)
        self.entrada_nombre.pack(pady=5)

        tk.Label(self.ventana, text="Cantidad:").pack(pady=5)
        self.entrada_cantidad = tk.Entry(self.ventana, width=50)
        self.entrada_cantidad.pack(pady=5)

        tk.Button(self.ventana, text="Añadir objeto", command=self.annadir_objeto).pack(pady=5)
        tk.Button(self.ventana, text="Sacar objeto", command=self.sacar_objeto).pack(pady=5)
        tk.Button(self.ventana, text="Ver inventario", command=self.ver_inventario).pack(pady=5)
        tk.Button(self.ventana, text="Sincronizar manualmente", command=self.sincronizar_manual).pack(pady=5)
        tk.Button(self.ventana, text="Salir", command=self.salir).pack(pady=5)

        self.ventana.mainloop()

    def enviar_peticion(self, endpoint, metodo="GET", datos=None, nodo=None):
        url = f"{nodo or self.nodo_url}/{endpoint}"
        try:
            if metodo == "POST":
                respuesta = requests.post(url, json=datos)
            else:
                respuesta = requests.get(url)

            if respuesta.status_code == 200:
                return respuesta.json()
            else:
                return {"error": respuesta.json().get("error", "Error desconocido")}
        except requests.RequestException as e:
            return {"error": str(e)}

    def annadir_objeto(self):
        nombre = self.entrada_nombre.get()
        cantidad = self.entrada_cantidad.get()

        if not nombre or not cantidad.isdigit():
            messagebox.showwarning("Advertencia", "Debes introducir un nombre y una cantidad válida.")
            return

        datos = {"nombre": nombre, "cantidad": int(cantidad)}
        respuesta = self.enviar_peticion("inventario/annadir", metodo="POST", datos=datos)

        if "error" in respuesta:
            messagebox.showerror("Error", respuesta["error"])
        else:
            messagebox.showinfo("Éxito", respuesta["mensaje"])

    def sacar_objeto(self):
        nombre = self.entrada_nombre.get()
        cantidad = self.entrada_cantidad.get()

        if not nombre or not cantidad.isdigit():
            messagebox.showwarning("Advertencia", "Debes introducir un nombre y una cantidad válida.")
            return

        datos = {"nombre": nombre, "cantidad": int(cantidad)}
        respuesta = self.enviar_peticion("inventario/sacar", metodo="POST", datos=datos)

        if "error" in respuesta:
            messagebox.showerror("Error", respuesta["error"])
        else:
            messagebox.showinfo("Éxito", respuesta["mensaje"])

    def ver_inventario(self):
        respuesta = self.enviar_peticion("inventario/ver")

        if "error" in respuesta:
            messagebox.showerror("Error", respuesta["error"])
        else:
            contenido = respuesta
            resultado = "Contenido del inventario:\n"
            for item in contenido:
                resultado += f"- {item['objeto']}: {item['cantidad']}\n"
            messagebox.showinfo("Inventario", resultado)

    def sincronizar_manual(self):
        """Sincroniza manualmente el inventario con todos los nodos descubiertos."""
        for nodo in self.nodos_descubiertos:
            if nodo != self.nodo_url:  # Evita sincronizar consigo mismo
                respuesta = self.enviar_peticion("inventario/ver", nodo=nodo)
                if "error" in respuesta:
                    print(f"Error al sincronizar con {nodo}: {respuesta['error']}")
                else:
                    self.sincronizar_inventario_local(respuesta)
        messagebox.showinfo("Sincronización", "Sincronización manual completada.")

    def sincronizar_inventario_local(self, inventario_remoto):
        """Actualiza el inventario local según el inventario remoto recibido."""
        session_inventario = {item['objeto']: item['cantidad'] for item in inventario_remoto}
        respuesta_local = self.enviar_peticion("inventario/ver")
        if "error" not in respuesta_local:
            for item in respuesta_local:
                nombre = item['objeto']
                cantidad = item['cantidad']
                if nombre in session_inventario:
                    session_inventario[nombre] = max(session_inventario[nombre], cantidad)
        for nombre, cantidad in session_inventario.items():
            self.enviar_peticion("inventario/annadir", metodo="POST", datos={"nombre": nombre, "cantidad": cantidad})

    def descubrir_nodos_periodicamente(self):
        """Descubre nodos vecinos periódicamente cada 30 segundos."""
        while not self.shutdown_flag:
            for nodo in list(self.nodos_descubiertos):
                try:
                    respuesta = self.enviar_peticion("nodos", nodo=nodo)
                    if "error" not in respuesta:
                        nuevos_nodos = respuesta.get("nodos", [])
                        self.nodos_descubiertos.update(nuevos_nodos)
                except Exception as e:
                    print(f"Error al descubrir nodos desde {nodo}: {e}")
            time.sleep(30)

    def salir(self):
        """Gracefully exit and stop threads."""
        self.shutdown_flag = True  # Set the shutdown flag to stop threads
        self.ventana.quit()  # Close the Tkinter window
        self.ventana.destroy()  # Properly clean up the Tkinter window

if __name__ == "__main__":
    nodo_url = input("Ingrese la URL del nodo (ej. http://localhost:5000): ")
    ClienteP2P(nodo_url)
