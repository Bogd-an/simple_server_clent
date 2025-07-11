# ws_singleton.py
from websocket import create_connection, WebSocket
import threading
from ..Message import Message
from ..Tokens import URL

class WebSocketClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(WebSocketClient, cls).__new__(cls)
                cls._instance._url = URL
                cls._instance._ws: WebSocket | None = None # type: ignore
                cls._instance._connected = False
                cls._instance._receive_thread = None
                cls._instance.on_message = lambda msg: print("<- ", msg)  # за замовчуванням
        return cls._instance

    def connect(self):
        if not self._connected:
            self._ws = create_connection(self._url)
            self._connected = True
            self._start_receiving()
        return self._connected
    
    def send(self, msg: str):
        # print("-> ", msg)
        self._ws.send(msg)

    def _start_receiving(self):
        def _loop():
            while self._connected:
                try:
                    msg = self._ws.recv()
                    self.on_message(msg)
                except Exception:
                    self._connected = False
                    break
        self._receive_thread = threading.Thread(target=_loop, daemon=True)
        self._receive_thread.start()

    def close(self):
        if self._connected:
            self._connected = False
            self._ws.close()


if __name__ == "__main__":
    import time

    def receive(msg):
        m, v = Message.from_json_crypt(msg)
        if not v: return
        print('<-', m)

    def send(msg):
        print("-> ", msg)
        ws.send(msg)

    print("Підключення до WebSocket сервера ")
    ws = WebSocketClient()
    ws.on_message = receive
    ws.connect()

    while True: time.sleep(1)