# Arquitectura V1

[-> esquema](https://github.com/SantiagoAtencia/Almacenes/blob/main/documentos/linux_service_architecture.pdf)
## ClientUI
(Client User Interface)
- Programa Python tipo REPL
- Cada menú borra la pantalla, muestra opciones y consuta al usuario.
- Envía peticiones REST al servicio
- En principio se conecta al localhost y un puerto TCP prefijado: 10000
- (en la v2 le daremos opción de elegir host y puerto en la linea de comandos)
- Usará la librería Requests como cliente REST (ayuda: https://www.datacamp.com/tutorial/making-http-requests-in-python)

## Comandos REST
- POST para enviar un comando para editar datos. Se manda como diccionario python, y las librerías lo converten sólo a json.
    - Formato:

    ```
    data = {
        'command': 'inc',  # ejemplo de incrementar
        'objeto': 'cepillo',
        'quantity': '14',
    }
    ``` 
    - `inc`para incrementar
    - `dec`para decrementar

 - GET para pedir datos.
    - Formato:
    ```
    <URL>/objetos/objeto:id     # para pedir la cantidad de un item

    <URL>/objetos/              # para pedir el inventario completo

    <URL>/                      # info del servicio
    ```

## StoreService
Servicio consistente en un programa Pyton. El programa, ejecuta en memoria 2 procesos, el pricipal y un hijo. 
- El proceso principal será el __WebServer__.
- El proceso hijo será el __DataServer__.

El WebServer será el único cliente de DataServer. DataSever maneja su base de datos local. Sólo es accedido, únicamente, por su proceso padre, nada más. (expecto en fase de pruebas, que podremos usar un cliente de pruebas directo contra DataServer)

### WebServer
Se implementa con el framework web FastAPI
- Este framework directamente ejecuta el servidor we. Se han de definir las respuestas a las peticiones GET y POST, con funciones para cada caso.
- Dentro de cada "función manejadora de respuesta REST", se ve la petición, y si es de datos, que seán la mayoría, se manda la consulta en json al Datasever. Esto se hace mediante un mensaje ZMQ
- Podría haber mensajes REST que no sean de datos, como "terminar" o consultar si la base de datos existe.
    - TODO: lista de mensajes
    -  ...

### DataServer
Es un proceso corriendo con dos caras:
- Del lado "externo" sería el "servidor ZMQ". Es un bucle que va leyendo peticiones que lellegan por ZMQ y las va procesando.
- Del lado "interno" realiza las acciones en la base de datos. Se usa la librería SQLModel, que es un ORM para la base de datos SQLite.
- Objetos/clases:
    - Un objeto principal que es el blucle de lectura de mensajes. Es el "main" del proceso que se pone a esperar peticiones por ZMQ. Cuando le llega una, la descodifica y actua llamando a la base de datos. Puede haber mensajes especiales que no sean de datos:
        - Terminal proceso.
        - Otros en sl futuro
    - Un objeto base de datos que encapsula todo lo relacionado. Sus métodos son las acciones de modificación, consulta, etc. Se le pasan los parámetros de consulta y devuelve objetos ORM.
    #### Database
     - Será un fichero único porque será SQLite.
     - En principio en el directorio: `<app>/db_node1/almacen.sqlite`
    - Tabla "artículos", con campos: 
        - objeto
        - cantidad
    
     (en esta versión, el fichero es fijo, en posteriores puede que haya más subdirestorios para poder tener más nodos por máquina)

### ZMQ
- La comunicación entre los procesos será mediante ZMQ. Se usarán mensajes REQ-REP, que son los ideales aquí.
- El cliente ZME, que es el WebServer, puede crear varias sesiones http en paralelo. Por lo que cada sesión puede pedir, por mensajes ZMQ, cosas al DataServer. ZMQ se encarga de encolar las peticiones y dejar las sesiones bloqueadas hasta que se le responda. (ver tema del timeout)
- Se usará un socket UNIX para la comunicación ZMQ, al estar los dos procesos en la misma máquina: `/tmp/almacen_node1.sock`. 
(en v1, cambiará y habrá un socket por servicio, por eso se usará el nombre del nodo)


## Despliege
- Convendrá hacer un Makefile para que instale las librerías necesarias de python, tras hacer un entorno virtual, e instalar ZMQ.
## Programas provisionales
- Cliente ZMQ
    - Un cliente provisional que ataca al Datasever para probar que funciona bien.
    Es similar al programa completo del servicio pero en el proceso principal no tiene ningún servidor web