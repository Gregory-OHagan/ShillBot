
import socket
import threading
import json

import settings


class MothershipServer(object):

    host = ''
    port = None
    sock = None

    buff_size = None

    def __init__(self):
        self.host = settings.MOTHERSHIP.get('host', 'localhost')
        self.port = settings.MOTHERSHIP.get('port', 8080)
        self.buff_size = settings.BUFFER_SIZE

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def run(self):

        print('Starting Mothership.')

        self.sock.listen(5)
        print('Mother is listening...')
        while True:
            worker, address = self.sock.accept()
            worker.settimeout(60)
            print('Connection Received: %s' % str(address))
            threading.Thread(target=self.handle_worker_contact, args=(worker, address)).start()

    def handle_worker_contact(self, worker, address):
        while True:
            try:
                data = worker.recv(self.buff_size)
                if data:
                    json_data = json.loads(data)
                    print('%s' % json_data)
                else:
                    raise ValueError('No Value Given')
            except:
                worker.close()
                return False







