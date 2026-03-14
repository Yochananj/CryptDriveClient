<img width="298" height="256" alt="icon" src="https://github.com/user-attachments/assets/cd4bb9d5-06c9-404d-8ef5-f09261e0ed28" />

# Cyber 2025-26 Final Project - © Yochanan Julian - CryptDrive Client

A secure, end-to-end encrypted cloud storage desktop application built with Python and Flet. CryptDrive enables users to store, manage, and access their files with client-side encryption, ensuring that only the user can decrypt and access their data.

## 🚀 Getting Started

**Note**: This is a client application that requires a compatible CryptDrive server to function. The server implementation is not included in this repository (See [Yochananj/CryptDriveServer](https://github.com/Yochananj/CryptDriveServer))

### Installation

1. Clone the repository:
```shell
git clone https://github.com/Yochananj/CryptDriveClient
cd CryptDriveClient
```


2. Run the installation script:

For MacOS:
```shell
chmod +x install.sh
./install.sh
```
For Windows:
```powershell
.\ install.ps1
```

3. Enter your server's address when prompted

```shell
"Enter server IP address (default == localhost): "
1.2.3.4
```

## 🖥️ Supported Platforms

- **macOS**: Full support with native file dialogs (using AppleScript)
- **Windows**: Full support with native file dialogs (using PowerShell)


## 🔐 Security Features

- **End-to-End Encryption**: Files are encrypted on the client side before upload using AES-GCM
- **Password-Based Key Derivation**: Uses Argon2 for secure password-based key derivation
- **Master Key Encryption**: File encryption master key is itself encrypted with a password-derived key
- **Secure Communication**: X25519 key exchange for establishing encrypted client-server communication channels
- **SHA-256 Password Hashing**: Server-side authentication uses SHA-256 hashed passwords

## ⚠️ Security Notes

- **Never share your password** - it's the only way to decrypt your files
- **Lost passwords cannot be recovered** - all files will be permanently inaccessible
- The server never has access to unencrypted files or encryption keys
- All encryption happens client-side before any data transmission


## 📂 Project Structure

```
CryptDriveClient/
├── src/
│   ├── Controllers/          # MVC Controllers
│   ├── Dependencies/         # Constants and utilities
│   ├── Services/            # Business logic services
│   ├── Views/               # UI components
│   └── main.py              # Application entry point
└── assets/                  # Application assets (fonts, icons)
```
### MVC Pattern
The application follows the Model-View-Controller pattern:

- **Models**: Services handle business logic (encryption, file operations, communication)
- **Views**: UI components built with Flet framework
- **Controllers**: Manage user interactions and coordinate between views and services

## 🛠️ Technology Stack

- **Python 3.10+**
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
- **`UIElements`**: Common UI components used throughout the application
