# Esquema
- Función :\
  Entrada: entrada\
  Salida: salida
  
# Funciones Cliente a Web Server
- añadirObjeto:\
  Entrada: json:"accion:annadir, nombre:item.nombre, cantidad:item.cantidad"\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados, "mensaje": f"Objeto {nombre} annadido con cantidad {cantidad}"\
  
- sacarObjeto:\
  Entrada: json:"accion:sacar, nombre:item.nombre, cantidad:item.cantidad"\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados, "mensaje": f"Objeto {nombre} sacado con cantidad {cantidad}"\
  
- reservarObjeto:\
  Entrada: json:"accion:reservar, nombre:item.nombre, cantidad:item.reservados"\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados, "mensaje": f"Objeto {nombre} reservado con cantidad {cantidad}"\
  
- sacarReserva:\
  Entrada: json:"accion:sacar_reserva, nombre:item.nombre, cantidad:item.reservados"\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados, "mensaje": f"Objeto {nombre} reserva sacada con cantidad {cantidad}"\
  
- cancelarReserva:\
  Entrada: json:"accion:cancelar_reserva, nombre:item.nombre, cantidad:item.reservados"\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados, "mensaje": f"Objeto {nombre} reserva cancelada con cantidad {cantidad}"\
  
- getItemQuantity:\
  Entrada: json:"accion:get_item_quantity, nombre:item.nombre"\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad\
  
- remove_db:\
  Entrada: json:"accion:remove_db, nombre:db.nombre"\
  Salida: "status": "success", "nombre": nombre, "mensaje": f"Nueva base de datos {nombre}"\
  
- verAlmacen:\
  Entrada: /inventario/ver\
  Salida: resultado = [
                {"nombre": item.objeto, "cantidad": item.cantidad, "reservados": item.reservados}
                for item in contenido
            ]

- get_node_name:\
  Entrada: "accion": "get_node_name"\
  Salida: "status": "success", "node_name": NODE_NAME\

  
