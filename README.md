<img width="298" height="256" alt="icon" src="https://github.com/user-attachments/assets/cd4bb9d5-06c9-404d-8ef5-f09261e0ed28" />

# Cyber 2025-26 Final Project - © Yochanan Julian - CryptDrive Client

A secure, end-to-end encrypted cloud storage desktop application built with Python and Flet. CryptDrive enables users to store, manage, and access their files with client-side encryption, ensuring that only the user can decrypt and access their data.

## 🚀 Getting Started

**Note**: This is a client application that requires a compatible CryptDrive server to function. The server implementation is not included in this repository (See [Yochananj/CryptDriveServer](https://github.com/Yochananj/CryptDriveServer))

### Installation

1. Clone the repository:
```shell script
git clone https://github.com/Yochananj/CryptDriveClient
cd CryptDriveClient
```


2. Set up a virtual environment:
```shell script
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```


3. Install dependencies:
```shell script
pip install flet cryptography argon2-cffi
```


### Running the Application

```shell script
python src/main.py
```


## 🖥️ Supported Platforms

- **macOS**: Full support with native file dialogs (using AppleScript)
- **Windows**: Full support with native file dialogs (using PowerShell)


## 📝 Server Configuration

The client connects to a CryptDrive server. Configure the server address in `src/Dependencies/Constants.py`:

```python
server_address = "localhost"  # Change to your server address
server_port = 8081           # Change to your server port
```

## 🔐 Security Features

- **End-to-End Encryption**: Files are encrypted on the client side before upload using AES-GCM
- **Password-Based Key Derivation**: Uses Argon2 for secure password-based key derivation
- **Master Key Encryption**: File encryption master key is itself encrypted with a password-derived key
- **Secure Communication**: X25519 key exchange for establishing encrypted client-server communication channels
- **SHA-256 Password Hashing**: Server-side authentication uses SHA-256 hashed passwords

## ⚠️ Security Notes

- Never share your password - it's the only way to decrypt your files
- The server never has access to unencrypted files or encryption keys
- All encryption happens client-side before any data transmission
- Lost passwords cannot be recovered - all files will be permanently inaccessible


## 📂 Project Structure

```
CryptDriveClient/
├── src/
│   ├── Controllers/          # MVC Controllers
│   ├── Dependencies/         # Constants and utilities
│   ├── Services/            # Business logic services
│   ├── Views/               # UI components
│   │   └── storage/         # Local storage directories
│   └── main.py              # Application entry point
└── assets/                  # Application assets (fonts, icons)
```
### MVC Pattern
The application follows the Model-View-Controller pattern:

- **Models**: Services handle business logic (encryption, file operations, communication)
- **Views**: UI components built with Flet framework
- **Controllers**: Manage user interactions and coordinate between views and services

## 🛠️ Technology Stack

- **Python 3.13.9**
- **Flet**: Cross-platform UI framework
- **cryptography**: Encryption library for AES-GCM and X25519
- **argon2-cffi**: Password-based key derivation


### Core Components

#### Services
- **`FileEncryptionService`**: Handles file encryption/decryption using AES-GCM
- **`SecureCommunicationManager`**: Manages encrypted client-server communication using X25519 key exchange
- **`ClientFileService`**: Handles local file system operations (cross-platform file dialogs)
- **`ClientCommsManager`**: High-level communication interface with the server
- **`PasswordHashingService`**: SHA-256 password hashing utility

#### Controllers
- **`HomeController`**: Manages the main file browsing interface and all file/directory operations
- **`LoginController`**: Handles user authentication
- **`SignUpController`**: Manages user registration

#### Views
- **`HomeView`**: Main application window with navigation rail
- **`LoginView`**: User login interface
- **`SignUpView`**: User registration interface
- **`FileContainer`**: File browser UI component
- **`AccountContainer`**: User account management UI
- **`AboutContainer`**: Application information
