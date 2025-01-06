# Esquema
- Función :\
  Entrada: entrada\
  Salida: salida
  
# Funciones Cliente a Web Server
- añadirObjeto:\
  Entrada: "/inventario/annadir", "POST", { nombre, cantidad }\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados, "mensaje": f"Objeto {nombre} annadido con cantidad {cantidad}"\
  
- sacarObjeto:\
  Entrada: "/inventario/sacar", "POST", { nombre, cantidad }\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados, "mensaje": f"Objeto {nombre} sacado con cantidad {cantidad}"\
  
- reservarObjeto:\
  Entrada: "/inventario/reservar", "POST", { nombre, cantidad }\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados, "mensaje": f"Objeto {nombre} reservado con cantidad {cantidad}"\
  
- sacarReserva:\
  Entrada: "/inventario/sacar_reserva", "POST", { nombre, cantidad }\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados, "mensaje": f"Objeto {nombre} reserva sacada con cantidad {cantidad}"\
  
- cancelarReserva:\
  Entrada: "/inventario/cancelar_reserva", "POST", { nombre, cantidad }\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad, "reservados": item.reservados, "mensaje": f"Objeto {nombre} reserva cancelada con cantidad {cantidad}"\
  
- getItemQuantity:\
  Entrada: "/inventario/get_item_quantity", "POST", { nombre }\
  Salida: "status": "success", "nombre": nombre, "cantidad": item.cantidad\
  
- remove_db:\
  Entrada: "/inventario/remove_db", "POST", { nombre }\
  Salida: "status": "success", "nombre": nombre, "mensaje": f"Nueva base de datos {nombre}"\
  
- verAlmacen:\
  Entrada: "/inventario/ver", "GET"\
  Salida: resultado = [
                {"nombre": item.objeto, "cantidad": item.cantidad, "reservados": item.reservados}
                for item in contenido
            ]

- get_node_name:\
  Entrada: '/inventario/get_node_name', methods=['GET']\
  Salida: "status": "success", "node_name": NODE_NAME\

  
