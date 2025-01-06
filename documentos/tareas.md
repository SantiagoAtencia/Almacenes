
# Tareas
## Fase 1

### - Especificación. Requisitos funcionales.
- [x] 1 Explicación con Detalle de lo que tiene que hacer desde el punto de vista del usuario. Todas las interacciones posibles, excepciones.
	
### - Diseño de arquitectura software.
- [x] 2 Detalle de todos los elementos software a urilizar. Tecnologías para cada elementos, frameworks, librerías, servicios. EConfiguración de cada una, puertos, directorios... Especificación de protocolos e interfaces a hacer: sintaxis de mensajes. Ej: mensajes REST, mensajes internos ZMQ...
	
### - Desarrollo de manejador de base de datos:
	
  Es un proceso que maneja la base de datos con el ORM. Implementa un servidor ZMQ. PAra probarlo aisladamente, hacer un pequeño cliente ZMQ para hablar hacer las pruebas. Previamente se han tenido que definir lasintaxis de mensajes ZMQ.
- [x] 3.1 Definición de cliente de pruebas (=cliente ZMQ)y desarrollo del mismo. Batería de pruebas.
- [ ] 3.2 Desarrollo de programa proceso manejador base de datos (=servidor ZMQ)
- [ ] 3.3 Ejecutar cliente de pruebas contra el servidor, hasta pasar lo tests.
	
### -  Desarrollo de Servdior REST
- [x] 4.1 Definición de cliente de pruebas. (=clinte REST). Batería de pruebas.
- [ ] 4.2 Desarrollo de servidor REST, (sin cliente ZMQ hasta que esté listo)
- [ ] 4.3 Ejecución del cliente de pruebas.
- [ ] 4.4 Integración de cliente ZMQ en el servidor.
- [ ] 4.5 Pruebas desde cliente.
      
	(dado que el servidor REST también será el cliente ZMQ, las primeras pruebas fallarán hasta que se integre el cliente ZMQ)
	
### -  Integración de Servidor REST, con servidor ZMQ.
- [ ] 5.1 Integrar en un sólo programa, de forma que el programa tenga 2 procesos. El principal será el servidor REST y un hijo el servidor ZMQ. Comunicación interna por Socket UNIX.
- [ ] 5.2 Pruebas desde el cliente de pruebas desarrollado en el anterior punto.
	
### -  Programa cliente de usuario.

Es el interface con el usuario.
- [ ] 6.1 Definir batería de pruebas manuales que un usuario tendrá que hacer.
- [ ] 6.2 Desarrollo de programa, sin conexión a servidor.
- [ ] 6.3 Pruebas iniciales manuales, de menús y opciones, sin conexión a servidor.
- [ ] 6.4 Cuando esté lista la integración de servidores: pruebas manuales finales.
	
### - Depuración de programa, refactorización, documentación.
- [ ] 7 Depuración
	
_____ fase 1 completada ____	

## Fase 2
### - Conseguir visivilidad de IPs por VPN
- [ ]	8 Como en la VPN las IPs serán dinámicas, intentar con túneles SSH o un "pseudo DNS"
	
### - Ampliación de programa para comunicación entre servidores
- [ ]	9.1 Definición de pruebas para nuevas funciones
- [ ]	9.2 Programación de nuevas funciones.
- [ ]	9.3 Depliegue de servidores en una misma máquina.
- [ ]	9.4 Pruebas con un cliente y varios clientes
- [ ]	9.5 Pruebas de despliegue en máquinas diferentes (requiere tener funcionando VPN)

### - Depuración de programa, refactorización, documentación.
- [ ] 	10 Depuración
_____ 	fase 2 completada _______
## Fase 3
### - Lista dinámica de servidores.
- [ ] 11.1 Definición de pruebas
- [ ] 11.2 Amplliar base de datos con tabla nueva de hosts
- [ ] 11.3 Ampliar servidor REST para que detecte desconexión, reconexión, alta de nodo, baja de nodo, consulta automática a vecinos, respuesta a vecinos, etc...
- [ ] 11.4 Implementar algoritmo de actualización automática de tabla, versionado, etc.
- [ ] 11.5 Ampliar cliente de usuario para permitir altas y bajas.
- [ ] 11.6 Pruebas
	
### - Depuración de programa, refactorización, documentación.
- [ ] 12 Depuración
_____ 	fase 3 completada _______
	
