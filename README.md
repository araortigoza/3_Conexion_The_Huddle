# 💬 Conexión: The Huddle

Chat en tiempo real por consola, implementado con **sockets TCP** en Python. Un servidor central retransmite los mensajes entre todos los clientes conectados.

## 📋 Descripción

El proyecto está compuesto por dos scripts independientes:

- **`server.py`**: levanta un servidor TCP que acepta múltiples clientes simultáneamente usando el módulo `select` (multiplexación de sockets, sin necesidad de crear un hilo por cliente). Al conectarse, cada cliente envía su nombre, y el servidor retransmite (`broadcast`) los mensajes de cada cliente a todos los demás.
- **`cliente.py`**: se conecta al servidor, pide un nombre de usuario y permite enviar mensajes por consola. Usa un hilo (`threading`) para recibir mensajes del servidor en paralelo, mientras el hilo principal espera que el usuario escriba.

### Funcionalidades

- Notificación a todos los clientes cuando alguien se une o se desconecta del chat.
- Al conectarse, se muestra la lista de usuarios ya conectados.
- Manejo de desconexiones limpias (el cliente escribe `salir` o cierra con `Ctrl+C`) y abruptas (`ConnectionResetError`).
- El prompt de entrada (`>`) se vuelve a dibujar automáticamente después de recibir un mensaje, para no interrumpir lo que el usuario esté escribiendo.

## ⚙️ Requisitos

- Python 3
- No requiere librerías externas (usa solo `socket`, `select`, `threading` y `sys`, incluidas en la instalación estándar de Python)

## 🚀 Cómo ejecutar

1. Iniciar el servidor:

```bash
python server.py
```

2. En una o más terminales adicionales, iniciar uno o varios clientes:

```bash
python cliente.py
```

Por defecto, el servidor escucha en `127.0.0.1:5000`. Si se quiere correr en otra IP o puerto, hay que modificar las constantes `DIRECCION_IP` y `PUERTO` al inicio de `server.py` y `cliente.py`.

## 🧠 Detalles técnicos

- El servidor mantiene un diccionario `clientes` que asocia cada socket con el nombre de usuario correspondiente, y una lista `MONITOREO_DE_SOCKETS` que `select.select()` usa para saber qué sockets están listos para leer o presentan errores.
- Cuando un socket nuevo aparece como "listo" y coincide con el socket del propio servidor, se interpreta como una nueva conexión entrante; en caso contrario, se interpreta como un mensaje de un cliente ya conectado.
- La función `broadcast` recorre todos los clientes conectados (excepto el que envió el mensaje) y les reenvía el mensaje, eliminando del diccionario y de la lista de monitoreo a cualquier cliente cuyo envío falle.
- Del lado del cliente, el hilo secundario (`recibir_mensajes`) corre en modo `daemon`, por lo que se cierra automáticamente cuando el hilo principal termina, sin necesidad de lógica adicional de limpieza.
