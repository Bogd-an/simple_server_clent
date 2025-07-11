#client.py
import asyncio
from ..Message import Message

class UDPServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, handler):
        self.message_handler = handler
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):  
        self.transport.sendto(
            self.message_handler(data, addr), addr
        )

async def loop_listener(handler, LISTEN_PORT=1234):
    print("Запускаємо асинхронного UDP клієнта...")

    transport, protocol = await asyncio.get_running_loop(
        ).create_datagram_endpoint(
            lambda: UDPServerProtocol(handler),
            local_addr=('0.0.0.0', LISTEN_PORT)
        )

    while True: await asyncio.sleep(1)  # Залишаємо сервер працювати

if __name__ == "__main__":
    def message_handler(data:bytes, addr):
        mess, valid = Message.loads_c(data)
        if valid:
            print(f"<- {addr[0]}:{addr[1]}: decode {mess}")
            answer = Message.new(text='decode ok', userID=addr)
            print(f"-> : {answer.dumps()}")
            return answer.dumps_c()
        else:
            print(f"<- {addr[0]}:{addr[1]}: {data.decode()}")
            print(f"-> : decode error")
            return 'decode error'.encode()
    
    asyncio.run(loop_listener(message_handler))
