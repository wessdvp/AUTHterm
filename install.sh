#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo: sudo ./install.sh"
    exit 1
fi

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install it and run the script again."
    exit 1
fi

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Installing pip3..."
    apt install python3-pip -y
fi

# Upgrade pip to the latest version
echo "Upgrading pip to the latest version..."
pip3 install --root-user-action=ignore --upgrade pip

# Install virtualenv if not installed
if ! command -v virtualenv &> /dev/null; then
    echo "virtualenv is not installed. Installing it now..."
    pip3 install --root-user-action=ignore virtualenv
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating a virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate || { echo "Failed to activate virtual environment."; exit 1; }

# Install required Python packages
echo "Installing necessary Python packages..."
pip install --root-user-action=ignore pyotp

# Create or override the executable script for the app
echo "Creating executable script for authterm..."
cat << EOF > /usr/local/bin/authterm
#!/bin/bash
source "$(dirname "\$0")/venv/bin/activate"
exec python3 "$(dirname "\$0")/src/authenticator.py"
EOF

# Make the script executable
chmod +x /usr/local/bin/authterm

echo -e "\nInstallation complete! Use 'authterm' to run your app."

