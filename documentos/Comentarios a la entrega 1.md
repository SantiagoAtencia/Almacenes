Se entrega el proyecto a falta de algunas depuraciones. Lamentablemente ha faltado tiempo para rematar el trabajo para esta fecha.
Nuestra idea es terminarlo para antes de la presentación.

Actualmente el programa hace lo siguiente:
- Dataserver. Servidor que maneja la base de datos. Totalmente funcional, accesible por una cola de mensajes ZMQ. MAneja la base de datos local SQLite.
- Webserver. Servidor REST web. Funciona bien. Responde a todas las peticiones http REST. Los manejadores de las respuestas se comunican con el Dataserver a traves de ZMQ, usando un UNIX socket.
- Cliente. CLiente tipo CLI que interactura con el usuario con la consola y envia peticiones GET y POST por http al Webserver. Funciona

- Por otro lado un sistema de lista de "peers" distribuida, con funciones de alta, baja, broadcast. Control de consistencia mediante número de versiones, una variación de relojes de Lamport.
- El sistema también permite a un nuevo nodo elegir qué IP expone al grupo. Guarda la información en fichero json. Permite reconexiones, actualización de la lista de peers.
- Funciona con un servidor de prueba Web- Rest.
- Un make file que automáticamente: crea un entorno virtual python, instala los paquetes necsarios y ejecutará la aplicación. Para faciliar el despliegue

Falta:
 - Integrar los 2 servidores web en uno solo.
 - Ampliar algunos puntos REST para ampliar más funciones de consulta cruzada entre nodos.

