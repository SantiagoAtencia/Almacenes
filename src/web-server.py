import zmq
import zmq.error
import json
import os
import argparse
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder='../templates')


def enviar_mensaje(mensaje_dict):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  # REQ para enviar peticiones
    socket.connect(f"ipc:///tmp/almacen_{NODE_NAME}.sock")  # Conecta al servidor en el puerto 5555

    # Establecer un timeout de 5 segundos para las respuestas
    socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5000 ms = 5 segundos
    try:
        mensaje_json = json.dumps(mensaje_dict, ensure_ascii=False)
        print(f"Enviando: {mensaje_json}")
        socket.send_json(mensaje_dict)

        # Intentar recibir respuesta del servidor
        respuesta_json = socket.recv_json()
        respuesta = respuesta_json.get("mensaje", "No hay mensaje en el JSON")
        print(f"Respuesta recibida: {respuesta}")
        #return json.loads(respuesta)  # Decodificar la respuesta JSON
        return respuesta_json
    except zmq.error.Again:
        # Manejar el caso de timeout
        print("No se recibió respuesta del servidor (timeout)")
        return {"error": "No se recibió respuesta del servidor (timeout)"}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventario/get_node_name', methods=['GET'])
def get_node_name():
    mensaje = {
        "accion": "get_node_name",
    }
    respuesta = enviar_mensaje(mensaje)
    return jsonify(respuesta), 200

@app.route('/inventario/annadir', methods=['POST'])
def annadir_objeto():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')
    mensaje = {
        "accion": "annadir",
        "nombre": nombre,
        "cantidad": cantidad
    }
    respuesta = enviar_mensaje(mensaje)
    return jsonify(respuesta), 200


@app.route('/inventario/sacar', methods=['POST'])
def sacar_objeto():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')
    mensaje = {
        "accion": "sacar",
        "nombre": nombre,
        "cantidad": cantidad
    }
    respuesta = enviar_mensaje(mensaje)
    return jsonify(respuesta), 200


@app.route('/inventario/reservar', methods=['POST'])
def reservar():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')
    mensaje = {
        "accion": "reservar",
        "nombre": nombre,
        "cantidad": cantidad
    }
    respuesta = enviar_mensaje(mensaje)
    return jsonify(respuesta), 200


@app.route('/inventario/sacar_reserva', methods=['POST'])
def sacar_reserva():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')
    mensaje = {
        "accion": "sacar_reserva",
        "nombre": nombre,
        "cantidad": cantidad
    }
    respuesta = enviar_mensaje(mensaje)
    return jsonify(respuesta), 200


@app.route('/inventario/cancelar_reserva', methods=['POST'])
def cancelar_reserva():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')
    mensaje = {
        "accion": "cancelar_reserva",
        "nombre": nombre,
        "cantidad": cantidad
    }
    respuesta = enviar_mensaje(mensaje)
    return jsonify(respuesta), 200

@app.route('/inventario/get_item_quantity', methods=['POST'])
def get_item_quantity():
    datos = request.json
    nombre = datos.get('nombre')

    mensaje = {
        "accion": "get_item_quantity",
        "nombre": nombre
    }
    respuesta = enviar_mensaje(mensaje)
    return jsonify(respuesta), 200


@app.route('/inventario/ver', methods=['GET'])
def ver_inventario():
    mensaje = {
        "accion": "ver"
    }
    respuesta = enviar_mensaje(mensaje)
    return jsonify(respuesta), 200


@app.route('/inventario/remove_db', methods=['POST'])
def remove_db():
    datos = request.json
    nombre = datos.get('nombre')

    mensaje = {
        "accion": "remove_db",
        "nombre": nombre
    }
    respuesta = enviar_mensaje(mensaje)
    return jsonify(respuesta), 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Iniciar servidor de inventario.")
    parser.add_argument(
        "--node-name",
        required=True,
        help="Nombre del nodo (NODE_NAME)"
    )
    args = parser.parse_args()
    NODE_NAME = args.node_name
    puerto = int(input("Introduce un puerto para el nodo: "))
    app.run(port=puerto)
