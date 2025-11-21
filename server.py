import socket
import select

clientes = {} # SE CREA UN DICCIONARIO EN DONDE SE GUARDARAN LOS SOCKETS Y NOMBRES DE LOS CLIENTES
MONITOREO_DE_SOCKETS = [] # SE CREA UNA LISTA DE MONITOREO DE SOCKETS PARA SELECT
DIRECCION_IP = '127.0.0.1'
PUERTO = 5000

# SE CREA LA FUNCION PRINCIPAL DEL SERVIDOR
def server():
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SE CREA EL OBJETO SOCKET DEL SERVIDOR CON IPv4 Y TCP
    socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # ESTA FUNCION NOS PERMITE REUTILIZAR LA DIRECCION IP Y EL PUERTO EN CASO DE CERRAR EL SERVIDOR Y QUERER ACTIVARLO RAPIDAMENTE 
    socket_server.bind((DIRECCION_IP, PUERTO)) # SE ENLAZA LA DIRECCION IP Y EL PUERTO
    socket_server.listen(5) # SE ACTIVA EL MODO ESCUCHA DEL SERVIDOR

    print(f"Escuchando en: {DIRECCION_IP}: Puerto:{PUERTO}") # SE IMPRIME MENSAJE

    MONITOREO_DE_SOCKETS.append(socket_server) # SE AGREGA A LA LISTA DE MONITOREO EL SOCKET DEL SERVIDOR

    # BUCLE PRINCIPAL
    while True:
        sockets_listos, _, sockets_error = select.select(MONITOREO_DE_SOCKETS, [], MONITOREO_DE_SOCKETS) # SE INICIALIZA SELECT - NOS RETORNA 3 LISTAS (LECTURA, ESCRITURA, ERROR)
        
        # SE RECORRE LA LISTA DE SOCKETS LISTOS
        for socket_actual in sockets_listos:
            # SI EL SOCKET_ACTUAL ES IGUAL A SOCKET_SERVER ES PORQUE HAY UN NUEVO CLIENTE QUERIENDO CONECTARSE
            if socket_actual == socket_server:
                cliente_socket, cliente_direccion = socket_server.accept() # SE ACEPTA LA CONEXION Y SE CREA UN NUEVO SOCKET PARA EL CLIENTE NUEVO
                print(f"Se acepto conexion de {cliente_direccion}") # MENSAJE

                try:
                    nombre_cliente = cliente_socket.recv(1024) # SE ESPERA RECIBIR DATOS DEL CLIENTE (EN ESTE CASO, SU NOMBRE)

                    # SI EL NOMBRE DEL CLIENTE NO EXISTE SIGNIFICA QUE EL CLIENTE SE DESCONECTO
                    if not nombre_cliente:
                        print(f"Cliente {cliente_direccion} se desconectó antes de enviar su nombre.") # MUESTRA EN LA TERMINAL DEL SERVIDOR EL MENSAJE
                        cliente_socket.close() # SE CIERRA EL SOCKET DEL CLIENTE
                        continue

                    nombre_cliente = nombre_cliente.decode("utf-8").strip() # SE DECODIFICA EL NOMBRE RECIBIDO EN BYTES A TEXTO
                    MONITOREO_DE_SOCKETS.append(cliente_socket) # SE AGREGA A LA LISTA DE MONITOREO EL SOCKET DEL CLIENTE
                    clientes[cliente_socket] = nombre_cliente # SE AGREGA AL DICCONARIO EL SOCKET Y EL NOMBRE DEL CLIENTE
                    print(f"{nombre_cliente} se ha conectado desde {cliente_direccion}") # MUESTRA EN LA TERMINAL DEL SERVIDOR EL MENSAJE
                    broadcast(cliente_socket, f"{nombre_cliente} se ha unido al chat.".encode('utf-8')) # ENVIA EL MENSAJE A TODOS LOS DEMAS CLIENTES MENOS AL QUE ACABA DE CONECTARSE
                    usuarios_actuales = ", ".join(clientes.values()) # SE EXTRAE DEL DICCIONARIO DE CLIENTES SOLO LOS VALORES (LOS NOMBRES)
                    cliente_socket.send(f"Usuarios conectados: {usuarios_actuales}".encode('utf-8')) # ENVIA A CADA CLIENTE ESA "LISTA" DE NOMBRES CONECTADOS
                
                # IDENTIFICA SI OCURRE CUALQUIER TIPO DE ERROR AL RECIBIR EL NOMBRE
                except Exception as e:
                    print(f"Error al recibir nombre:{e}") # SE IMPRIME EL TIPO DE ERROR
                    cliente_socket.close() # SE CIERRA EL SOCKET DE ESE CLIENTE

            # SI YA EXISTE UN CLIENTE CONECTADO Y HA ENVIADO SU NOMBRE EXITOSAMENTE
            else:
                try:
                    mensaje = socket_actual.recv(1024) # SE ESPERA RECIBIR EL MENSAJE DEL CLIENTE

                    # SI EL MENSAJE EXISTE
                    if mensaje:
                        nombre_clien = clientes[socket_actual] # SE TRAE EL NOMBRE DEL CLIENTE DEL DICCIONARIO
                        mensaje_texto = mensaje.decode("utf-8").strip() # SE DECODIFICA EL MENSAJE RECIBIDO EN BYTES A TEXTO
                        print(f"<{nombre_clien}>: {mensaje_texto}") # SE MUESTRA EN LA TERMINAL DEL SERVIDOR EL NOMBRE JUNTO CON EL MENSAJE
                        mensaje_a_enviar = f"<{nombre_clien}>: {mensaje_texto}".encode('utf-8') # CODIFICAMOS EL MENSAJE RECIBIDO DE VUELTA A BYTES PARA ENVIAR A LOS DEMAS CLIENTES
                        broadcast(socket_actual, mensaje_a_enviar) # ENVIA EL MENSAJE RECIBIDO A TODOS LOS DEMAS CLIENTES CONECTADOS

                    # SI EL CLIENTE DE DESCONECTO LIMPIAMENTE
                    else:
                        nombre_clien = clientes[socket_actual] # SE TRAE EL NOMBRE DEL CLIENTE DEL DICCIONARIO
                        print(f"{nombre_clien} se desconectó.") # SE MUESTRA EN LA TERMINAL DEL SERVIDOR QUIEN SE DESCONECTO
                        broadcast(socket_actual, f"{nombre_clien} se ha desconectado.".encode('utf-8')) # SE INFORMA A LOS DEMAS CLIENTES QUIEN SE DECONECTO

                        MONITOREO_DE_SOCKETS.remove(socket_actual) # ELIMINA DE LA LISTA DE MONITOREO AL CLIENTE DESCONECTADO
                        del clientes[socket_actual] # ELIMINA DEL DICCIONARIO DE CLIENTES AL CLIENTE DESCONECTADO
                        socket_actual.close() # SE CIERRA EL SOCKET DEL CLIENTE DESCONECTADO

                # IDENTIFICA SI EL CLIENTE SE DESCONECTO ABRUPTAMENTE
                except ConnectionResetError:
                    nombre_clien = clientes.get(socket_actual, "Cliente Desconocido") # SE TRAE EL NOMBRE DEL CLIENTE DESCONECTADO Y SI NO EXISTE TRAE CLIENTE DESCONOCIDO
                    print(f"{nombre_clien} se desconectó") # SE MUESTRA EN LA TERMINAL DEL SERVIDOR QUIEN SE DESCONECTO
                    broadcast(socket_actual, f"{nombre_clien} se ha desconectado.".encode('utf-8')) # INFORMAMOS A LOS DEMAS CLIENTES QUIEN SE DECONECTO

                    MONITOREO_DE_SOCKETS.remove(socket_actual) # ELIMINA DE LA LISTA DE MONITOREO AL CLIENTE DESCONECTADO
                    del clientes[socket_actual] # ELIMINA DEL DICCIONARIO DE CLIENTES AL CLIENTE DESCONECTADO
                    socket_actual.close() # SE CIERRA EL SOCKET DEL CLIENTE DESCONECTADO
        
        # SE RECORRE LA LISTA DE SOCKETS CON ERRORES
        for socket_error in sockets_error:
            # SI EXISTE EL SOCKET CON ERROR DENTRO DEL DICCIONARIO DE CLIENTES
            if socket_error in clientes:
                nombre_clien = clientes[socket_error] # SE TRAE EL NOMBRE DEL CLIENTE QUE TIENE UN ERROR
                print(f"Error en el socket de {nombre_clien}.") # SE INFORMA EN LA TERMINAL DEL SERVIDOR
                MONITOREO_DE_SOCKETS.remove(socket_error) # ELIMINA DE LA LISTA DE MONITOREO AL CLIENTE CON ERROR
                del clientes[socket_error] # ELIMINA DEL DICCIONARIO DE CLIENTES AL CLIENTE CON ERROR
            socket_error.close() # SE CIERRA EL SOCKET DEL CLIENTE CON ERROR

# SE CREA LA FUNCION DE BROADCAST
def broadcast(sender_socket, mensaje):
    # SE RECORRE EL DICCIONARIO DE CLIENTES
    for client_socket in clientes:
        # SI EL CLIENTE ES DIFERENTE DEL CLIENTE QUE ENVIO EL MENSAJE
        if client_socket != sender_socket:
            try:
                client_socket.send(mensaje) # SE ENVIA EL MENSAJE A LOS DEMAS CLIENTES

            # IDENTIFICA SI ALGO FALLO CON EL CLIENTE AL MOMENTO DE ENVIAR EL MENSAJE
            except:
                client_socket.close() # SE CIERRA EL SOCKET DEL CLIENTE

                # SI EL CLIENTE ESTA EN LA LISTA DE MONITOREO
                if client_socket in MONITOREO_DE_SOCKETS: # SE LO ELIMINA
                    MONITOREO_DE_SOCKETS.remove(client_socket)
                # SI EL CLIENTE ESTA EN EL DICCIONARIO DE CLIENTES
                if client_socket in clientes:
                    del clientes[client_socket] # SE LO ELIMINA

server() # SE LLAMA A LA FUNCION DEL SERVIDOR




    

