# Simple-FTP-Client

A lightweight, GUI-based FTP file sharing client and server application. This program allows you to securely transfer files over your local network using an easy-to-use interface.

## Features

- **Set Up Credentials**: Configure your FTP server with a username and password for secure access.
- **Start Server**: Launch a local FTP server to enable file uploads.
- **File Upload**: Easily upload files to the server with a simple file selection dialog.
- **Secure File Handling**: Files are stored in a dedicated upload directory (`uploaded_files`).

## How to Use

### Download and Run

1. Place the executable in a folder of your choice.
2. Double-click the executable to launch the application.

### Set Up Credentials

1. Click the "Set Up Credentials" button.
2. Enter a username and password for your FTP server.
3. Credentials will be securely saved in a file named `ftp_credentials.cfg` within the executable's directory.

### Start the FTP Server

1. Click the "Start Server" button.
2. The server will start running, and the application will display the server's IP address and username.

### Upload Files

1. Click the "Upload Files" button to select files from your computer.
2. The selected files will be uploaded to the server's `uploaded_files` directory.

## Notes

- The FTP server runs locally and is accessible only within your local network.
- Ensure your firewall settings allow traffic on port 21 to enable successful connections.
- If you encounter issues, make sure your `ftp_credentials.cfg` file exists and has valid credentials.

## System Requirements

- **Python 3.7 or higher** (if running from source)
- **pyftpdlib** & **bcrypt** Python libraries (for source code usage)

To install the required dependencies, run:

```bash
pip install bcrypt pyftpdlib

