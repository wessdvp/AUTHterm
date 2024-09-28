import curses
import time
import os
import pyotp
import json
import hashlib
import re

# A simple dictionary to store secrets
secrets = {}
password_hash = None

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_PATH = os.path.join(BASE_DIR, 'vault.json')

# Function to load splash art from a text file
def load_splash_art():
    splash_art_path = os.path.join(BASE_DIR, 'assets', 'splash.txt')  # Correct path to splash.txt
    if os.path.exists(splash_art_path):
        with open(splash_art_path, 'r', encoding='utf-8') as f:
            art_lines = f.read().strip().splitlines()
            return art_lines if art_lines else ["(Splash art is empty)"]
    else:
        return ["(Splash art not found)"]

# Function to load secrets from vault.json
def load_secrets():
    global secrets, password_hash  # Declare as global at the start
    if os.path.exists(VAULT_PATH):
        with open(VAULT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            password_hash = data.get("password_hash")
            secrets = data.get("secrets", {})

# Function to save secrets to vault.json
def save_secrets():
    global password_hash  # Declare as global at the start
    with open(VAULT_PATH, 'w', encoding='utf-8') as f:
        json.dump({"password_hash": password_hash, "secrets": secrets}, f)

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to handle the first launch password setup
def setup_password(stdscr):
    global password_hash  # Declare as global at the start
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 2, w//2 - 10, "Set up your vault password: ")
    stdscr.refresh()
    curses.noecho()  # Turn off echoing (hide cursor)
    password = stdscr.getstr(h//2 - 1, w//2 - 10, 20).decode('utf-8')
    password_hash = hash_password(password)
    save_secrets()  # Save the password hash and empty secrets
    stdscr.addstr(h//2 + 1, w//2 - 10, "Password set successfully!")
    stdscr.refresh()
    stdscr.getch()
    curses.echo()  # Turn on echoing again (show cursor)

# Function to verify password
def verify_password(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 2, w//2 - 10, "Enter vault password: ")
    stdscr.refresh()
    curses.noecho()  # Turn off echoing
    password = stdscr.getstr(h//2 - 1, w//2 - 10, 20).decode('utf-8')
    if hash_password(password) == password_hash:
        stdscr.addstr(h//2 + 1, w//2 - 10, "Password verified!")
        stdscr.refresh()
        stdscr.getch()
    else:
        stdscr.addstr(h//2 + 1, w//2 - 10, "Invalid password! Exiting...")
        stdscr.refresh()
        stdscr.getch()
        exit()

# splash screen
def splash_screen(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    splash_art = load_splash_art()
    art_start_y = max((h - len(splash_art)) // 2 - 4, 0)

    for i, line in enumerate(splash_art):
        x = max((w - len(line)) // 2, 0)
        stdscr.addstr(art_start_y + i, x, line.strip())

    developer_text = "wessdvp - 2024"
    stdscr.addstr(art_start_y + len(splash_art) + 2, (w - len(developer_text)) // 2, developer_text)

    prompt_text = "Press any key to continue..."
    stdscr.addstr(art_start_y + len(splash_art) + 4, (w - len(prompt_text)) // 2, prompt_text)

    stdscr.refresh()
    stdscr.getch()

# Function to display the main menu with the splash art
def main_menu(stdscr):
    curses.curs_set(0)
    splash_art = load_splash_art()
    selected_option = 0
    h, w = stdscr.getmaxyx()
    menu = ["1. Create Secret", "2. Edit Secret", "3. List Secrets", "4. Delete Secret", "5. Change Password", "6. About", "7. Help", "8. Exit"]
    
    while True:
        stdscr.clear()
        # Display splash art at the top of the menu
        art_start_y = max((h - len(splash_art)) // 2 - 4, 0)
        for i, line in enumerate(splash_art):
            x = max((w - len(line)) // 2, 0)
            stdscr.addstr(art_start_y + i, x, line.strip())
        
        stdscr.addstr(art_start_y + len(splash_art) + 2, (w - len("Main Menu")) // 2, "Main Menu")

        for i in range(len(menu)):
            if i == selected_option:
                stdscr.addstr(art_start_y + len(splash_art) + 4 + i, (w - len(menu[i])) // 2, menu[i], curses.A_REVERSE)
            else:
                stdscr.addstr(art_start_y + len(splash_art) + 4 + i, (w - len(menu[i])) // 2, menu[i])

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and selected_option > 0:
            selected_option -= 1
        elif key == curses.KEY_DOWN and selected_option < len(menu) - 1:
            selected_option += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:  # Enter key
            if selected_option == 0:
                create_secret(stdscr)
            elif selected_option == 1:
                edit_secret(stdscr)
            elif selected_option == 2:
                list_secrets(stdscr)
            elif selected_option == 3:
                delete_secret(stdscr)
            elif selected_option == 4:
                change_password(stdscr)
            elif selected_option == 5:
                about(stdscr)
            elif selected_option == 6:
                help_menu(stdscr)
            elif selected_option == 7:
                exit_app(stdscr)
    curses.curs_set(1)

# Function to change password
def change_password(stdscr):
    global password_hash  # Declare as global at the start
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Function to get password without displaying any characters
    def get_password(prompt_y, prompt_x, prompt_text, max_length):
        stdscr.addstr(prompt_y, prompt_x, prompt_text + ": ")
        stdscr.addstr(h//2 + 4, w//2 - 10, "[ESC] Return to the main menu")
        stdscr.refresh()
        curses.noecho()  # Turn off echoing
        password = ""
        
        while True:
            ch = stdscr.getch()
            if ch == 27:  # ESC key
                return None  # Return None to indicate going back
            elif ch in [curses.KEY_BACKSPACE, 127]:  # Handle backspace
                if password:
                    password = password[:-1]  # Remove last character from password
                    # Clear the current input area
                    stdscr.addstr(prompt_y, prompt_x + len(prompt_text) + 2, " " * (max_length + 1))  # Clear previous input
                    stdscr.refresh()
            elif ch in range(32, 127):  # Only allow printable characters
                if len(password) < max_length:
                    password += chr(ch)  # Append new character to password
                    # Do not show anything (keep it hidden)
            elif ch == curses.KEY_ENTER or ch in [10, 13]:  # Enter key
                break
        return password

    current_password = get_password(h//2 - 1, w//2 - 10, "Current Password", 20)
    if current_password is None:  # User pressed ESC
        stdscr.addstr(h//2 + 5, w//2 - 10, "Operation aborted!     ")
        stdscr.refresh()
        return

    if hash_password(current_password) == password_hash:
        new_password = get_password(h//2 + 2, w//2 - 10, "New Password", 20)
        if new_password is None:  # User pressed ESC
            stdscr.addstr(h//2 + 5, w//2 - 10, "Operation aborted!     ")
            stdscr.refresh()
            return
        password_hash = hash_password(new_password)
        save_secrets()
        stdscr.addstr(h//2 + 4, w//2 - 10, "Password changed successfully!")
    else:
        stdscr.addstr(h//2 + 4, w//2 - 10, "Invalid current password!")

    stdscr.refresh()
    stdscr.getch()

# Function for the "About" section
def about(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    about_text = ["About", "=====", " ", "AUTHterm", "Version 1.0", "Developer: wessdvp", "License: CC BY"]
    for i, line in enumerate(about_text):
        stdscr.addstr(h//2 + i, (w - len(line)) // 2, line)
    stdscr.addstr(h//2 + len(about_text) + 2, (w - len("[Any key] Return to main menu")) // 2, "[Any key] Return to main menu")
    stdscr.refresh()
    stdscr.getch()

# Function for the "Help" section
def help_menu(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    help_text = [
        "Help",
        "====",
        "1. Create Secret: Add a new secret to your vault.",
        "2. Edit Secret: Modify an existing secret.",
        "3. List Secrets: View all stored secrets.",
        "4. Delete Secret: Delete an existing secret.",
        "5. Change Password: Update your vault password.",
        "6. About: Information about the application.",
        "7. Help: Display this help menu.",
        "8. Exit: Close the application."
    ]

    # Pagination variables
    total_items = len(help_text) - 2  # Exclude title and separator
    total_pages = total_items  # One item per page
    current_page = 0

    while True:
        stdscr.clear()

        # Display the title and current help item
        stdscr.addstr(1, (w - len(help_text[0])) // 2, help_text[0])  # Title
        stdscr.addstr(2, (w - len(help_text[1])) // 2, help_text[1])  # Separator

        # Display the current help item
        if current_page < total_items:
            stdscr.addstr(h // 2, (w - len(help_text[current_page + 2])) // 2, help_text[current_page + 2])

        # Navigation prompt
        stdscr.addstr(h - 2, (w - len("[Left] Previous [Right] Next [Enter] Return to main menu")) // 2,
                      "[Left] Previous [Right] Next [Enter] Return to main menu")
        
        stdscr.refresh()
        
        key = stdscr.getch()

        if key == curses.KEY_RIGHT and current_page < total_pages - 1:
            current_page += 1  # Next page
        elif key == curses.KEY_LEFT and current_page > 0:
            current_page -= 1  # Previous page
        elif key == 10:  # Enter key
            break  # Exit the help menu

#ft to check base32
def is_base32(secret_value):
    base32_regex = r'^[A-Z2-7]+=*$'  # Regex to match Base32 encoding
    return bool(re.match(base32_regex, secret_value))

# Function to create a secret
def create_secret(stdscr):
    global secrets  # Assuming secrets is defined somewhere globally
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    stdscr.addstr(h//2 - 1, w//2 - 10, "Enter secret name: ")
    stdscr.addstr(h//2 + 4, w//2 - 10, "[ESC] Return to the main menu")
    stdscr.refresh()
    curses.echo()
    secret_name = ""

    # Loop to get secret name, allowing ESC to quit
    while True:
        # Clear the area where secret name will be displayed before re-drawing it
        stdscr.move(h//2, w//2 - 10)
        stdscr.clrtoeol()  # Clear to the end of the line
        stdscr.addstr(h//2, w//2 - 10, secret_name)  # Display the current input
        stdscr.refresh()

        ch = stdscr.getch()

        if ch == 27:  # ESC key
            stdscr.addstr(h//2 + 5, w//2 - 10, "Operation aborted!")
            stdscr.refresh()
            return  # Return to the main menu
        elif ch in range(32, 127):  # Only allow printable characters
            secret_name += chr(ch)
        elif ch == curses.KEY_BACKSPACE or ch in [127, 8]:  # Handle backspace for different key codes
            if secret_name:
                secret_name = secret_name[:-1]  # Remove last character
        elif ch == curses.KEY_ENTER or ch in [10, 13]:  # Enter key
            break

    stdscr.addstr(h//2 + 1, w//2 - 10, "Enter secret value (Base32): ")
    stdscr.addstr(h//2 + 4, w//2 - 10, "[ESC] Return to the main")
    stdscr.refresh()
    secret_value = ""

    # Loop to get secret value, allowing ESC to quit
    while True:
        # Clear the area where secret value will be displayed before re-drawing it
        stdscr.move(h//2 + 2, w//2 - 10)
        stdscr.clrtoeol()  # Clear to the end of the line
        stdscr.addstr(h//2 + 2, w//2 - 10, secret_value)  # Display the current input
        stdscr.refresh()

        ch = stdscr.getch()

        if ch == 27:  # ESC key
            stdscr.addstr(h//2 + 5, w//2 - 10, "Operation aborted!")
            stdscr.refresh()
            return  # Return to the main menu
        elif ch in range(32, 127):  # Only allow printable characters
            secret_value += chr(ch)
        elif ch == curses.KEY_BACKSPACE or ch in [127, 8]:  # Handle backspace for different key codes
            if secret_value:
                secret_value = secret_value[:-1]  # Remove last character
        elif ch == curses.KEY_ENTER or ch in [10, 13]:  # Enter key
            break

    # Check if the secret value is in valid Base32 format
    if not is_base32(secret_value):
        stdscr.addstr(h//2 + 4, w//2 - 10, "Error: Secret value must be Base32!")
        stdscr.refresh()
        stdscr.getch()  # Wait for user input
        return  # Exit the function early if not valid

    secrets[secret_name] = secret_value
    save_secrets()
    stdscr.addstr(h//2 + 3, w//2 - 10, "Secret created successfully!")
    stdscr.refresh()
    stdscr.getch()

# Function to edit a secret
def edit_secret(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    if not secrets:
        stdscr.addstr(h // 2, w // 2 - 10, "No secrets available!")
        stdscr.refresh()
        stdscr.getch()
        return

    secrets_list = list(secrets.keys())
    selected_index = 0

    while True:
        stdscr.clear()
        stdscr.addstr(h // 2 - 1, w // 2 - 10, "[Enter] Edit Secret [x] Return to main menu")
        for i, secret_name in enumerate(secrets_list):
            if i == selected_index:
                stdscr.addstr(h // 2 + i, w // 2 - 10, secret_name, curses.A_REVERSE)
            else:
                stdscr.addstr(h // 2 + i, w // 2 - 10, secret_name)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and selected_index > 0:
            selected_index -= 1
        elif key == curses.KEY_DOWN and selected_index < len(secrets_list) - 1:
            selected_index += 1
        elif key in [curses.KEY_ENTER, 10, 13]:  # Enter key
            old_secret_name = secrets_list[selected_index]
            old_secret_value = secrets[old_secret_name]

            stdscr.addstr(h // 2 + len(secrets_list) + 1, w // 2 - 10, "Enter new name (leave empty to keep it): ")
            stdscr.refresh()
            curses.echo()
            new_secret_name = stdscr.getstr(h // 2 + len(secrets_list) + 2, w // 2 - 10, 20).decode('utf-8')

            while True:
                stdscr.addstr(h // 2 + len(secrets_list) + 3, w // 2 - 10, "Enter new value (leave empty to keep it): ")
                stdscr.refresh()
                stdscr.addstr(h // 2 + len(secrets_list) + 4, w // 2 - 10, " " * 20)  # Clear previous input
                stdscr.refresh()
                new_secret_value = stdscr.getstr(h // 2 + len(secrets_list) + 4, w // 2 - 10, 20).decode('utf-8')

                # Clear the line for previous error messages
                error_line = h // 2 + len(secrets_list) + 5
                stdscr.addstr(error_line, w // 2 - 10, " " * 60)  # Clear error line

                # Check if the new value is valid Base32
                if new_secret_value and not is_base32(new_secret_value):
                    stdscr.addstr(error_line, w // 2 - 10, "Base32 error! [x] go back [Enter] try again")
                    stdscr.refresh()

                    key = stdscr.getch()
                    if key == ord('x') or key == ord('X'):
                        stdscr.addstr(error_line, w // 2 - 10, " " * 60)  # Clear error message
                        break  # Go back to the secrets list
                    elif key in [curses.KEY_ENTER, 10, 13]:
                        stdscr.addstr(error_line, w // 2 - 10, " " * 60)  # Clear error message
                        continue  # Retry input

                # If the input is valid or empty, exit the loop
                break 

            # If the user pressed 'x', just return to the main edit interface
            if key == ord('x') or key == ord('X'):
                stdscr.addstr(error_line, w // 2 - 10, " " * 60)  # Clear error message
                continue

            # Only update the secret if valid input was provided
            updated = False  # Flag to track if an update was made
            if new_secret_name or new_secret_value:  # If a new name or value is provided
                if new_secret_name:  # If a new name is provided
                    secrets[new_secret_name] = secrets.pop(old_secret_name)  # Rename
                    updated = True
                if new_secret_value:  # If a new value is provided
                    secrets[new_secret_name if new_secret_name else old_secret_name] = new_secret_value  # Update value
                    updated = True

            if updated:
                save_secrets()
                stdscr.addstr(h // 2 + len(secrets_list) + 6, w // 2 - 10, "Secret updated successfully! Click [Enter]")
                stdscr.refresh()
                stdscr.getch()  # Wait for user to acknowledge success
                return  # Return to the main menu after success
                
            continue  # Return to the secrets list for further actions
        
        elif key == ord('x') or key == ord('X'):
            # If 'x' is pressed in the main editing loop, return to the main menu
            return  # Exit this function to go back to the main menu

    stdscr.clear()  # Clear the screen before returning

# Function to delete a secret
def delete_secret(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    # Check if the secrets list is empty
    if not secrets:
        stdscr.addstr(h//2 - 1, w//2 - 10, "No secrets available.")
        stdscr.refresh()
        stdscr.getch()
        return  # Exit the function if there are no secrets

    stdscr.addstr(h//2 - 1, w//2 - 10, "Select secret to delete:")
    stdscr.addstr(h//2 + len(secrets) + 3, w//2 - 30, "[Enter] Delete Secret, [Any button] Return to main menu")
    stdscr.refresh()

    secrets_list = list(secrets.keys())
    selected_secret_index = 0

    while True:
        for i, secret_name in enumerate(secrets_list):
            if i == selected_secret_index:
                stdscr.addstr(h//2 + i, w//2 - 10, secret_name, curses.A_REVERSE)
            else:
                stdscr.addstr(h//2 + i, w//2 - 10, secret_name)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and selected_secret_index > 0:
            selected_secret_index -= 1
        elif key == curses.KEY_DOWN and selected_secret_index < len(secrets_list) - 1:
            selected_secret_index += 1
        elif key in [curses.KEY_ENTER, 10, 13]:  # Enter key
            # Ask for confirmation before deleting
            confirm_msg = f"Are you sure you want to delete '{secrets_list[selected_secret_index]}'? (y/n): "
            stdscr.addstr(h//2 + len(secrets_list) + 1, w//2 - len(confirm_msg) // 2, confirm_msg)
            stdscr.refresh()

            confirmation = stdscr.getch()
            if confirmation in [ord('y'), ord('Y')]:  # If user confirms
                del secrets[secrets_list[selected_secret_index]]
                save_secrets()
                stdscr.addstr(h//2 + len(secrets_list) + 2, w//2 - 10, "Secret deleted successfully!")
            else:
                stdscr.addstr(h//2 + len(secrets_list) + 2, w//2 - 10, "Deletion canceled.")
            
            stdscr.refresh()
            stdscr.getch()
            break  # Exit the loop after deletion or cancellation
        elif key == ord ('x') or ord('X'):  # Check for 'x' key to exit
            break  # Exit the loop if 'x' is pressed

# Function to list and view secrets
def list_secrets(stdscr):
    while True:
        stdscr.clear()  # Clear screen to avoid glitches
        h, w = stdscr.getmaxyx()

        # List secrets
        stdscr.addstr(h // 2 - 2, w // 2 - 10, "Available Secrets:")

        if not secrets:
            stdscr.addstr(h // 2, w // 2 - 10, "No secrets available.")
            stdscr.refresh()
            stdscr.getch()
            return  # Exit the function after displaying the message

        secret_names = list(secrets.keys())
        selected_secret = 0

        while True:
            stdscr.clear()  # Ensure the screen is cleared on each iteration
            for i, secret_name in enumerate(secret_names):
                if i == selected_secret:
                    stdscr.addstr(h // 2 + i, w // 2 - 10, f"{i + 1}. {secret_name}", curses.A_REVERSE)
                else:
                    stdscr.addstr(h // 2 + i, w // 2 - 10, f"{i + 1}. {secret_name}")

            stdscr.addstr(h // 2 + len(secret_names) + 2, w // 2 - 10, "[Enter] See code [Any button] Return to main menu")
            stdscr.refresh()
            

            key = stdscr.getch()
            if key == curses.KEY_UP and selected_secret > 0:
                selected_secret -= 1
            elif key == curses.KEY_DOWN and selected_secret < len(secret_names) - 1:
                selected_secret += 1
            elif key in (curses.KEY_ENTER, 10, 13):  # Enter key
                secret_name = secret_names[selected_secret]
                show_code(stdscr, secret_name)
                break  # Return to the list of secrets after viewing code
            elif key == ord ('x') or ord('X'):
                return  # Exit listing and return to the main menu

# generate code ft
def generate_code(secret):
    """Generate a 6-digit numerical TOTP code."""
    totp = pyotp.TOTP(secret)
    return totp.now()  # Get current TOTP code

# timer gui ft
def draw_timer(stdscr, secret):
    # Clear the screen
    stdscr.clear()

    # Set up dimensions
    h, w = stdscr.getmaxyx()

    # Timer duration (30 seconds)
    duration = 30
    start_time = time.time()

    # Calculate the next code change time
    next_code_time = (start_time + duration) // duration * duration  # Align to the next 30s boundary

    while True:
        current_time = time.time()
        remaining = next_code_time - current_time  # Time remaining until next code change

        # Generate code
        code = generate_code(secret)

        # Display code and remaining time
        stdscr.addstr(h // 2 - 2, w // 2 - 10, f"Current Code: {code}")
        stdscr.addstr(h // 2, w // 2 - 10, f"Time remaining: {int(remaining)} seconds")

        # Modify the progress bar length (add 10 characters to the default length)
        bar_length = 30  # 20 + 10
        progress = int((remaining / duration) * bar_length)
        
        # Remove the square brackets and just print the bar
        stdscr.addstr(h // 2 - 1, w // 2 - 10, "█" * progress + "─" * (bar_length - progress))

        stdscr.addstr(h // 2 + 1, w // 2 - 10, "Press 'q' to return to the secrets list.")  # Instruction to quit
        stdscr.refresh()  # Refresh display to show updated timer

        # Check for user input in a non-blocking way
        stdscr.nodelay(True)  # Set getch to non-blocking
        key = stdscr.getch()
        if key == ord('q'):  # Check if 'q' is pressed
            stdscr.nodelay(False)  # Reset nodelay mode before exiting
            return  # Exit the loop and return to secrets list

        # Sleep briefly to control the refresh rate
        time.sleep(0.5)  # Adjust sleep time as needed

        # Reset timer when time has elapsed
        if remaining <= 0:
            start_time = current_time  # Reset start time
            next_code_time = (start_time + duration) // duration * duration  # Reset next code time to the next 30s boundary

# show code ft
def show_code(stdscr, secret_name):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Get the secret key
    secret = secrets[secret_name]

    # Show the code generation process
    stdscr.addstr(h // 2 - 2, w // 2 - 10, f"Secret: {secret_name}")

    draw_timer(stdscr, secret)  # Call the timer function to display timer and code

    stdscr.refresh()

# Main function
def main(stdscr):
    splash_screen(stdscr)
    load_secrets()

    if password_hash is None:
        setup_password(stdscr)
    else:
        verify_password(stdscr)

    main_menu(stdscr)

def exit_app(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h // 2 - 1, w // 2 - 10, "Thanks for using the app!")
    stdscr.addstr(h // 2, w // 2 - 10, "Press any key to exit...")
    stdscr.refresh()
    
    stdscr.getch()  # Wait for user input
    # Optionally, you can also perform any cleanup here before exiting
    exit(0)  # Exit the application


if __name__ == "__main__":
    curses.wrapper(main)
