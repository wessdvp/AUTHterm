# Authenticator App

## Description

Authterm is a simple and secure terminal-based tool for managing your two-factor authentication (2FA) codes. It helps you generate and store your 2FA tokens safely.

## Features

- Easy to use interface
- Secure storage of 2FA tokens
- Fast access to your codes

## Installation Instructions

1. Open a terminal.
2. Navigate to the directory where the `install.sh` script is located.
3. Run the installation script with sudo:

   ```bash
   sudo ./install.sh
   ```

## Launching

After the installation is complete, you can launch the app by simply typing:

    authterm

## Usage

Once the app is running, follow the prompts to manage your 2FA tokens. Make sure to carefully read any prompts during the installation process for additional instructions or confirmations.

### Requirements

    Python 3
    pip3

### Required External Libraries
    
    pyotp

## Overview

This application is a terminal-based vault manager that allows users to securely store, edit, list, and delete secrets (like passwords or notes). It includes password protection and data is stored in a JSON file.

### Key Features

1. **Password Management**:
   - Users can set up a password for the vault.
   - The application verifies the entered password against a hashed version.

2. **Secret Management**:
   - Users can create new secrets, edit existing ones, list all stored secrets, and delete secrets.

3. **User Interface**:
   - The application uses the `curses` library for creating a text-based user interface, which supports keyboard navigation.

4. **Help and About Sections**:
   - Users can access information about the application and how to use it through the help menu.

## Troubleshooting

- If you encounter issues during installation, ensure you have pip3 installed and accessible in your `PATH`.
- Make sure to run the installation script with `sudo` to avoid permission issues.
- Check for any error messages in the terminal for guidance.

## License

This project is licensed under the CC BY License - see the LICENSE.txt file for details.