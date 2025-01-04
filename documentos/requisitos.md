
El objetivo de esta aplicación es crear un sistema distribuido de gestión de almacenes para una empresa que tiene varios almacenes separados. Cada almacén tendrá su propio nodo (un servidor con su base de datos local) y el sistema permitirá gestionar la información de los productos, el stock y la sincronización de datos entre los diferentes almacenes.

# Requisitos Funcionales
- Gestión de Productos:
Registrar nuevos productos en el inventario de cada almacén.
Modificar información de productos (nombre, descripción, precio, cantidad).
Eliminar productos.
Reservar productos y eliminarlos de reservados
Consultar el inventario disponible en cada almacén.
- Gestión de Movimientos de Mercancías:
Registrar entradas y salidas de productos (ventas, compras, traslados).
Generar reportes de movimientos de mercancías (historial de entradas y salidas).
- Comunicación entre Servidores:
Los servidores pueden intercambiar información sobre el inventario y movimientos de mercancías mediante solicitudes REST.
- Gestión de Base de Datos Local:
Cada almacén tiene su propia base de datos SQLite.
Las consultas a la base de datos local se gestionan secuencialmente mediante la cola de mensajes (ZMQ).
- Interfaz Cliente (Consola):
Un cliente de texto simple que permite realizar acciones de consulta y gestión de inventarios de forma básica.
# Requisitos No Funcionales
- Escalabilidad:
El sistema debe ser escalable, permitiendo agregar más servidores (almacenes) a medida que la empresa crece.
Los servidores deben poder desconectarse y reconectarse de forma dinámica.
- Rendimiento:
El servidor web debe ser capaz de manejar múltiples peticiones simultáneas de clientes y servidores sin afectar su rendimiento.
La comunicación con la base de datos debe ser eficiente, utilizando la cola de mensajes para coordinar las consultas.
- Seguridad:
Los clientes y servidores deben comunicarse de manera segura utilizando HTTPS.
Los datos sensibles deben ser encriptados y protegidos adecuadamente.
- Fiabilidad:
El sistema debe ser tolerante a fallos, permitiendo reconectar servidores y clientes en caso de desconexión.
Tecnologías Utilizadas
Lenguaje de Programación: Python (para el servidor web REST y el cliente de texto).
- Servidor Web REST: Flask o FastAPI.
Base de Datos: SQLite.
Cola de Mensajes (MQ): ZMQ (para coordinar las peticiones y respuestas entre el servidor web y el manejador de base de datos).
ORM: SQLAlchemy (para interactuar con SQLite).
Cliente de Texto: Cliente de consola básico utilizando Python.

# Tecnologías Utilizadas
- Lenguaje de Programación: Python (para el servidor web REST y el cliente de texto).
- Servidor Web REST: Flask o FastAPI.
- Base de Datos: SQLite.
- Cola de Mensajes (MQ): ZMQ (para coordinar las peticiones y respuestas entre el servidor web y el manejador de base de datos).
- ORM: SQLAlchemy (para interactuar con SQLite).
- Cliente de Texto: Cliente de consola básico utilizando Python.
