import zmq
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de SQLAlchemy
Base = declarative_base()

class Inventario(Base):
    __tablename__ = 'inventario'

    id = Column(Integer, primary_key=True, autoincrement=True)
    objeto = Column(String(70), nullable=False)
    cantidad = Column(Integer, nullable=False)

# Crear conexión con la base de datos
engine = create_engine('sqlite:///almacen.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def manejar_mensaje(mensaje):
    session = Session()
    try:
        comandos = mensaje.split(":")
        accion = comandos[0]

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
            session.commit()

            return f"Objeto {nombre} añadido con cantidad {cantidad}"

        elif accion == "sacar":
            nombre = comandos[1]
            cantidad = int(comandos[2])

            # Verificar si el objeto existe y tiene suficiente cantidad
            item = session.query(Inventario).filter_by(objeto=nombre).first()
            if not item:
                return f"Error: Objeto {nombre} no encontrado en el inventario"
            if item.cantidad < cantidad:
                return f"Error: Cantidad insuficiente de {nombre} en el inventario"

            item.cantidad -= cantidad
            if item.cantidad == 0:
                session.delete(item)  # Eliminar el objeto si la cantidad llega a 0
            session.commit()

            return f"Objeto {nombre} retirado con cantidad {cantidad}"

        elif accion == "ver":
            # Mostrar el contenido del inventario
            contenido = session.query(Inventario).all()
            resultado = "Contenido del almacén:\n"
            for item in contenido:
                resultado += f"- {item.objeto}: {item.cantidad}\n"
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
    socket.bind("tcp://*:5556")  # Escuchar en el puerto 5555

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
