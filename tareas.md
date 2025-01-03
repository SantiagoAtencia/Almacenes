
# Tareas
## Fase 1

### - Especificación. Requisitos funcionales.
- [ ] Explicación con Detalle de lo que tiene que hacer desde el punto de vista del usuario. Todas las interacciones posibles, excepciones.
	
### - Diseño de arquitectura software.
- [ ] Detalle de todos los elementos software a urilizar. Tecnologías para cada elementos, frameworks, librerías, servicios. EConfiguración de cada una, puertos, directorios... Especificación de protocolos e interfaces a hacer: sintaxis de mensajes. Ej: mensajes REST, mensajes internos ZMQ...
	
### - Desarrollo de manejador de base de datos:
	
  Es un proceso que maneja la base de datos con el ORM. Implementa un servidor ZMQ. PAra probarlo aisladamente, hacer un pequeño cliente ZMQ para hablar hacer las pruebas. Previamente se han tenido que definir lasintaxis de mensajes ZMQ.
- [ ] Definición de cliente de pruebas (=cliente ZMQ)y desarrollo del mismo. Batería de pruebas.
- [ ] Desarrollo de programa proceso manejador base de datos (=servidor ZMQ)
- [ ] Ejecutar cliente de pruebas contra el servidor, hasta pasar lo tests.
	
### -  Desarrollo de Servdior REST
- [ ] Definición de cliente de pruebas. (=clinte REST). Batería de pruebas.
- [ ] Desarrollo de servidor REST, (sin cliente ZMQ hasta que esté listo)
- [ ] Ejecución del cliente de pruebas.
- [ ] Integración de cliente ZMQ en el servidor.
- [ ] Pruebas desde cliente.
      
	(dado que el servidor REST también será el cliente ZMQ, las primeras pruebas fallarán hasta que se integre el cliente ZMQ)
	
### -  Integración de Servidor REST, con servidor ZMQ.
- [ ] Integrar en un sólo programa, de forma que el programa tenga 2 procesos. El principal será el servidor REST y un hijo el servidor ZMQ. Comunicación interna por Socket UNIX.
- [ ] Pruebas desde el cliente de pruebas desarrollado en el anterior punto.
	
### -  Programa cliente de usuario.

Es el interface con el usuario.
- [ ] Definir batería de pruebas manuales que un usuario tendrá que hacer.
- [ ] Desarrollo de programa, sin conexión a servidor.
- [ ] Pruebas iniciales manuales, de menús y opciones, sin conexión a servidor.
- [ ] Cuando esté lista la integración de servidores: pruebas manuales finales.
	
### - Depuración de programa, refactorización, documentación.
- [ ] Depuración
	
_____ fase 1 completada ____	

## Fase 2
### - Conseguir visivilidad de IPs por VPN
- [ ]	Como en la VPN las IPs serán dinámicas, intentar con túneles SSH o un "pseudo DNS"
	
### - Ampliación de programa para comunicación entre servidores
- [ ]	Definición de pruebas para nuevas funciones
- [ ]	Programación de nuevas funciones.
- [ ]	Depliegue de servidores en una misma máquina.
- [ ]	Pruebas con un cliente y varios clientes
- [ ]	Pruebas de despliegue en máquinas diferentes (requiere tener funcionando VPN)

### - Depuración de programa, refactorización, documentación.
- [ ] Depuración
_____ 	fase 2 completada _______
## Fase 3
### - Lista dinámica de servidores.
- [ ] Definición de pruebas
- [ ] Amplliar base de datos con tabla nueva de hosts
- [ ] Ampliar servidor REST para que detecte desconexión, reconexión, alta de nodo, baja de nodo, consulta automática a vecinos, respuesta a vecinos, etc...
- [ ] Implementar algoritmo de actualización automática de tabla, versionado, etc.
- [ ] Ampliar cliente de usuario para permitir altas y bajas.
- [ ] Pruebas
	
### - Depuración de programa, refactorización, documentación.
- [ ] Depuración
_____ 	fase 3 completada _______
	
