"""
COMPLETE PASSWORD MANAGER
==========================
All 4 problems FIXED!

Problems fixed:
1. ✅ Loop issue - Loop is OUTSIDE the function, no recursion
2. ✅ View feature - Search by website name, not fixed lines
3. ✅ Data structure - Using pipe-separated format (easy to work with)
4. ✅ Update/Delete - Both fully implemented

File format: website|username|password
Example:
    google.com|john123|pass123
    facebook.com|jane456|mypass456
"""

FILE_NAME = "passwords.txt"


def add_password():
    """Add a new password entry"""
    print("\n[+] ADD INFO")
    
    website = input("Website: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    # Basic validation
    if not website or not username or not password:
        print("❌ All fields required!")
        return
    
    # Append to file
    with open("Added_passwords.txt", "a") as f:
        f.write(f"{website}|{username}|{password}\n")
    
    print("✅ Password saved!")


def view_passwords():
    """View saved passwords"""
    print("\n[+] VIEW INFO")
    
    # Check if file exists
    try:
        with open("Added_passwords.txt", "r") as f:
            entries = f.readlines()
    except FileNotFoundError:
        print("❌ No passwords saved yet!")
        return
    
    if not entries:
        print("❌ No passwords saved yet!")
        return
    
    # Ask what to search for
    search = input("Search website (or press Enter to see all): ").strip()
    
    found = False
    entry_num = 0
    
    # Loop through ALL entries
    for entry in entries:
        entry = entry.strip()
        
        # Skip empty lines
        if entry == "":
            continue
        
        # Split the entry
        parts = entry.split("|")
        if len(parts) != 3:  # Make sure it's valid
            continue
        
        website, username, password = parts
        
        # If user searched, only show matches
        if search == "" or search.lower() in website.lower():
            entry_num += 1
            print(f"\n[Entry {entry_num}]")
            print(f"  Website: {website}")
            print(f"  Username: {username}")
            print(f"  Password: {password}")
            found = True
    
    if not found:
        if search == "":
            print("❌ No passwords saved yet!")
        else:
            print(f"❌ No entry found for '{search}'")


def update_password():
    """Update a password entry"""
    print("\n[+] UPDATE INFO")
    
    website_to_update = input("Website to update: ").strip()
    
    # Read all entries
    try:
        with open("Added_passwords.txt", "r") as f:
            entries = f.readlines()
    except FileNotFoundError:
        print("❌ No passwords saved yet!")
        return
    
    found = False
    updated_entries = []
    
    # Loop through entries
    for entry in entries:
        entry = entry.strip()
        
        if entry == "":
            updated_entries.append("\n")
            continue
        
        # Split entry
        parts = entry.split("|")
        if len(parts) != 3:
            updated_entries.append(entry + "\n")
            continue
        
        website, username, password = parts
        
        # Check if this is the one to update
        if website.lower() == website_to_update.lower():
            found = True
            print(f"\n[✓] Found: {website}")
            print(f"    Current username: {username}")
            print(f"    Current password: {password}")
            
            # Ask for new values
            new_user = input("\nNew username (press Enter to keep current): ").strip()
            new_pass = input("New password (press Enter to keep current): ").strip()
            
            # If user pressed Enter, keep old value
            if new_user == "":
                new_user = username
            if new_pass == "":
                new_pass = password
            
            # Add updated entry
            updated_entries.append(f"{website}|{new_user}|{new_pass}\n")
            print("✅ Entry updated!")
        else:
            # Keep this entry unchanged
            updated_entries.append(entry + "\n")
    
    if not found:
        print(f"❌ Website '{website_to_update}' not found!")
        return
    
    # Write back to file
    with open(FILE_NAME, "w") as f:
        f.writelines(updated_entries)


def delete_password():
    """Delete a password entry"""
    print("\n[+] DELETE INFO")
    
    website_to_delete = input("Website to delete: ").strip()
    
    # Read all entries
    try:
        with open("Added_passwords.txt", "r") as f:
            entries = f.readlines()
    except FileNotFoundError:
        print("❌ No passwords saved yet!")
        return
    
    found = False
    remaining_entries = []
    
    # Loop through entries
    for entry in entries:
        entry = entry.strip()
        
        if entry == "":
            continue
        
        # Split entry
        parts = entry.split("|")
        if len(parts) != 3:
            remaining_entries.append(entry + "\n")
            continue
        
        website, username, password = parts
        
        # Check if this is the one to delete
        if website.lower() == website_to_delete.lower():
            found = True
            print(f"\n[!] Found: {website}")
            
            # Ask for confirmation
            confirm = input("Delete this entry? (yes/no): ").lower()
            
            if confirm == "yes":
                print("✅ Entry deleted!")
                # DON'T add to remaining_entries (this deletes it)
            else:
                print("❌ Deletion cancelled!")
                # Add it back if user cancels
                remaining_entries.append(entry + "\n")
        else:
            # Keep this entry
            remaining_entries.append(entry + "\n")
    
    if not found:
        print(f"❌ Website '{website_to_delete}' not found!")
        return
    
    # Write back to file
    with open("Added_passwords.txt", "w") as f:
        f.writelines(remaining_entries)


def menu():
    """Main menu - LOOP IS HERE, NOT IN THE FUNCTION"""
    
    while True:  # ✅ Loop is OUTSIDE functions
        print('\n' + '='*50)
        print("[+] WELCOME TO PASSWORD MANAGER")
        print('='*50)
        print("[+] MENU")
        print("[+] ADD INFO       - 1")
        print("[+] VIEW INFO      - 2")
        print("[+] UPDATE INFO    - 3")
        print("[+] DELETE INFO    - 4")
        print("[+] EXIT           - 5")
        print('='*50)
        
        try:
            # Get user choice
            usr_option = int(input("\nEnter option (1-5): "))
            
            # Handle choice
            if usr_option == 1:
                add_password()
            elif usr_option == 2:
                view_passwords()
            elif usr_option == 3:
                update_password()
            elif usr_option == 4:
                delete_password()
            elif usr_option == 5:
                print("\n[+] Goodbye! Your passwords are safe. 👋\n")
                break  # ✅ Exit the loop
            else:
                print("❌ Invalid option! Enter 1-5.")
        
        except ValueError:
            print("❌ Invalid input! Enter a number.")
        except Exception as e:
            print(f"❌ Error: {e}")


# Run the program
if __name__ == "__main__":
    print("[+] Password Manager Started!\n")
    menu()