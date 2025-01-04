# servidor_p2p.py

from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime, timezone, timedelta
import requests
import threading
import zmq

# Configuración de Flask y SQLAlchemy
app = Flask(__name__)

Base = declarative_base()
nombre_base_datos = input("Ingrese el nombre de la base de datos (por ejemplo, inventario.db): ")
engine = create_engine(f'sqlite:///{nombre_base_datos}.db')
Session = sessionmaker(bind=engine)

# Configuración de ZeroMQ
puerto_zmq = int(input("Ingrese el puerto zmq: "))

context = zmq.Context()
socket_pub = context.socket(zmq.PUB)
# puerto_zmq = 5556  # Puerto para ZeroMQ PUB
socket_pub.bind(f"tcp://*:{puerto_zmq}")

# Málaga tiene UTC +1 en horario estándar (invierno)
malaga_timezone = timezone(timedelta(hours=1))  # UTC +1


# O para el horario de verano (UTC +2)
# malaga_timezone = timezone(timedelta(hours=2))  # UTC +2


class Inventario(Base):
    __tablename__ = 'inventario'

    id = Column(Integer, primary_key=True, autoincrement=True)
    objeto = Column(String(70), nullable=False)
    cantidad = Column(Integer, nullable=True, default=0)
    reservados = Column(Integer, nullable=True, default=0)
    CheckConstraint(
        'cantidad IS NOT NULL OR reservados IS NOT NULL',
        name='check_atributos_no_nulos'
    )


class Movimientos(Base):
    __tablename__ = 'movimientos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    objeto = Column(String(70), ForeignKey('inventario.objeto'), nullable=False)
    tipo = Column(String(50), nullable=False)  # "entrada", "salida", "reserva", "cancelacion reserva", "sacar reserva"
    cantidad = Column(Integer, nullable=True, default=0)
    reservados = Column(Integer, nullable=True, default=0)
    fecha = Column(DateTime, default=datetime.now(malaga_timezone), nullable=False)
    CheckConstraint(
        'cantidad IS NOT NULL OR reservados IS NOT NULL',
        name='check_atributos_no_nulos'
    )

    # Relación opcional para acceder al objeto Inventario asociado
    inventario = relationship('Inventario', backref='movimientos')


Base.metadata.create_all(engine)

# Lista de nodos vecinos (puede ser cargada dinámicamente)
nodos_vecinos = [
    "http://localhost:5000",
    "http://localhost:5001",
    "http://localhost:5002"
]


@app.route('/inventario/annadir', methods=['POST'])
def annadir_objeto():
    """Añadir un objeto al inventario local."""
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')

    session = Session()
    try:
        item = session.query(Inventario).filter_by(objeto=nombre).first()
        if item:
            item.cantidad += cantidad
        else:
            item = Inventario(objeto=nombre, cantidad=cantidad)
            session.add(item)

        session.commit()
        # Registrar movimiento
        movimiento = Movimientos(
            objeto=item.objeto,
            tipo="entrada",
            cantidad=cantidad,
            fecha=datetime.now(timezone.utc)
        )
        session.add(movimiento)
        session.commit()

        notificar_vecinos()  # Notificar a los nodos vecinos
        enviar_evento_zmq("annadir", nombre, cantidad)  # Enviar evento por ZeroMQ
        return jsonify({"mensaje": f"Objeto {nombre} añadido con cantidad {cantidad}"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route('/inventario/sacar', methods=['POST'])
def sacar_objeto():
    """Sacar un objeto del inventario local."""
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')

    session = Session()
    try:
        item = session.query(Inventario).filter_by(objeto=nombre).first()
        if not item or item.cantidad < cantidad:
            return jsonify({"error": f"Cantidad insuficiente de {nombre}"}), 400

        movimiento = Movimientos(
            objeto=item.objeto,
            tipo="salida",
            cantidad=cantidad,
            fecha=datetime.now(timezone.utc)
        )

        item.cantidad -= cantidad
        if item.cantidad == 0:
            session.delete(item)

        # Registrar movimiento
        session.add(movimiento)
        session.commit()

        notificar_vecinos()  # Notificar a los nodos vecinos
        enviar_evento_zmq("sacar", nombre, cantidad)  # Enviar evento por ZeroMQ
        return jsonify({"mensaje": f"Objeto {nombre} retirado con cantidad {cantidad}"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/inventario/reservar', methods=['POST'])
def reservar():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')

    session = Session()
    try:
        # Verificar si el objeto ya existe en el inventario
        item = session.query(Inventario).filter_by(objeto=nombre).first()
        if not item:
            return f"Error: Objeto {nombre} no encontrado en el inventario"
        if item.cantidad < cantidad:
            return f"Error: Cantidad insuficiente de {nombre} en el inventario"

        item.cantidad -= cantidad
        item.reservados += cantidad

        # Registrar movimiento
        movimiento = Movimientos(
            objeto=nombre,
            tipo="reserva",
            cantidad=item.cantidad,
            reservados=cantidad,
            fecha=datetime.now(malaga_timezone)
        )
        session.add(movimiento)
        session.commit()

        notificar_vecinos()  # Notificar a los nodos vecinos
        enviar_evento_zmq("reservar", nombre, cantidad)  # Enviar evento por ZeroMQ
        return jsonify({"mensaje": f"Objeto {nombre} reservado con cantidad {cantidad}"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()



@app.route('/inventario/sacar_reserva', methods=['POST'])
def sacar_reserva():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')

    session = Session()
    try:
        # Verificar si el objeto ya existe en el inventario
        item = session.query(Inventario).filter_by(objeto=nombre).first()

        if not item:
            return f"Error: Objeto {nombre} no encontrado en el inventario"
        if item.reservados < cantidad:
            return f"Error: Cantidad insuficiente de {nombre} en el inventario"
        movimiento = Movimientos(
            objeto=nombre,
            tipo="entrega de la reserva",
            cantidad=item.cantidad,
            reservados=cantidad,
            fecha=datetime.now(malaga_timezone)
        )
        item.reservados -= cantidad
        if item.cantidad == 0 and item.reservados == 0:
            session.delete(item)  # Eliminar el objeto si la cantidad llega a 0

        # Registrar movimiento

        session.add(movimiento)
        session.commit()

        notificar_vecinos()  # Notificar a los nodos vecinos
        enviar_evento_zmq("sacar_reserva", nombre, cantidad)  # Enviar evento por ZeroMQ
        return jsonify({"mensaje": f"Objeto {nombre} reserva sacada con cantidad {cantidad}"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route('/inventario/cancelar_reserva', methods=['POST'])
def cancelar_reserva():
    datos = request.json
    nombre = datos.get('nombre')
    cantidad = datos.get('cantidad')

    session = Session()
    try:
        # Verificar si el objeto ya existe en el inventario
        item = session.query(Inventario).filter_by(objeto=nombre).first()

        if not item:
            return f"Error: Objeto {nombre} no encontrado en el inventario"
        if item.reservados < cantidad:
            return f"Error: Cantidad insuficiente de {nombre} en el inventario"
        movimiento = Movimientos(
            objeto=nombre,
            tipo="cancelacion de la reserva",
            cantidad=item.cantidad,
            reservados=item.reservados,
            fecha=datetime.now(malaga_timezone)
        )
        item.reservados -= cantidad
        item.cantidad += cantidad

        # Registrar movimiento

        session.add(movimiento)
        session.commit()

        notificar_vecinos()  # Notificar a los nodos vecinos
        enviar_evento_zmq("cancelar_reserva", nombre, cantidad)  # Enviar evento por ZeroMQ
        return jsonify({"mensaje": f"Objeto {nombre} reserva cancelada con cantidad {cantidad}"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/inventario/ver', methods=['GET'])
def ver_inventario():
    """Ver el inventario local."""
    session = Session()
    try:
        contenido = session.query(Inventario).all()
        resultado = [{"objeto": item.objeto, "cantidad": item.cantidad} for item in contenido]
        return jsonify(resultado), 200
    finally:
        session.close()


@app.route('/sincronizar', methods=['POST'])
def sincronizar():
    """Sincronizar el inventario con otro nodo."""
    datos = request.json
    inventario_recibido = datos.get('inventario', [])

    session = Session()
    try:
        for item in inventario_recibido:
            nombre = item['objeto']
            cantidad = item['cantidad']

            item_local = session.query(Inventario).filter_by(objeto=nombre).first()
            if item_local:
                item_local.cantidad = cantidad  # Sincronización simple
            else:
                nuevo_item = Inventario(objeto=nombre, cantidad=cantidad)
                session.add(nuevo_item)

        session.commit()
        return jsonify({"mensaje": "Sincronización completada"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def notificar_vecinos():
    """Notificar a los nodos vecinos para que se sincronicen."""
    session = Session()
    inventario = session.query(Inventario).all()
    inventario_data = [{"objeto": item.objeto, "cantidad": item.cantidad} for item in inventario]

    for nodo in nodos_vecinos:
        try:
            requests.post(f"{nodo}/sincronizar", json={"inventario": inventario_data})
        except requests.RequestException as e:
            print(f"Error al notificar al nodo {nodo}: {e}")
    session.close()


def enviar_evento_zmq(accion, nombre, cantidad):
    """Enviar un evento mediante ZeroMQ."""
    mensaje = f"{accion}:{nombre}:{cantidad}"
    socket_pub.send_string(mensaje)


if __name__ == '__main__':
    # Ejecutar el servidor Flask en un hilo separado
    puerto = int(input("Ingrese el puerto para este nodo: "))
    threading.Thread(target=app.run(port=puerto)).start()

    # ZeroMQ SUB para recibir eventos de otros nodos
    socket_sub = context.socket(zmq.SUB)
    socket_sub.connect(f"tcp://localhost:{puerto_zmq}")
    socket_sub.setsockopt_string(zmq.SUBSCRIBE, "")


    def recibir_eventos_zmq():
        """Recibir y procesar eventos de ZeroMQ."""
        while True:
            mensaje = socket_sub.recv_string()
            accion, nombre, cantidad = mensaje.split(":")
            cantidad = int(cantidad)
            print(f"Evento recibido: {accion} {nombre} {cantidad}")
            if accion == "annadir":
                annadir_objeto_local(nombre, cantidad)
            elif accion == "sacar":
                sacar_objeto_local(nombre, cantidad)
            elif accion == "reservar":
                reservar_objeto_local(nombre, cantidad)
            elif accion == "sacar_reserva":
                sacar_reserva_objeto_local(nombre, cantidad)
            elif accion == "cancelar_reserva":
                cancelar_reserva_objeto_local(nombre, cantidad)


    def annadir_objeto_local(nombre, cantidad):
        """Añadir objeto localmente sin notificar vecinos."""
        session = Session()
        try:
            item = session.query(Inventario).filter_by(objeto=nombre).first()
            if item:
                item.cantidad += cantidad
            else:
                item = Inventario(objeto=nombre, cantidad=cantidad)
                session.add(item)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error al añadir objeto localmente: {e}")
        finally:
            session.close()


    def sacar_objeto_local(nombre, cantidad):
        """Sacar objeto localmente sin notificar vecinos."""
        session = Session()
        try:
            item = session.query(Inventario).filter_by(objeto=nombre).first()
            if item and item.cantidad >= cantidad:
                item.cantidad -= cantidad
                if item.cantidad == 0:
                    session.delete(item)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error al sacar objeto localmente: {e}")
        finally:
            session.close()

    def reservar_objeto_local(nombre, cantidad):
        session = Session()
        try:
            item = session.query(Inventario).filter_by(objeto=nombre).first()
            if item and item.cantidad >= cantidad:
                item.cantidad -= cantidad
                item.reservados += cantidad
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error al reservar objeto localmente: {e}")
        finally:
            session.close()

    def sacar_reserva_objeto_local(nombre, cantidad):
        session = Session()
        try:
            item = session.query(Inventario).filter_by(objeto=nombre).first()
            if item and item.reservados >= cantidad:
                item.reservados -= cantidad
                if item.reservados == 0 and item.cantidad == 0:
                    session.delete(item)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error al reservar objeto localmente: {e}")
        finally:
            session.close()

    def cancelar_reserva_objeto_local(nombre, cantidad):
        session = Session()
        try:
            item = session.query(Inventario).filter_by(objeto=nombre).first()
            if item and item.reservados >= cantidad:
                item.reservados -= cantidad
                item.cantidad += cantidad
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error al reservar objeto localmente: {e}")
        finally:
            session.close()

    # Iniciar el hilo para recibir eventos de ZeroMQ
    threading.Thread(target=recibir_eventos_zmq, daemon=True).start()
