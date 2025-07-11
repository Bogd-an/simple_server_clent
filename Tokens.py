TOKEN = "dffgsdasdasdasddsasd"
URL = "ws://localhost:8000/ws"
KEY = b'm7kPegt3IzTJoUSnlL31cpHfY83tcSrKw7T5YXpTDb4='

if __name__ == '__main__':
    from cryptography.fernet import Fernet
    print(f'KEY = {Fernet.generate_key()}')