from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone, timedelta
import zmq
from flask import Flask, request, jsonify

# Configuración de SQLAlchemy

app = Flask(__name__)

Base = declarative_base()

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
    objeto = Column(String(70), ForeignKey('inventario.id'), nullable=False)
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


# Crear conexión con la base de datos
engine = create_engine('sqlite:///almacen.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


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


if __name__ == "__main__":
    puerto = int(input("Introduce un puerto para el nodo: "))
    app.run(port=puerto)
