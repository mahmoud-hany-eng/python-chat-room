import socket
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import os

# Function to handle receiving messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                chat_box.config(state=tk.NORMAL)  # Allow editing the chat box
                chat_box.insert(tk.END, message + '\n')  # Display new message
                chat_box.config(state=tk.DISABLED)  # Prevent editing the chat box
                chat_box.yview(tk.END)  # Scroll to the bottom
            else:
                break
        except Exception as e:
            print(f"Error: {e}")
            break

# Function to send messages to the server
def send_message(client_socket, message):
    try:
        client_socket.send(message.encode('utf-8'))
    except Exception as e:
        print(f"Error sending message: {e}")

# Function to send files to the server
def send_file(client_socket, file_path):
    try:
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        # Notify the server of an incoming file
        client_socket.send(f"FILE|{file_size}|{file_name}".encode('utf-8'))
        
        # Send the file in chunks
        with open(file_path, "rb") as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                client_socket.send(data)
        
        # Notify user of successful file transfer
        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, f"Sent file: {file_name}\n")
        chat_box.config(state=tk.DISABLED)
        chat_box.yview(tk.END)

    except Exception as e:
        print(f"Error sending file: {e}")

# Function to connect to the server
def connect_to_server(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    return client_socket

# Function to join a room
def join_room():
    room_code = room_code_entry.get()
    name = name_entry.get()
    if room_code and name:
        send_message(client_socket, room_code)
        send_message(client_socket, name)  # Send the user's name to the server
        join_button.config(state=tk.DISABLED)
        message_entry.config(state=tk.NORMAL)
        send_button.config(state=tk.NORMAL)
        file_button.config(state=tk.NORMAL)
        name_entry.config(state=tk.DISABLED)

# Function to send a chat message
def send_chat_message():
    message = message_entry.get()
    if message:
        send_message(client_socket, message)  # Send message
        message_entry.delete(0, tk.END)

# Function to send a file
def send_chat_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        send_file(client_socket, file_path)

# Function to start the client
def start_client():
    global client_socket
    ip = ip_entry.get()
    try:
        client_socket = connect_to_server(ip, 5555)
        # Start a thread to receive messages from the server
        thread = threading.Thread(target=receive_messages, args=(client_socket,))
        thread.daemon = True  # Ensure thread ends when the main program exits
        thread.start()
    except Exception as e:
        messagebox.showerror("Connection Error", f"Unable to connect to the server: {e}")

# Create the main window
root = tk.Tk()
root.title("Modern Chat Room")
root.geometry("500x900")  # Window size
root.configure(bg='#1e1e1e')

# Create a Frame for the content
frame = tk.Frame(root, bg='#1e1e1e')
frame.pack(fill=tk.BOTH, expand=True)

# Create GUI elements with modern styles
ip_label = tk.Label(frame, text="Server IP:", font=("Segoe UI", 12), bg='#1e1e1e', fg='#ecf0f1')
ip_label.pack(pady=5)

ip_entry = tk.Entry(frame, font=("Segoe UI", 12), bd=2, relief="solid", highlightthickness=2, highlightcolor='#2980b9', fg="#34495e", bg="#ecf0f1")
ip_entry.pack(pady=5, padx=20)

connect_button = tk.Button(frame, text="Connect", command=start_client, font=("Segoe UI", 12), bg='#3498db', fg='white', relief="flat", bd=0, padx=30, pady=5)
connect_button.pack(pady=5)

room_code_label = tk.Label(frame, text="Enter Room Code:", font=("Segoe UI", 12), bg='#1e1e1e', fg='#ecf0f1')
room_code_label.pack(pady=5)

room_code_entry = tk.Entry(frame, font=("Segoe UI", 12), bd=2, relief="solid", highlightthickness=2, highlightcolor='#2980b9', fg="#34495e", bg="#ecf0f1")
room_code_entry.pack(pady=5, padx=20)

name_label = tk.Label(frame, text="Enter Your Name:", font=("Segoe UI", 12), bg='#1e1e1e', fg='#ecf0f1')
name_label.pack(pady=5)

name_entry = tk.Entry(frame, font=("Segoe UI", 12), bd=2, relief="solid", highlightthickness=2, highlightcolor='#2980b9', fg="#34495e", bg="#ecf0f1")
name_entry.pack(pady=5, padx=20)

join_button = tk.Button(frame, text="Join Room", command=join_room, font=("Segoe UI", 12), bg='#3498db', fg='white', relief="flat", bd=0, padx=30, pady=5)
join_button.pack(pady=5)

# Chat Box - Showing messages
chat_box = tk.Text(frame, height=15, width=60, state=tk.DISABLED, font=("Segoe UI", 12), bg='#34495e', fg='#ecf0f1', bd=0)
chat_box.pack(pady=5)

# Message Entry Field
message_entry = tk.Entry(frame, width=40, font=("Segoe UI", 12), bd=2, relief="solid", highlightthickness=2, highlightcolor='#2980b9', fg="#34495e", bg="#ecf0f1")
message_entry.pack(pady=5, padx=20)

send_button = tk.Button(frame, text="Send", command=send_chat_message, font=("Segoe UI", 12), bg='#2ecc71', fg='white', relief="flat", bd=0, padx=30, pady=5)
send_button.pack(pady=10)
send_button.config(state=tk.DISABLED)  # Disabled until room is joined

# File Upload Button
file_button = tk.Button(frame, text="Send File", command=send_chat_file, font=("Segoe UI", 12), bg='#f39c12', fg='white', relief="flat", bd=0, padx=30, pady=5)
file_button.pack(pady=10)
file_button.config(state=tk.DISABLED)  # Disabled until room is joined

# Update the window and ensure everything is visible on startup
root.update_idletasks()
root.geometry(f"{root.winfo_width()}x{root.winfo_height()}")  # Resize window after all elements are packed

# Run the Tkinter event loop
root.mainloop()