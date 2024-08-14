import socket
import threading
import configparser
import time
import uuid
import os
from colorama import Fore

CONFIG_FILE = 'client_config.ini'  # Archivo de configuración del cliente
RETRY_INTERVAL = 5  # Intervalo de reconexión
PORT = 8888  # Puerto de conexión

# Función para cargar data del archivo client_config.ini
def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        return None
    config.read(CONFIG_FILE)
    return config

# Creación del archivo client_config.ini y guardamos la ip y mac del cliente
def save_config(server_ip):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'server_ip': server_ip,
        'mac': ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# Función de conexión con el servidor
def connect_to_server(server_ip, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_ip, port))
        print(Fore.GREEN + f"Conexión establecida con éxito con el servidor {server_ip}:{port}")
        return client
    except socket.error as e:
        print(Fore.RED + f"No se pudo conectar al servidor en {server_ip}:{port}.")
        print(Fore.RED + f"Error: {e}")
        return None

# Función de monitor de la conexión con el servidor
def monitor_connection(client, server_ip, port):
    try:
        while True:
            time.sleep(2)  # Añadir un pequeño retardo antes de enviar el primer ping
            client.send("ping".encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            if response == "pong":
                print(Fore.GREEN + "Conectado...")
            else:
                print(Fore.RED + "Respuesta inesperada del servidor.")
            time.sleep(5)  # Verificar la conexión cada 5 segundos
    except socket.error as e:
        print(Fore.RED + f"Error en la conexión con el servidor {server_ip}:{port}: {e}")
        client.close()
        reconnect_to_server(server_ip, port)

# Función de reconexión con el servidor
def reconnect_to_server(server_ip, port):
    while True:
        print(Fore.CYAN + f"Intentando reconectar al servidor {server_ip}:{port}...")
        time.sleep(RETRY_INTERVAL)
        client = connect_to_server(server_ip, port)
        if client:
            monitor_thread = threading.Thread(target=monitor_connection, args=(client, server_ip, port), daemon=True)
            monitor_thread.start()
            monitor_thread.join()  # Esperar a que el hilo termine antes de intentar reconectar
            break

# Función principal del script
def main():
    config = load_config()
    if config is None:
        while True:
            server_ip = input(Fore.WHITE + "Ingrese la IP del servidor: ")
            client = connect_to_server(server_ip, PORT)
            if client:
                save_config(server_ip)  # Guardar la configuración solo si se establece la conexión
                monitor_thread = threading.Thread(target=monitor_connection, args=(client, server_ip, PORT), daemon=True)
                monitor_thread.start()
                monitor_thread.join()  # Mantener el hilo principal en ejecución mientras el monitor está activo
                break
            else:
                print(Fore.RED + "No se pudo establecer la conexión. Intente nuevamente.")
    else:
        server_ip = config['DEFAULT']['server_ip']
        client = connect_to_server(server_ip, PORT)
        if client:
            monitor_thread = threading.Thread(target=monitor_connection, args=(client, server_ip, PORT), daemon=True)
            monitor_thread.start()
            monitor_thread.join()
        else:
            reconnect_to_server(server_ip, PORT)

# Ejecución del script
if __name__ == "__main__":
    main()
