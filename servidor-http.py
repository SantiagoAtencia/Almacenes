import zmq
import zmq.error
from flask import Flask, request, jsonify

app = Flask(__name__)

def enviar_mensaje(mensaje):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  # REQ para enviar peticiones
    socket.connect("tcp://localhost:5555")  # Conecta al servidor en el puerto 5555

    # Establecer un timeout de 5 segundos para las respuestas
    socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5000 ms = 5 segundos
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

@app.route('/inventario/annadir', methods=['POST'])
def annadir_objeto():
    #por definir
        datos = request.json
        nombre = datos.get('nombre')
        cantidad = datos.get('cantidad')
        mensaje = f"añadir:{nombre}:{cantidad}"
        respuesta = enviar_mensaje(mensaje)
        return "Objeto añadido correctamente"


@app.route('/inventario/sacar', methods=['POST'])
def sacar_objeto():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')
    mensaje = f"sacar:{nombre}:{cantidad}"
    respuesta = enviar_mensaje(mensaje)
    return "Objeto extraido correctamente"

@app.route('/inventario/reservar', methods=['POST'])
def reservar():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')
    mensaje = f"reservar:{nombre}:{cantidad}"
    respuesta = enviar_mensaje(mensaje)
    return "Objeto extraido correctamente"


@app.route('/inventario/sacar_reserva', methods=['POST'])
def sacar_reserva():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')
    mensaje = f"sacar reserva:{nombre}:{cantidad}"
    respuesta = enviar_mensaje(mensaje)
    return "Objeto reservado extraido correctamente"



@app.route('/inventario/cancelar_reserva', methods=['POST'])
def cancelar_reserva():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')
    mensaje = f"cancelar reserva:{nombre}:{cantidad}"
    respuesta = enviar_mensaje(mensaje)
    return "Reserva cancelada correctamente"

@app.route('/inventario/ver', methods=['GET'])
def ver_inventario():
    mensaje = "ver"
    respuesta = enviar_mensaje(mensaje)
    return "inventario ispeccionado con exito"
if __name__ == "__main__":
    puerto = int(input("Introduce un puerto para el nodo: "))
    app.run(port=puerto)