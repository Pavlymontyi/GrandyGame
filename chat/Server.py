# -*- coding: utf-8 - * -
import json
import socket
import sys
import threading
from chat import model

BUFFER_SIZE = 2 ** 10
CLOSING = "Application closing..."
CONNECTION_ABORTED = "Connection aborted"
CONNECTED_PATTERN = "Client connected: {}:{}"
ERROR_ARGUMENTS = "Provide port number as the first command line argument"
ERROR_OCCURRED = "Error Occurred"
EXIT = "exit"
JOIN_PATTERN = "{username} has joined"
RUNNING = "Server is running..."
SERVER = "SERVER"
SHUTDOWN_MESSAGE = "shutdown"
TYPE_EXIT = "Type 'exit' to exit>"





class Server(object):
    """A simple example of Server class"""  # Можно получить вызвав x.__doc__

    def __init__(self, argv):
        self.clients = set() # Клиентские сокеты
        self.listen_thread = None  # Тред, в котором крутимся и ждем подключений от клиентов. Порождаем клиентские сокеты при подключении
        self.port = None # Порт, проставляется при парсинге входящий параметров
        self.sock = None  # Серверный сокет - умеет принимать соединения от клиентов, порождая клиентский сокет
        self.parse_args(argv)

    def listen(self):
        # socket. listen ( [ backlog ] )
        # Enable a server to accept connections. If backlog is specified, it must be at least 0 (if it is lower, it is set to 0);
        # it specifies the number of unaccepted connections that the system will allow before refusing new connections.
        # If not specified, a default reasonable value is chosen.
        # Changed in version 3.5: The backlog parameter is now optional.
        self.sock.listen(1)
        while True:
            try:
                # Accept a connection. The socket must be bound to an address and listening for connections.
                # The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data on the connection,
                # and address is the address bound to the socket on the other end of the connection.
                # The newly created socket is non-inheritable.
                client, address = self.sock.accept()
            except OSError:
                print(CONNECTION_ABORTED)
                return
            print(CONNECTED_PATTERN.format(*address))
            self.clients.add(client)
            # Запускаем поток на обработку конкретного клиентского соединения
            threading.Thread(target=self.handle, args=(client,)).start()

    # Принимает сообщения от конкретного клиента
    def handle(self, client):
        while True:
            try:
                message = model.Message(**json.loads(self.receive(client)))
            except (ConnectionAbortedError, ConnectionResetError):
                print(CONNECTION_ABORTED)
                return
            if message.quit:
                # Получили сообщение на отключение клиента - отключаем клиента
                client.close()
                self.clients.remove(client)
                return
            print(str(message))
            # if SHUTDOWN_MESSAGE.lower() == message.message.lower():
            #     self.exit()
            #     return
            if not self.validate(message.message):
                #todo: добавить обработку ситуации когда невалидное сообщение
                print('asd')
            message.message.split(' ')

            self.broadcast(message)

    def validate(self, message):
        return True

    def broadcast(self, message):
        for client in self.clients:
            client.sendall(message.marshal())

    def receive(self, client):
        buffer = ""
        while not buffer.endswith(model.END_CHARACTER):
            buffer += client.recv(BUFFER_SIZE).decode(model.TARGET_ENCODING)
        return buffer[:-1]

    def run(self):
        print(RUNNING)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("", self.port))
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()

    def parse_args(self, argv):
        if len(argv) != 2:
            raise RuntimeError(ERROR_ARGUMENTS)
        try:
            self.port = int(argv[1])
        except ValueError:
            raise RuntimeError(ERROR_ARGUMENTS)

    # Тушим сервер
    def exit(self):
        self.sock.close()
        for client in self.clients:
            client.close()
        print(CLOSING)

if __name__ == "__main__":
    try:
        Server(sys.argv).run()
    except RuntimeError as error:
        print(ERROR_OCCURRED)
        print(str(error))