import asyncio
import websockets

from ..Message import Message, Cm
from ..Tokens import TOKEN

clients_websocket = []
clients_status    = []

async def handler(websocket):
    # Додаємо нового клієнта
    if websocket not in clients_websocket:
        clients_websocket.append(websocket)
        clients_status.append(True)
        clients_online = clients_status.count(True)
        print(f"[🔌] Клієнт підключився: {websocket.remote_address}, зараз {clients_online} клієнтів.")
        await websocket.send(Message.to_userID_crypt(str(websocket.remote_address)))
    try:
        async for message in websocket:
            msg, valid = Message.from_json_crypt(message)
            if not valid:
                print(f"[❗] Неправильне повідомлення від {websocket.remote_address}: {message}")
                continue
            print(f"[📥] Отримано від {websocket.remote_address}: {message}")

            # Розсилка всім, крім відправника
            for client_ws, client_status in zip(clients_websocket, clients_status):
                if not client_status:
                    clients_status[clients_websocket.index(client_ws)] = True
                if client_status: # and client_ws != websocket # Не надсилаємо повідомлення назад відправнику
                    await client_ws.send(message)
                    print(f"[📤] Надіслано до {client_ws.remote_address}: {message}")
    except websockets.ConnectionClosed:
        print(f"[❌] Клієнт відключився: {websocket.remote_address}")
    finally:
        clients_status[clients_websocket.index(websocket)] = False
        clients_online = clients_status.count(True)
        print(f"[ℹ️] Активних клієнтів: {clients_online}")

if __name__ == "__main__":
    async def main():
        async with websockets.serve(handler, "0.0.0.0", 8000):
            print("🚀 WebSocket сервер запущено на ws://0.0.0.0:8000")
            await asyncio.Future()  # тримай сервер активним

    asyncio.run(main())
