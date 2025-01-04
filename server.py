from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone, timedelta
import zmq

# Configuración de SQLAlchemy
Base = declarative_base()

# Málaga tiene UTC +1 en horario estándar (invierno)
malaga_timezone = timezone(timedelta(hours=1))  # UTC +1


# O para el horario de verano (UTC +2)
# malaga_timezone = timezone(timedelta(hours=2))  # UTC +2

class Inventario(Base):
    __tablename__ = 'inventario'

    id = Column(Integer, primary_key=True, autoincrement=True)
    objeto = Column(String(70), nullable=False)
    cantidad = Column(Integer,nullable=True, default=0)
    reservados = Column(Integer,nullable=True, default=0)
    CheckConstraint(
        'cantidad IS NOT NULL OR reservados IS NOT NULL',
        name='check_atributos_no_nulos'
    )


class Movimientos(Base):
    __tablename__ = 'movimientos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    objeto = Column(String(70), ForeignKey('inventario.id'), nullable=False)
    tipo = Column(String(50), nullable=False)  # "entrada", "salida", "reserva", "cancelacion reserva", "sacar reserva" 
    cantidad = Column(Integer, nullable=True,default=0)
    reservados = Column(Integer,nullable=True,default=0)
    fecha = Column(DateTime, default=datetime.now(malaga_timezone), nullable=False)
    CheckConstraint(
        'cantidad IS NOT NULL OR reservados IS NOT NULL',
        name='check_atributos_no_nulos'
    )
    # Relación opcional para acceder al objeto Inventario asociado
    inventario = relationship('Inventario', backref='movimientos')


# Crear conexión con la base de datos
engine = create_engine('sqlite:///almacen.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def manejar_mensaje(mensaje):
    session = Session()
    try:
        comandos = mensaje.split(":")
        accion = comandos[0]
        #### AÑADIR####
        if accion == "añadir":
            nombre = comandos[1]
            cantidad = int(comandos[2])

            # Verificar si el objeto ya existe en el inventario
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

            return f"Objeto {nombre} añadido con cantidad {cantidad}"
        #### SACAR####
        elif accion == "sacar":
            nombre = comandos[1]
            cantidad = int(comandos[2])

            # Verificar si el objeto existe y tiene suficiente cantidad
            item = session.query(Inventario).filter_by(objeto=nombre).first()
            

            if not item:
                return f"Error: Objeto {nombre} no encontrado en el inventario"
            if item.cantidad < cantidad:
                return f"Error: Cantidad insuficiente de {nombre} en el inventario"
            movimiento = Movimientos(
                objeto=nombre,
                tipo="salida",
                cantidad=cantidad,
                reservados= item.reservados,
                fecha=datetime.now(malaga_timezone)
            )
            item.cantidad -= cantidad
            if item.cantidad  == 0 and item.reservados == 0:
                session.delete(item)  # Eliminar el objeto si la cantidad llega a 0

            # Registrar movimiento

            session.add(movimiento)
            session.commit()

            return f"Objeto {nombre} retirado con cantidad {cantidad}"
        #### RESERVAR####
        elif accion == "reservar":
            nombre = comandos[1]
            cantidad = int(comandos[2])

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

            return f"Objeto {nombre} añadido con cantidad {cantidad}"
        #### SACAR RESERVA####
        elif accion == "sacar reserva":
            nombre = comandos[1]
            cantidad = int(comandos[2])

            # Verificar si el objeto existe y tiene suficiente cantidad
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
            if item.cantidad  == 0 and item.reservados == 0:
                session.delete(item)  # Eliminar el objeto si la cantidad llega a 0

            # Registrar movimiento

            session.add(movimiento)
            session.commit()

            return f"Objeto {nombre} retirado con cantidad {cantidad}"
        ####CANCELAR RESERVA####
        elif accion == "cancelar reserva":
            nombre = comandos[1]
            cantidad = int(comandos[2])

            # Verificar si el objeto existe y tiene suficiente cantidad
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

            return f"Objeto {nombre} retirado con cantidad {cantidad}"
        #### CONSULTAR####
        elif accion == "ver":
            # Mostrar el contenido del inventario
            contenido = session.query(Inventario).all()
            resultado = "Contenido del almacén:\n"
            for item in contenido:
                resultado += f"- {item.objeto}: {item.cantidad} reservados: {item.reservados}\n"
            return resultado.strip()
        else:
            return "Acción no reconocida"

    except Exception as e:
        session.rollback()
        return f"Error al manejar el mensaje: {e}"

    finally:
        session.close()


def servidor():
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # REP para recibir peticiones y enviar respuestas
    socket.bind("tcp://*:5555")  # Escuchar en el puerto 5556

    print("Servidor iniciado y esperando mensajes...")

    while True:
        try:
            mensaje = socket.recv_string()  # Recibir mensaje como string
            print(f"Mensaje recibido: {mensaje}")

            respuesta = manejar_mensaje(mensaje)  # Manejar el mensaje

            socket.send_string(respuesta)  # Enviar respuesta

        except Exception as e:
            print(f"Error al procesar el mensaje: {e}")


if __name__ == "__main__":
    servidor()
    