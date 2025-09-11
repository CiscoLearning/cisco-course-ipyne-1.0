import subprocess

def ping_device(ip_address):
    result = subprocess.run(["ping", "-c", "5", ip_address], capture_output=True, text=True)
    if "icmp_seq" in result.stdout:
        print(f"Device {ip_address} is reachable.")
    else:
        print(f"Device {ip_address} is NOT reachable.")

if __name__ == "__main__":
    ip_address = "10.0.0.103"  
    ping_device(ip_address)
