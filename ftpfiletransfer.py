import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import os
import bcrypt
import socket
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import threading
import sys
from appdirs import AppDirs

dirs = AppDirs("ezFTP", "ezFTP")
CREDENTIALS_FILE = os.path.join(dirs.user_data_dir, "ftp_credentials.cfg")

ftp_username = None
ftp_hashed_password = None
ftp_server = None
ftp_thread = None
ftp_port = 21

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

def save_credentials(username, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    os.makedirs(dirs.user_data_dir, exist_ok=True)  # Ensure the directory exists
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
    global ftp_username, ftp_hashed_password, ftp_server, ftp_thread, ftp_port

    ftp_username, ftp_hashed_password = load_credentials()
    if not ftp_username or not ftp_hashed_password:
        return

    entered_password = simpledialog.askstring("Verify Password", f"Enter the password for user {ftp_username}:", show='*')
    if not entered_password or not check_password(entered_password, ftp_hashed_password):
        messagebox.showerror("Error", "Invalid password. Server not started.")
        return

    try:
        ftp_port = int(simpledialog.askstring("Set Port", "Enter the port number for the FTP server (default: 21):", initialvalue="21"))
        if ftp_port < 1 or ftp_port > 65535:
            raise ValueError
    except (ValueError, TypeError):
        messagebox.showerror("Error", "Invalid port number. Server not started.")
        return

    local_ip = get_local_ip()

    upload_dir = "uploaded_files"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    authorizer = DummyAuthorizer()
    authorizer.add_user(ftp_username, entered_password, upload_dir, perm='elradfmw')

    class CustomFTPHandler(FTPHandler):
        def on_connect(self):
            connection_label.config(text="Connection established.")

    handler = CustomFTPHandler
    handler.authorizer = authorizer

    ftp_server = FTPServer((local_ip, ftp_port), handler)

    ftp_thread = threading.Thread(target=ftp_server.serve_forever)
    ftp_thread.daemon = True
    ftp_thread.start()

    status_label.config(text=f"Server started! IP: {local_ip}, Port: {ftp_port}, Username: {ftp_username}")
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    upload_button.config(state=tk.NORMAL)

def stop_ftp_server():
    global ftp_server, ftp_thread

    if ftp_server:
        ftp_server.close_all()
        ftp_thread.join()

        ftp_server = None
        ftp_thread = None

        status_label.config(text="Server stopped.")
        connection_label.config(text="")
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        upload_button.config(state=tk.DISABLED)

def upload_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("All Files", "*.*")])

    if not file_paths:
        return

    from ftplib import FTP

    ftp = FTP(get_local_ip())

    entered_password = simpledialog.askstring("Enter FTP Password", "Enter password for user:")
    if not entered_password or not check_password(entered_password, ftp_hashed_password):
        messagebox.showerror("Error", "Invalid password. Unable to log in.")
        return

    ftp.login(ftp_username, entered_password)

    progress_window = tk.Toplevel(root)
    progress_window.title("Upload Progress")
    progress_window.geometry("400x100")

    progress_label = tk.Label(progress_window, text="Uploading files...")
    progress_label.pack(pady=10)

    progress_bar = ttk.Progressbar(progress_window, length=300, mode="determinate")
    progress_bar.pack(pady=10)

    progress_bar['maximum'] = len(file_paths)

    for i, file_path in enumerate(file_paths, 1):
        with open(file_path, 'rb') as file:
            ftp.storbinary(f"STOR {os.path.basename(file_path)}", file)
        progress_bar['value'] = i
        progress_window.update_idletasks()

    ftp.quit()

    progress_label.config(text="Upload Complete!")
    tk.Button(progress_window, text="Close", command=progress_window.destroy).pack(pady=10)

    messagebox.showinfo("Upload Complete", "Files uploaded successfully!")

root = tk.Tk()
root.title("ezFTP 2.0.2")
root.geometry("400x300")
root.resizable(False, False)

setup_button = tk.Button(root, text="Set Up Credentials", command=setup_credentials)
setup_button.pack(pady=10)

start_button = tk.Button(root, text="Start Server", command=start_ftp_server)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Server", command=stop_ftp_server, state=tk.DISABLED)
stop_button.pack(pady=10)

upload_button = tk.Button(root, text="Upload Files", command=upload_files, state=tk.DISABLED)
upload_button.pack(pady=10)

status_label = tk.Label(root, text="Server not started.", wraplength=350)
status_label.pack(pady=10)

connection_label = tk.Label(root, text="", wraplength=350, fg="green")
connection_label.pack(pady=5)

root.mainloop()
