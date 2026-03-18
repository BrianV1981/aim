#!/home/kingb/aim/venv/bin/python3
import keyring
import getpass
import sys

def main():
    print("--- A.I.M. Secret Management Utility ---")
    
    # Check keyring backend
    kb = keyring.get_keyring()
    print(f"Active Backend: {kb.name}")
    
    if "Plaintext" in kb.name:
        print("WARNING: Using a plaintext backend. Secrets will be stored unencrypted.")
        print("For better security, install 'libsecret-1-0' and 'python3-secretstorage'.\n")
    else:
        print("Status: Secure backend detected.\n")

    print("This script will store your GOOGLE_API_KEY in the local keyring.")
    
    try:
        key = getpass.getpass("Enter your GOOGLE_API_KEY: ")
        if not key:
            print("Error: Key cannot be empty.")
            sys.exit(1)
            
        keyring.set_password("aim-system", "google-api-key", key)
        print("\nSuccess! Key stored in keyring under 'aim-system:google-api-key'.")
        print("You can now safely remove the GOOGLE_API_KEY export from your .bashrc.")
        
    except Exception as e:
        print(f"\nFailed to store key: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
