
# Diseño de aplicación.
  Se supone que es tenemos una empresa con diferentes almacenes separados. Cada almacén tiene un ordenador con el control de almacén propio. Son los nodos de una aplicación distribuida.

 Para simplificar he pensado hacer unas fases:
 
 fase 1: un servidor con una base de datos y un cliente.
 
 fase 2: más servidores, en una lista fija y conocida, y que los servidores de consulten
 
 fase 3: lista dinámica de servidores, posibilidad de altas, bajas, desconexiones, reconoexiones.
 
 fase 4: cliente gráfico,(si da tiempo)
 
 

## Arquitectura

Cada nodo ejecuta el mismo programa "server". Es un servicio linux (daemon).
 Este servicio tiene una base de datos local con los datos de su almaceén.
 
 TAmbién habrá una apliación cliente que se ejecuta en cada nodo, comunicándose al servidor local.
 
 El programa cliente sólo se conecta al servidor, que es el que hace toda la lógica. Cada servidor se conecta por red al resto de los servidores también.

Tecnologías:
La comunicación con un servidor, desde un client u otro servidor será con API REST (http).
Por tanto el servidor tendrá un servidor web respondiendo las peticiones REST.
Cada servidor tendrá una base de dalos local SQLite.
El servidor web puede atender varias peticiones http simultaneamente (diferentes sesiones hppt), es lo normal en los servidores web. Por otro lado, la base de datos, al ser sin servidor(es SQLite), conviene accederla secuancialmente. Por tanto, vamos a usar una cola de mensajes (MQ) para coordinar las peticiones REST y las consultas a la base de datos. Además, es una especificación del profesor. PAra este caso se podría hacer sin cola de mensajes, pero la usaremos. He pensado que el servicio ZMQ valdría para esto, ya que implementa un protocolo REQ/REP que es exactamente lo que necesitamos. 
Por tanto, el servidor tendrá dos procesos:
 - El servidor web/REST
 - El manejador de la base de datos (usaremos un ORM)
 
 El servidor crea una sesión por cada petición REST. En el manejador de cada petición, se envía un mensaje a la MQ (en ZMQ exisiste un tipo de mensaje REQ, que se queda esperando mensaje de respuesta)
 El menejador de la base de datos, va concumiendo mensajes secuencialmente de la cola. Procesa cada uno y manda a la MQ el mensaje de respuesta.
 
 Dado que el programa tiene que ejecuar 2 servicios, he pensado que el programa principal podría ser el servidor web/REST y lanzar un proceso hijo que sea el manejador de la base de datos. Por que el servidor REST será el cliente del manejador de la base de datos ( a traves de la MQ)
 
 Cliente:
 Un simple cliente de texto, con menús de texto básicos, que será cliente de un servidor REST al que se conecte
 
### Librerías a usar:
ZMQ tiene librería para python. Viendo los ejemplos, parece muy fácil de usar porque ya implementa la funciones que necesitamos. Creo que no requiere servicio ejecutándose, son unas librerías que se ejecutan desde el código.
Para la base de datos, el ORM que me parece mejor en nuestro caso es SQLModel. Viendo los ejemplos, parece bastante sencillo manejar la base de datos desde python.
Para el servidor web/REST, he visto que con FastAPI es también muy fácil, copiando los ejemplos y modificándolos.

Estos son los paquetes que he encontrado y me parece que nos podrían valer, pero si veis otros, lo comentamos.
Lo mismo digo con la arquitectura software, es como yo lo veo, si teneis otras ideas, las comentamos.

Para el desarrollo he pensado esto:
- En fase de desarollo podemos usar codespaces como en la otra. A mi me gusta.
- En VSCode (que es lo que hay en codespaces) se puede instalar una extensión que permite ver bases de datos SQLite, así que, vemos las tripas de la base de datos en tiempo real.
- Cuando necesitemos ejecutar varios servidores, se puede hacer desde la misma máquina, dándole a la aplicación un parámetro que usará para elegir un puerto TCP diferente y una base de datos diferente. Así que se ejecutarán 2 o 3 o más servidores, cada uno en un puerto. Me parece fácil.
- Cuando funcione, en teoría, sólo hay que instalar un servidor en máquinas diferentes, y con sus direcciones IP debería funcionar. Usaremos una VPN.


SQLModel: 
 https://sqlmodel.tiangolo.com/
 https://sqlmodel.tiangolo.com/learn/
 
FastAPI:
 https://fastapi.tiangolo.com/tutorial/first-steps/
 (FastAPI hace mil cosas, solo usaremos un servidor REST simple)

ZMQ:
 https://zeromq.org/get-started/
 https://zeromq.org/languages/python/
	(ZMQ tiene mucha documentación, es muy potente. Pero nosotros no usaremos casi nada, no hace falta leer más que la introducción y el ejemplo de python, si quereis ir al grano)

Python: 
 El que no sepa python, que mire esto:
 https://blu3r4y.github.io/python-for-java-developers/?print-pdf
 El que tenga tiempo, el tutorial oficial de python está muy bien: https://docs.python.org/3/tutorial/
 

