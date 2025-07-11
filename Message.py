#Message.py

from dataclasses import dataclass, asdict
import dataclasses
import json
from datetime import datetime
from typing import Tuple

from Tokens import KEY

from cryptography.fernet import Fernet
fernet_key = Fernet(KEY)

import getpass
WINDOWS_NAME = getpass.getuser()


from enum import Enum

class Cmd(str, Enum):
    HANDSHAKE = 'handshake'
    PING = 'ping'
    ERROR = 'error'

@dataclass
class Message:
    """
    Клас для представлення повідомлення між клієнтом і сервером.

    Атрибути:
        userID (str): Ім'я користувача, який надіслав повідомлення.
        timestamp (str): Час створення повідомлення.
        text (str): Текст повідомлення.
        cmd (Cmd): Команда (наприклад, handshake, ping, error).
        args (str): Додаткові аргументи для команди.
    """

    userID: str = ''
    timestamp: str = ''
    text: str = ''
    cmd: Cmd = ''
    args: str = ''

    @staticmethod
    def loads_c(encrypted_bytes: bytes) -> Tuple['Message', bool]:
        """
        Декодує та розшифровує повідомлення з байтів.

        Args:
            encrypted_bytes (bytes): Зашифровані байти повідомлення.

        Returns:
            Tuple[Message, bool]: Об'єкт Message та ознака валідності.
        """
        try:
            return Message.loads(fernet_key.decrypt(encrypted_bytes).decode())
        except Exception as e:
            print(f"Error decrypting message: {e}")
            return Message(), False

    @staticmethod
    def loads(json_str: str) -> Tuple['Message', bool]:
        """
        Декодує повідомлення з JSON-стрічки.

        Args:
            json_str (str): JSON-стрічка повідомлення.

        Returns:
            Tuple[Message, bool]: Об'єкт Message та ознака валідності.
        """
        valid = False
        try:
            data = json.loads(json_str)
            fields = {f.name for f in dataclasses.fields(Message)}
            msg_data = {k: data[k] for k in data if k in fields}
            msg = Message(**msg_data)

            valid = True
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            msg = Message()
        return msg, valid

    @staticmethod
    def new(**data) -> 'Message':
        """
        Створює нове повідомлення з поточним часом та ім'ям користувача.

        Args:
            **data: Дані для ініціалізації атрибутів повідомлення.

        Returns:
            Message: Новий об'єкт Message.
        """
        m = Message(**{f: data.get(f, '') for f in asdict(Message())})
        m.timestamp = datetime.now().isoformat()
        m.userID = WINDOWS_NAME
        return m

    def __str__(self) -> str:
        """
        Повертає повідомлення у форматі JSON з відступами.

        Returns:
            str: JSON-представлення повідомлення.
        """
        return json.dumps(asdict(self), indent=4)
    
    def __repr__(self) -> str:
        """
        Повертає строкове представлення повідомлення.

        Returns:
            str: JSON-представлення повідомлення.
        """
        return self.__str__()

    def dumps(self) -> str:
        """
        Серіалізує повідомлення у JSON-стрічку.

        Returns:
            str: JSON-стрічка.
        """
        return json.dumps(asdict(self))

    def dumps_c(self) -> bytes:
        """
        Серіалізує та шифрує повідомлення.

        Returns:
            bytes: Зашифровані байти повідомлення.
        """
        return fernet_key.encrypt(self.dumps().encode())
    
    def encode(self) -> bytes:
        """
        Серіалізує та шифрує повідомлення (аналог dumps_c).

        Returns:
            bytes: Зашифровані
        """
        return self.dumps_c()

if __name__ == "__main__":
    print('\n тест повідомлення')

    m = Message.new()
    m.text = "test text"

    print('\n шифрування')
    crypt = m.dumps_c()
    print(crypt)

    print('\n рошифрування')
    m2, valid = Message.loads_c(crypt)
    print(m2)

    # for _ in range(100): print(Message.new().dumps_c())
