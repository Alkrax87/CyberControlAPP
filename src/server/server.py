import socket
import threading
import os
from colorama import Fore

HOST = '0.0.0.0'  # Escuchar en todas las interfaces de red
PORT = 8888  # Puerto de conexión
clients = []  # Almacenar las conexiones

# Función de limpiar la consola
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Función que maneja las conexiones
def handle_client(conn, addr):
    global clients
    print(Fore.GREEN + f"\nConexión establecida con: {addr}")
    clients.append(addr)
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            if data.decode('utf-8') == 'ping':
                conn.send('pong'.encode('utf-8'))
    except Exception as e:
        print(Fore.RED + f"Error con {addr}: {e}")
    finally:
        print(Fore.RED + f"\nConexión cerrada con: {addr}")
        clients.remove(addr)
        conn.close()

# Función que muestra las conexiones establecidas en tiempo real
def show_connections():
    while True:
        clear_screen()
        print(Fore.WHITE + "Estado de conexiones")
        print("---------------------")
        if clients:
            for idx, client in enumerate(clients):
                print(f"[{idx + 1}] {client}")
        else:
            print("No hay conexiones activas.")
        print("\nAtrás [0]")

        choice = input("Elige una opción: ")
        if choice == '0':
            break

# Función que muestra la interfaz de consola principal
def main_menu():
    while True:
        clear_screen()
        print(Fore.WHITE + "Proyecto Control de Cyber")
        print("-------------------------------------")
        print(f"Servidor escuchando en {HOST}:{PORT}")
        print("-------------------------------------")
        print("[1] Ver estado de conexiones")
        print("-------------------------------------")
        print("\n[9] Salir")

        choice = input("Elige una opción: ")
        if choice == '1':
            show_connections()
        elif choice == '9':
            print(Fore.YELLOW + "Cerrando servidor...")
            os._exit(0)

# Función principal del script
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    threading.Thread(target=main_menu, daemon=True).start()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

# Ejecución del script
if __name__ == "__main__":
    main()
