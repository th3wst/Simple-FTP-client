import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import bcrypt
import socket
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import threading

CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ftp_credentials.cfg")

ftp_username = None
ftp_hashed_password = None


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

def save_credentials(username, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    with open(CREDENTIALS_FILE, "w") as cred_file:
        cred_file.write(f"{username}\n{hashed_password.decode()}")

def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        messagebox.showerror("Error", "Credentials file not found. Please set up credentials first.")
        return None, None

    with open(CREDENTIALS_FILE, "r") as cred_file:
        lines = cred_file.readlines()
        if len(lines) < 2:
            messagebox.showerror("Error", "Invalid credentials file format.")
            return None, None

        username = lines[0].strip()
        hashed_password = lines[1].strip()
        return username, hashed_password

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def setup_credentials():
    username = simpledialog.askstring("Set Username", "Enter FTP Username:")
    if not username:
        messagebox.showwarning("Warning", "Username cannot be empty!")
        return

    password = simpledialog.askstring("Set Password", "Enter FTP Password:", show='*')
    if not password:
        messagebox.showwarning("Warning", "Password cannot be empty!")
        return

    save_credentials(username, password)
    messagebox.showinfo("Success", "Credentials saved successfully!")

def start_ftp_server():
    global ftp_username, ftp_hashed_password

    ftp_username, ftp_hashed_password = load_credentials()
    if not ftp_username or not ftp_hashed_password:
        return

    entered_password = simpledialog.askstring("Verify Password", f"Enter the password for user {ftp_username}:", show='*')
    if not entered_password or not check_password(entered_password, ftp_hashed_password):
        messagebox.showerror("Error", "Invalid password. Server not started.")
        return

    local_ip = get_local_ip()

    upload_dir = "uploaded_files"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    authorizer = DummyAuthorizer()
    authorizer.add_user(ftp_username, entered_password, upload_dir, perm='elradfmw')

    handler = FTPHandler
    handler.authorizer = authorizer

    server = FTPServer((local_ip, 21), handler)

    ftp_thread = threading.Thread(target=server.serve_forever)
    ftp_thread.daemon = True
    ftp_thread.start()

    status_label.config(text=f"Server started! IP: {local_ip}, Username: {ftp_username}")
    start_button.config(state=tk.DISABLED)
    upload_button.config(state=tk.NORMAL)


def upload_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("All Files", "*.*")])

    if not file_paths:
        return

    from ftplib import FTP

    ftp = FTP(get_local_ip())
    ftp.login(ftp_username, ftp_hashed_password)

    for file_path in file_paths:
        with open(file_path, 'rb') as file:
            ftp.storbinary(f"STOR {os.path.basename(file_path)}", file)

    ftp.quit()

    messagebox.showinfo("Upload Complete", "Files uploaded successfully!")

root = tk.Tk()
root.title("FTP File Transfer 1.0")
root.geometry("400x250")
root.resizable(False, False)

setup_button = tk.Button(root, text="Set Up Credentials", command=setup_credentials)
setup_button.pack(pady=10)

start_button = tk.Button(root, text="Start Server", command=start_ftp_server)
start_button.pack(pady=10)

upload_button = tk.Button(root, text="Upload Files", command=upload_files, state=tk.DISABLED)
upload_button.pack(pady=10)

status_label = tk.Label(root, text="Server not started.", wraplength=350)
status_label.pack(pady=20)

root.mainloop()