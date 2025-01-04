# Almacenes ??nombre?? -  Especificaciones v1
(hay que ponerle algún nombre al la aplicación)

(en esta versión sólo unas especificaciones básicas, ya se ampliará)

El objetivo de esta aplicación es crear un sistema distribuido de gestión de almacenes para una empresa que tiene varios almacenes separados. Cada almacén tendrá su propio nodo (un servidor con su base de datos local) y el sistema permitirá gestionar la información de los productos, el stock y la sincronización de datos entre los 
diferentes almacenes.

En cada nodo se desarrollan 2 programas:

Habrá un programa cliente __ClientUI__ que será el que el usuario manejará. Se comunica, en principio con el servicio:

__StoreService__ será un servicio que maneja la base de datos local.

El servicio también podrá consultar a otros nodos remotos, llamando a sus servicios correspondientes para consultar información. 

## Operaciones
(en esta versión definimos unas pocas )
### Gestión de Productos:
El usuario podrá hacer las siguientes operaciones
 - Aumentar cantidad de un artículo
 - Disminuri la cantidad de un artículo
 Si un artículo no existe, se crea.
 Si un artículo se queda a cero, nada, cantidad cero.
 Si se intenta restar más de lo que hay: error.
 - Consultar la cantidad de un artículo concreto.
 - Consultar listado completo de inventario local.

### Gestión interna:
 - Si al arrancar, no hay base de datos local, avisar la usuario y consultar para crear una nueva.


### Servicio:
- Servicio API REST en un puerto TCP
- Se ejeuta llamando al programa que se queda en memoria, daemon. Imprimirá la dirección TCP a la que responde.

## Cliente
- Programa UI de texto CLI(Command line interface). Mostrará menús en cada opción, para que el usuario no tenga que momorizar nada. Borrará la pantalla en cada menú.
