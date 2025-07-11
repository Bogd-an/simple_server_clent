# server_minimal.py

from http.server import HTTPServer, BaseHTTPRequestHandler
from ..Message import Message, Cmd
import getpass

SERVER_NAME = 'server_' + getpass.getuser()

class SimpleHandler(BaseHTTPRequestHandler):
    
    def answer_message(self, **args):
        args['userID'] = self.server_name
        response_msg = Message.new(**args)
        print(f"-> {self.address_string()}: {response_msg}")
        response_bytes = response_msg.dumps_c()
        self.answer(response_bytes, 200)
    
    def answer(self, response_bytes, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)
    
    def read_request(self):
        content_length = self.headers.get('Content-Length')
        if content_length is None: return b''
        return self.rfile.read(int(content_length))


class Handler(SimpleHandler):
    def __init__(self, *args, **kwargs):
        self.server_name = SERVER_NAME
        super().__init__(*args, **kwargs)

    def do_POST(self):
        try:
            if self.path != '/message':
                return self.answer_message(cmd=Cmd.ERROR, text='Invalid endpoint')
                        
            msg, valid = Message.loads_c(self.read_request())
            if not valid:
                return self.answer_message(cmd=Cmd.ERROR, text='Invalid or corrupted message')

            print(f"\n<- {self.address_string()}: {msg}")

            if msg.cmd == Cmd.HANDSHAKE:
                return self.answer_message(cmd=Cmd.HANDSHAKE)

            return self.answer_message(cmd=Cmd.ERROR, text='Unknown cmd')

        except Exception as e:
            self.answer_message(cmd=Cmd.ERROR, text='Internal server error')


def run_server(handler_class=Handler, port=5000):
    httpd = HTTPServer(('0.0.0.0', port), handler_class)
    print(f"Starting http server on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
