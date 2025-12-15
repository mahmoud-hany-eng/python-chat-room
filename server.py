import socket
import threading
import os

clients = []
rooms = {}

# Function to handle incoming messages
def handle_client(client_socket, addr):
    try:
        # Receive room code and user name
        room_code = client_socket.recv(1024).decode('utf-8')
        name = client_socket.recv(1024).decode('utf-8')

        # Add client to the room
        if room_code not in rooms:
            rooms[room_code] = []
        rooms[room_code].append((client_socket, name))

        # Notify all clients in the room about the new user
        for client, _ in rooms[room_code]:
            client.send(f"{name} has joined the room {room_code}".encode('utf-8'))

        # Handle communication
        while True:
            message = client_socket.recv(1024)

            if not message:
                break

            # Handle file message
            if message.startswith(b"FILE|"):
                _, file_size, file_name = message.split(b"|")
                file_size = int(file_size)

                # Receive file data in chunks
                with open(f"received_{file_name.decode('utf-8')}", 'wb') as f:
                    bytes_received = 0
                    while bytes_received < file_size:
                        file_data = client_socket.recv(min(1024, file_size - bytes_received))
                        if not file_data:
                            break
                        f.write(file_data)
                        bytes_received += len(file_data)

                # Notify the room about the received file
                for client, _ in rooms[room_code]:
                    client.send(f"{name} sent a file: {file_name.decode('utf-8')}".encode('utf-8'))

            else:
                # Decode text message and broadcast it to all clients in the room
                message_text = message.decode('utf-8')
                for client, _ in rooms[room_code]:
                    client.send(f"{name}: {message_text}".encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Remove client from the room and close the connection
        for room_code, room_clients in rooms.items():
            if (client_socket, name) in room_clients:
                room_clients.remove((client_socket, name))
                # Notify the room about the user leaving
                for client, _ in room_clients:
                    client.send(f"{name} has left the room.".encode('utf-8'))
                break
        clients.remove(client_socket)
        client_socket.close()

# Server setup
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 5555))
    server_socket.listen(5)
    print("Server started...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"New connection from {addr}")
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()