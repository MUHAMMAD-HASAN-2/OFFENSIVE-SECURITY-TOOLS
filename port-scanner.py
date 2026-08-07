import socket
from concurrent.futures import ThreadPoolExecutor

# 1. IP addresses must be strings
target = input("Enter The IP Address you want to scan: ").strip()

# List of common ports to scan
ports = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 3389] 

def scan_and_grab(ip, port):
    """Checks if a port is open and attempts to grab its banner."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    
    try:
        # Check TCP connection (0 means success/open)
        result = sock.connect_ex((ip, port))
        
        if result == 0:
            # Try passive read first (SSH, FTP, etc.)
            banner = ""
            try:
                banner = sock.recv(1024).decode('utf-8', errors='replace').strip()
            except socket.timeout:
                pass

            # If no passive banner, send active probe (HTTP, etc.)
            if not banner:
                try:
                    probe = f"HEAD / HTTP/1.1\r\nHost: {ip}\r\n\r\n".encode('utf-8')
                    sock.send(probe)
                    banner = sock.recv(1024).decode('utf-8', errors='replace').strip()
                except Exception:
                    banner = "No banner response"

            clean_banner = banner.split('\n')[0] if banner else "No banner response"
            print(f"[+] Port {port:<5} OPEN  | Banner: {clean_banner}")
            
    except Exception as e:
        pass
    finally:
        sock.close()

# 2. Worker wrapper for executor.map (passes target IP along with each port)
def worker(port):
    scan_and_grab(target, port)

# 3. Thread pool execution over the defined ports list
print(f"\n[*] Scanning target {target} across {len(ports)} ports...\n")

with ThreadPoolExecutor(max_workers=50) as executor:
    # Pass the list directly to executor.map
    executor.map(worker, ports)

print("\n[*] Scan complete!")

