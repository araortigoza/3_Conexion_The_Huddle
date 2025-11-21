import socket
import threading
import sys

DIRECCION_IP = '127.0.0.1'
PUERTO = 5000

# SE CREA LA FUNCION PARA RECIBIR MENSAJES
def recibir_mensajes(cliente_socket):
    primer_mensaje = True # SE CREA UNA BANDERA PARA IDENTIFICAR SI ES EL PRIMER MENSAJE DEL CLIENTE ENVIADO POR EL SERVIDOR
    while True:
        try:
            mensaje = cliente_socket.recv(1024) # SE ESPERA RECIBIR DATOS DEL SERVIDOR
            
            # SI EL MENSAJE NO EXISTE SIGNIFICA QUE EL SERVIDOR SE DESCONECTO CORRECTAMENTE
            if not mensaje:
                print("\n[!] El servidor se ha desconectado.") # INFORMA AL CLIENTE
                cliente_socket.close() # CIERRA EL SOCKET DEL CLIENTE
                sys.exit() # SE CIERRA EL PROGRAMA
            
            mensaje_texto = mensaje.decode("utf-8").strip() # SE DECODIFICA EL MENSAJE RECIBIDO EN BYTES A TEXTO

            # SI EL MENSAJE EXISTE
            if mensaje_texto:
                print(f"\r\033[K{mensaje_texto}") # IMPRIME EN LA TERMINAL EL MENSAJE RECIBIDO - \r MUEVE EL CURSOR AL INICIO DE LA LINEA Y \033[K BORRA TODX LO QUE ESTA EN ESA LINEA (FRECUENTEMENTE EL ">" DEL PROMPT DE ENTRADA) E IMPRIME EL MENSAJE RECIBIDO
                # SI NO ES EL PRIMER MENSAJE
                if not primer_mensaje:
                    print("> ", end="", flush=True) # REIMPRIME EL PROMPT DE ENTRADA - flush=True ASEGURA QUE SE MUESTRE INMEDIATAMENTE
                # CAMBIAMOS LA BANDERA CUANDO YA NO ES EL PRIMER MENSAJE ENVIADO POR EL SERVIDOR
                else:
                    primer_mensaje = False  

        # SI EL SERVIDOR SE DESCONECTA ABRUPTAMENTE
        except ConnectionResetError:
            print("\n[!] La conexión con el servidor fue reiniciada o cerrada abruptamente.") # INFORMA AL CLIENTE
            cliente_socket.close() # CIERRA EL SOCKET DEL CLIENTE
            sys.exit() # SE CIERRA EL PROGRAMA

        # SI OCURRE CUALQUIER OTRO TIPO DE ERROR
        except OSError:
            break # SE TERMINA LA FUNCION

# SE CREA LA FUNCION PRINCIPAL DE CLIENTE
def cliente():
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SE CREA EL OBJETO SOCKET DEL CLIENTE CON IPv4 Y TCP
    try:
        cliente_socket.connect((DIRECCION_IP, PUERTO)) # SE CONECTA CON EL SERVIDOR A TRAVES DE LA IP Y EL PUERTO
    
    # SI EL CLIENTE NO PUDO CONECTARSE AL SERVIDOR
    except ConnectionRefusedError:
        print(f"Error: No se pudo conectar al servidor en {DIRECCION_IP}:{PUERTO}. Asegúrate de que el servidor esté corriendo.") # INFORMA AL CLIENTE
        sys.exit() # CIERRA EL PROGRAMA

    print("🌈 Bienvenido al Chat 🌈") # MENSAJE DE BIENVENIDA AL CLIENTE

    # SE INICIA UN BUCLE HASTA QUE EL CLIENTE INGRESE SU NOMBRE
    while True:
        nombre = input("Por favor, ingresa tu nombre: ").strip()
        if nombre:
            break
        print("El nombre no puede estar vacío. Intenta de nuevo.")

    cliente_socket.send(nombre.encode('utf-8')) # SE ENVIA AL SERVIDOR EL NOMBRE INGRESADO POR EL CLIENTE

    hilo_secundario = threading.Thread(target=recibir_mensajes, args=(cliente_socket,)) # SE CREA UN HILO SECUNDARIO
    hilo_secundario.daemon = True # SE DEFINE EL HILO COMO DAEMON - ESTO SIGNIFICA QUE ESTE HILO SE DETIENE AUTOMATICAMENTE CUANDO EL HILO PRINCIPAL SE CIERRA
    hilo_secundario.start() # COMIENZA A EJECUTARSE EL HILO SECUNDARIO

    # MENSAJES CON INSTRUCCIONES PARA EL CLIENTE 
    print("\n¡Conexión establecida! Escribe un mensaje y presiona Enter.") 
    print("Para salir, escribe 'salir' o presiona Ctrl+C.")
    
    # BUCLE PRINCIPAL
    while True:
        try:
            mensaje_a_enviar = input("> ") # PERMITIMOS AL CLIENTE ESCRIBIR SU MENSAJE CON UN PROMPT DE ENTRADA (">")

            # SI EL MENSAJE ES IGUAL A SALIR
            if mensaje_a_enviar.lower() == 'salir':
                break # SE DETIENE EL BUCLE (DESCONEXION LIMPIA DEL CLIENTE)
            
            # SI NO EXISTE EL MENSAJE O ESTA VACIO
            if not mensaje_a_enviar.strip():
                continue # LO IGNORAMOS

            cliente_socket.send(mensaje_a_enviar.encode('utf-8')) # CODIFICAMOS EL MENSAJE DEL CLIENTE DE TEXTO A BYTES Y ENVIAMOS AL SERVIDOR

        # IDENTIFICA SI EL CLIENTE PRESIONO CTRL + C
        except KeyboardInterrupt:
            break # SE DETIENE EL BUCLE (DESCONEXION LIMPIA DEL CLIENTE)
        
        # IDENTIFICA CUALQUIER TIPO DE ERROR
        except Exception as e:
            print(f"Error al enviar: {e}") # IMPRIME EL TIPO DE ERROR
            break # SE DETIENE EL BUCLE (DESCONEXION ABRUPTA DEL CLIENTE)

    print("\nDesconectando...") # MENSAJE DE SALIDA
    cliente_socket.close() # CIERRA EL SOCKET DEL CLIENTE Y AVISA AL SERVIDOR QUE SE DESCONECTO

cliente() # SE LLAMA A LA FUNCION DEL CLIENTE
