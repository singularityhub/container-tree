#
# Copyright (C) 2018-2019 Vanessa Sochat.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import http.server
import socketserver
from random import choice
from threading import Thread
import os


def get_web_server(port=None):
    '''get_web_server returns a httpd object (socket server)

    Parameters
    ==========
    port: the port for the server, selected randomly if not defined

    '''
    if port == None:
        port = choice(range(2000,9999))

    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)
    server = Thread(target=httpd.serve_forever)
    server.setDaemon(True)
    server.start()
    return httpd,port


def serve_template(webroot, port=None):
    '''serve some folder with a simple httpserver'''

    os.chdir(webroot)
    httpd,port = get_web_server(port=port)
    print('Serving at localhost:%s' %port)
    httpd.serve_forever()
