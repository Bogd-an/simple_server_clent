from flask import Flask, request, Response
from ..Message import Message, Cmd

SERVER_NAME = 'server1'

app = Flask(__name__)

@app.route('/message', methods=['POST'])
def receive_message():
    try:
        encrypted_data = request.data
        msg, valid = Message.loads_c(encrypted_data)
        if not valid:
            response = Message.new(userID=SERVER_NAME, cmd=Cmd.ERROR, text='Invalid or corrupted message')
            return Response(response.dumps_c(), status=400, content_type='application/octet-stream')
        
        print(f"Received from {request.remote_addr}: {msg}")
        
        if msg.cmd == Cmd.HANDSHAKE:
            response = Message.new(userID=SERVER_NAME, cmd=Cmd.HANDSHAKE, text='Hello from server!')
        else:
            response = Message.new(userID=SERVER_NAME, cmd=Cmd.ERROR, text='Unknown command')
        
        return Response(response.dumps_c(), content_type='application/octet-stream')
    
    except Exception as e:
        print(f"Error: {e}")
        response = Message.new(userID=SERVER_NAME, cmd=Cmd.ERROR, text='Internal server error')
        return Response(response.dumps_c(), status=500, content_type='application/octet-stream')

if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
