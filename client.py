# Cliente con ZeroMQ con interfaz gráfica para gestionar un almacén
import zmq
import zmq.error

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("Error: La biblioteca 'tkinter' no está instalada. Por favor, instálala antes de continuar.")
    exit(1)


def cliente():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  # REQ para enviar peticiones
    socket.connect("tcp://localhost:5555")  # Conecta al servidor en el puerto 5555

    # Establecer un timeout de 5 segundos para las respuestas
    socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5000 ms = 5 segundos

    def enviar_mensaje(mensaje):
        try:
            print(f"Enviando: {mensaje}")
            socket.send_string(mensaje)

            # Intentar recibir respuesta del servidor
            respuesta = socket.recv_string()
            print(f"Respuesta recibida: {respuesta}")
            return respuesta
        except zmq.error.Again:
            # Manejar el caso de timeout
            print("No se recibió respuesta del servidor (timeout)")
            return "Error: No se recibió respuesta del servidor (timeout)"

    def añadir_objeto():
        nombre = entrada_nombre.get()
        cantidad = entrada_cantidad.get()
        if not nombre or not cantidad.isdigit():
            messagebox.showwarning("Advertencia", "Debes introducir un nombre y una cantidad válida.")
            return
        mensaje = f"añadir:{nombre}:{cantidad}"
        respuesta = enviar_mensaje(mensaje)
        messagebox.showinfo("Respuesta del servidor", respuesta)

    def sacar_objeto():
        nombre = entrada_nombre.get()
        cantidad = entrada_cantidad.get()
        if not nombre or not cantidad.isdigit():
            messagebox.showwarning("Advertencia", "Debes introducir un nombre y una cantidad válida.")
            return
        mensaje = f"sacar:{nombre}:{cantidad}"
        respuesta = enviar_mensaje(mensaje)
        messagebox.showinfo("Respuesta del servidor", respuesta)

    def ver_almacen():
        mensaje = "ver"
        respuesta = enviar_mensaje(mensaje)
        messagebox.showinfo("Contenido del almacén", respuesta)

    def salir():
        ventana.quit()
        ventana.destroy()

    # Configuración de la interfaz gráfica
    ventana = tk.Tk()
    ventana.title("Cliente ZeroMQ - Gestión de Almacén")

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

    boton_ver = tk.Button(ventana, text="Ver almacén", command=ver_almacen)
    boton_ver.pack(pady=5)

    boton_salir = tk.Button(ventana, text="Salir", command=salir)
    boton_salir.pack(pady=5)

    ventana.mainloop()


if __name__ == "__main__":
    cliente()
