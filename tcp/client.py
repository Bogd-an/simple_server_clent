import requests
from ..Message import Message, Cmd
import socket
from concurrent.futures import ThreadPoolExecutor

import getpass
WINDOWS_NAME = getpass.getuser()

SERVER_NAME = 'client_' + WINDOWS_NAME

PORT = 5000
TIMEOUT = 0.5  # timeout для запитів



def scan_network(port=5000) -> str:
    """Сканує локальну мережу для пошуку сервера"""

    def get_local_subnet():
        """Отримати локальну IP і підмережу /24"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Підключаємось до "зовнішнього" адреса, щоб дізнатись свій IP (не відправляємо дані)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = "127.0.0.1"
        finally:
            s.close()

        # Визначаємо підмережу, обрізаючи останній октет IP
        subnet_parts = local_ip.split('.')
        subnet = '.'.join(subnet_parts[:3]) + '.'
        return subnet

    def check_server(ip):
        url = f'http://{ip}:{port}/message'
        test_msg = Message.new(userID=SERVER_NAME, cmd=Cmd.HANDSHAKE).dumps_c()
        try:
            response = requests.post(url, data=test_msg, timeout=TIMEOUT)
            if response.status_code == 200:
                resp_msg, valid = Message.loads_c(response.content)
                if valid:
                    # print(f"Server found at {ip}")
                    return (ip, resp_msg.userID)
        except Exception:
            return None
    

    subnet = get_local_subnet()

    print(f"Scanning local network for server: {subnet}0/24")
    ips = [f"{subnet}{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(check_server, ips)
    results = [result for result in results if result is not None]
    print("Scan complete = ", results)
    return results

def send_message(server_ip, **messageArgs):
    url = f'http://{server_ip}:{PORT}/message'
    
    msg = Message.new(**messageArgs)
    msg.userID = SERVER_NAME
    print(f"->: {msg}")

    response = requests.post(url, data=msg.dumps_c())
    
    resp_msg = valid = False 
    if response.status_code == 200:
        resp_msg, valid = Message.loads_c(response.content)
        if valid:
            print(f"<-: {resp_msg}")
        else:
            print("Invalid response from server")
    else:
        print(f"Error: {response.status_code} {response.text}")
        
    return resp_msg, valid

def main():
    servers = scan_network()
    if not servers: return
    
    server_ip, server_name = servers[0]
    
    # send_message(server_ip, userID='client', text=f'Hello, {server_name}')
    
    

if __name__ == "__main__":
    main()
