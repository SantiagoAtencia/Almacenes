from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone, timedelta
import zmq
import json
import os
import argparse
# Configuración de SQLAlchemy
Base = declarative_base()

# Málaga tiene UTC +1 en horario estándar (invierno)
malaga_timezone = timezone(timedelta(hours=1))  # UTC +1

NODE_NAME = "node1"


# O para el horario de verano (UTC +2)
# malaga_timezone = timezone(timedelta(hours=2))  # UTC +2

class Inventario(Base):
    __tablename__ = 'inventario'

    id = Column(Integer, primary_key=True, autoincrement=True)
    objeto = Column(String(70), nullable=False)
    cantidad = Column(Integer, nullable=True, default=0)
    reservados = Column(Integer, nullable=True, default=0)
    '''CheckConstraint(
        'cantidad IS NOT NULL OR reservados IS NOT NULL',
        name='check_atributos_no_nulos'
    )'''


class Movimientos(Base):
    __tablename__ = 'movimientos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    objeto = Column(String(70), ForeignKey('inventario.id'), nullable=False)
    tipo = Column(String(50), nullable=False)  # "entrada", "salida", "reserva", "cancelacion reserva", "sacar reserva" 
    cantidad = Column(Integer, nullable=True, default=0)
    reservados = Column(Integer, nullable=True, default=0)
    fecha = Column(DateTime, default=datetime.now(malaga_timezone), nullable=False)
    '''CheckConstraint(
        'cantidad IS NOT NULL OR reservados IS NOT NULL',
        name='check_atributos_no_nulos'
    )'''
    # Relación opcional para acceder al objeto Inventario asociado
    inventario = relationship('Inventario', backref='movimientos')


#engine = create_engine(f'sqlite:///almacen.db')


# Función para cambiar la base de datos y crear Session
def cambiar_base_datos(nueva_bd):
    global engine, Session
    engine = create_engine(f'sqlite:///{nueva_bd}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    print(f"Base de datos cambiada a {nueva_bd}")


# Inicializar la sesión con la base de datos por defecto
#cambiar_base_datos("almacen.db")


def manejar_mensaje(mensaje_json):
    session = Session()
    try:
        mensaje = json.loads(mensaje_json)  # Decodificar mensaje JSON
        accion = mensaje.get("accion")

        if not accion:
            return json.dumps({"status": "error", "message": "Acción no especificada"})

        if accion == "annadir":
            nombre = mensaje.get("nombre")
            cantidad = int(mensaje.get("cantidad"))
            if not nombre or cantidad is None:
                return json.dumps({"status": "error", "message": "Faltan datos: nombre o cantidad"})

            item = session.query(Inventario).filter_by(objeto=nombre).first()
            if item:
                item.cantidad += cantidad
            else:
                item = Inventario(objeto=nombre, cantidad=cantidad)
                session.add(item)

            # Registrar movimiento
            movimiento = Movimientos(
                objeto=nombre,
                tipo="entrada",
                cantidad=cantidad,
                reservados=item.reservados,
                fecha=datetime.now(malaga_timezone)
            )
            session.add(movimiento)
            session.commit()
            return json.dumps(
                {"status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados,
                 "mensaje": f"Objeto {nombre} annadido con cantidad {cantidad}"})

        elif accion == "sacar":
            nombre = mensaje.get("nombre")
            cantidad = int(mensaje.get("cantidad"))
            if not nombre or cantidad is None:
                return json.dumps({"status": "error", "message": "Faltan datos: nombre o cantidad"})

            item = session.query(Inventario).filter_by(objeto=nombre).first()

            if not item:
                return json.dumps({"status": "error", "message": f"Objeto {nombre} no encontrado en el inventario"})

            if item.cantidad < cantidad:
                return json.dumps({"status": "error", "message": f"Cantidad insuficiente de {nombre} en el inventario"})

            movimiento = Movimientos(
                objeto=nombre,
                tipo="salida",
                cantidad=cantidad,
                reservados=item.reservados,
                fecha=datetime.now(malaga_timezone)
            )
            item.cantidad -= cantidad
            '''if item.cantidad == 0 and item.reservados == 0:
                session.delete(item)  # Eliminar el objeto si la cantidad llega a 0'''

            session.add(movimiento)
            session.commit()

            return json.dumps(
                {"status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados,
                 "mensaje": f"Objeto {nombre} sacado con cantidad {cantidad}"})

        if accion == "reservar":
            nombre = mensaje.get("nombre")
            cantidad = int(mensaje.get("cantidad"))
            if not nombre or cantidad is None:
                return json.dumps({"status": "error", "message": "Faltan datos: nombre o cantidad"})

            item = session.query(Inventario).filter_by(objeto=nombre).first()

            if not item:
                return json.dumps({"status": "error", "message": f"Objeto {nombre} no encontrado en el inventario"})
            if item.cantidad < cantidad:
                return json.dumps({"status": "error", "message": f"Cantidad insuficiente de {nombre} para reservar"})

            item.cantidad -= cantidad
            item.reservados += cantidad

            movimiento = Movimientos(
                objeto=nombre,
                tipo="reserva",
                cantidad=item.cantidad,
                reservados=item.reservados,
                fecha=datetime.now(malaga_timezone)
            )
            session.add(movimiento)
            session.commit()

            return json.dumps(
                {"status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados,
                 "mensaje": f"Objeto {nombre} reservado con cantidad {cantidad}"})

        elif accion == "cancelar_reserva":
            nombre = mensaje.get("nombre")
            cantidad = int(mensaje.get("cantidad"))
            if not nombre or cantidad is None:
                return json.dumps({"status": "error", "message": "Faltan datos: nombre o cantidad"})

            item = session.query(Inventario).filter_by(objeto=nombre).first()

            if not item:
                return json.dumps({"status": "error", "message": f"Objeto {nombre} no encontrado en el inventario"})
            if item.reservados < cantidad:
                return json.dumps(
                    {"status": "error", "message": f"Cantidad insuficiente de {nombre} reservada para cancelar"})

            item.cantidad += cantidad
            item.reservados -= cantidad

            movimiento = Movimientos(
                objeto=nombre,
                tipo="cancelacion reserva",
                cantidad=item.cantidad,
                reservados=item.reservados,
                fecha=datetime.now(malaga_timezone)
            )
            session.add(movimiento)
            session.commit()

            return json.dumps(
                {"status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados,
                 "mensaje": f"Objeto {nombre} reserva cancelada con cantidad {cantidad}"})

        elif accion == "sacar_reserva":
            nombre = mensaje.get("nombre")
            cantidad = int(mensaje.get("cantidad"))
            if not nombre or cantidad is None:
                return json.dumps({"status": "error", "message": "Faltan datos: nombre o cantidad"})

            item = session.query(Inventario).filter_by(objeto=nombre).first()

            if not item:
                return json.dumps({"status": "error", "message": f"Objeto {nombre} no encontrado en el inventario"})
            if item.reservados < cantidad:
                return json.dumps(
                    {"status": "error", "message": f"Cantidad insuficiente de {nombre} reservada para retirar"})

            item.reservados -= cantidad

            movimiento = Movimientos(
                objeto=nombre,
                tipo="sacar reserva",
                cantidad=item.cantidad,
                reservados=item.reservados,
                fecha=datetime.now(malaga_timezone)
            )
            session.add(movimiento)
            session.commit()

            return json.dumps(
                {"status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados,
                 "mensaje": f"Objeto {nombre} reserva sacada con cantidad {cantidad}"})
        elif accion == "ver":
            contenido = session.query(Inventario).all()
            resultado = [
                {"nombre": item.objeto, "cantidad": item.cantidad, "reservados": item.reservados}
                for item in contenido
            ]
            print(resultado)
            return json.dumps({"status": "success", "inventario": resultado})

        elif accion == "get_item_quantity":
            nombre = mensaje.get("nombre")
            if nombre is None:
                return json.dumps({"status": "error", "message": "Falta nombre"})

            item = session.query(Inventario).filter_by(objeto=nombre).first()

            if not item:
                return json.dumps({"status": "error", "message": f"Objeto {nombre} no encontrado en el inventario"})

            return json.dumps({"status": "success", "nombre": nombre, "cantidad": item.cantidad})

        elif accion == "get_node_name":
            return json.dumps({"status": "success", "node_name": NODE_NAME})

        elif accion == "remove_db":
            nombre = mensaje.get("nombre")
            if not nombre:
                return json.dumps({"status": "error", "message": "Falta nombre"})
            cambiar_base_datos(f"{nombre}.db")
            return json.dumps(
                {"status": "success", "nombre": nombre, "mensaje": f"Nueva base de datos {nombre}"})

        else:
            return json.dumps({"status": "error", "message": "Acción no reconocida"})

    except Exception as e:
        session.rollback()
        return json.dumps({"status": "error", "message": f"Error al manejar el mensaje: {e}"})

    finally:
        session.close()


def servidor(socket_path):
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # REP para recibir peticiones y enviar respuestas
    socket.bind(f"ipc://{socket_path}")  # Enlazar al socket Unix

    print(f"Servidor iniciado y escuchando en {socket_path}")

    while True:
        try:
            mensaje = socket.recv_string()  # Recibir mensaje como string
            print(f"Mensaje recibido: {mensaje}")

            respuesta = manejar_mensaje(mensaje)  # Manejar el mensaje

            socket.send_string(respuesta)  # Enviar respuesta

        except Exception as e:
            print(f"Error al procesar el mensaje: {e}")


if __name__ == "__main__":
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Iniciar servidor de inventario.")
    parser.add_argument(
        "directorio",
        help="Directorio donde se almacenará la base de datos y el socket Unix"
    )
    args = parser.parse_args()

    # Crear el directorio si no existe
    os.makedirs(args.directorio, exist_ok=True)

    # Configurar la base de datos
    db_path = os.path.join(args.directorio, "almacen.db")
    cambiar_base_datos(db_path)

    # Configurar el socket Unix
    socket_path = "/tmp/almacen.sock"
    servidor(socket_path)

