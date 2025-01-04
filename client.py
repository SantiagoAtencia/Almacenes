# Cliente con ZeroMQ con interfaz gráfica para gestionar un almacén
import requests
try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("Error: La biblioteca 'tkinter' no está instalada. Por favor, instálala antes de continuar.")
    exit(1)

BASE_URL = "http://localhost:5000"

def cliente():

    def enviar_peticion(endpoint, metodo="GET", datos = None):
        try:
            url = f"{BASE_URL}/{endpoint}"

            if metodo == "GET":
                respuesta = requests.get(url, timeout=5)
            elif metodo == "POST":
                respuesta = requests.post(url, json=datos, timeout=5)
            else:
                raise ValueError("Método HTTP no soportado")

            return respuesta.json()
        except requests.exceptions.Timeout:
            return "Error: No se recibió respuesta del servidor (timeout)"
        except requests.exceptions.RequestException as e:
            return f"Error de conexión: {e}"

    def añadir_objeto():
        nombre = entrada_nombre.get()
        cantidad = entrada_cantidad.get()
        if not nombre or not cantidad.isdigit():
            messagebox.showwarning("Advertencia", "Debes introducir un nombre y una cantidad válida.")
            return
        datos = {"nombre": nombre, "cantidad": int(cantidad)}
        respuesta = enviar_peticion("/inventario/annadir", "POST", datos)
        messagebox.showinfo("Respuesta del servidor", respuesta["mensaje"])

    def reservar_objeto():
        nombre = entrada_nombre.get()
        cantidad = entrada_cantidad.get()
        if not nombre or not cantidad.isdigit():
            messagebox.showwarning("Advertencia", "Debes introducir un nombre y una cantidad válida.")
            return
        datos = {"nombre": nombre, "cantidad": int(cantidad)}
        respuesta = enviar_peticion("/inventario/reservar", "POST", datos)
        messagebox.showinfo("Respuesta del servidor", respuesta["mensaje"])
    
    def sacar_objeto():
        nombre = entrada_nombre.get()
        cantidad = entrada_cantidad.get()
        if not nombre or not cantidad.isdigit():
            messagebox.showwarning("Advertencia", "Debes introducir un nombre y una cantidad válida.")
            return
        datos = {"nombre": nombre, "cantidad": int(cantidad)}
        respuesta = enviar_peticion("/inventario/sacar", "POST", datos)
        messagebox.showinfo("Respuesta del servidor", respuesta["mensaje"])

    def sacar_reserva():
        nombre = entrada_nombre.get()
        cantidad = entrada_cantidad.get()
        if not nombre or not cantidad.isdigit():
            messagebox.showwarning("Advertencia", "Debes introducir un nombre y una cantidad válida.")
            return
        datos = {"nombre": nombre, "cantidad": int(cantidad)}
        respuesta = enviar_peticion("/inventario/sacar_reserva", "POST", datos)
        messagebox.showinfo("Respuesta del servidor", respuesta["mensaje"])

    def cancelar_reserva():
        nombre = entrada_nombre.get()
        cantidad = entrada_cantidad.get()
        if not nombre or not cantidad.isdigit():
            messagebox.showwarning("Advertencia", "Debes introducir un nombre y una cantidad válida.")
            return
        datos = {"nombre": nombre, "cantidad": int(cantidad)}
        respuesta = enviar_peticion("/inventario/cancelar_reserva", "POST", datos)
        messagebox.showinfo("Respuesta del servidor", respuesta["mensaje"])

    def ver_almacen():
        respuesta = enviar_peticion("/inventario/ver", "GET")
        contenido = "Contenido del inventario:\n"
        for item in respuesta:
            contenido += f"- {item['objeto']}: {item['cantidad']}\n"
        messagebox.showinfo("Contenido del almacén", contenido)

    def salir():
        ventana.quit()
        ventana.destroy()

    # Configuración de la interfaz gráfica
    ventana = tk.Tk()
    ventana.title("Cliente API REST - Gestión de Almacén")

    tk.Label(ventana, text="Nombre del objeto:").pack(pady=5)
    entrada_nombre = tk.Entry(ventana, width=50)
    entrada_nombre.pack(pady=5)

    tk.Label(ventana, text="Cantidad:").pack(pady=5)
    entrada_cantidad = tk.Entry(ventana, width=50)
    entrada_cantidad.pack(pady=5)

    boton_añadir = tk.Button(ventana, text="Añadir objeto", command=añadir_objeto)
    boton_añadir.pack(pady=5)

    boton_sacar = tk.Button(ventana, text="Sacar objeto", command=sacar_objeto)
    boton_sacar.pack(pady=5)

    boton_reservar = tk.Button(ventana, text="Reservar objeto", command=reservar_objeto)
    boton_reservar.pack(pady=5) 


    boton_sacar = tk.Button(ventana, text="Sacar reserva", command=sacar_reserva)
    boton_sacar.pack(pady=5)

    boton_reservar = tk.Button(ventana, text="Cancelar reservar objeto", command=cancelar_reserva)
    boton_reservar.pack(pady=5) 


    boton_ver = tk.Button(ventana, text="Ver almacén", command=ver_almacen)
    boton_ver.pack(pady=5)

    boton_salir = tk.Button(ventana, text="Salir", command=salir)
    boton_salir.pack(pady=5)

    ventana.mainloop()

if __name__ == "__main__":
    cliente()
