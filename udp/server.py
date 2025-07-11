# server.py
import asyncio
import socket
import sys

BROADCAST_IP = '255.255.255.255'
PORT = 1234
from ..Message import Message

async def send_and_receive(message, timeout=5, port=PORT, message_decoder=lambda x: x):
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.get_running_loop()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setblocking(False)
    sock.bind(('', 0))  # Прив'язка до будь-якого вільного порту

    print(f"->: {message}")
    sock.sendto(message.encode(), (BROADCAST_IP, port))

    end_time = loop.time() + timeout
    try:
        while True:
            remaining = end_time - loop.time()
            if remaining <= 0: break
            # Чекаємо відповідь з використанням recv замість recvfrom
            data = await asyncio.wait_for(loop.sock_recv(sock, 1024), timeout=remaining)
            print(message_decoder(data))
    except asyncio.TimeoutError:
        print("⏱️ Таймаут: більше немає відповідей.")
    finally:
        sock.close()

if __name__ == "__main__":
    def decoder(data:bytes):
        mess, valid = Message.loads_c(data)
        if valid:
            print(f"<- : decode {mess}")
        else:
            print(f"<- : {data.decode()}")

    asyncio.run(send_and_receive(
            Message.new(text="hello from server", userID='server'),
            message_decoder=decoder
        ))
