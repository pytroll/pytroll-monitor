#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2019

# Author(s):

#   Martin.Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""A logger sending statuses to monitor."""

import logging
from six.moves.urllib.parse import urlparse
import json
from threading import Thread
import sys
from socket import gaierror
from queue import Queue

logger = logging.getLogger(__name__)


class RequestOP5Handler(logging.Handler):
    """Monitoring handler."""

    def __init__(self, auth, service, server, host):
        """Init the handler."""
        from pytroll_monitor.monitor_hook import OP5Monitor
        logging.StreamHandler.__init__(self)
        self.auth = auth
        self.service = service
        self.server = server
        self.host = host
        self.monitor = OP5Monitor(auth, service, server, host)

    def emit(self, record):
        """Emit the message."""
        if record.levelno < logging.INFO:
            return
        if record.levelno >= logging.INFO:
            status = 0
        if record.levelno >= logging.WARNING:
            status = 1
        if record.levelno >= logging.ERROR:
            status = 2
        self.monitor.send_message(status, self.format(record))


class OP5Handler(logging.Handler):
    """Monitoring handler."""

    def __init__(self, auth, service, server, host):
        """Init the handler."""
        logging.Handler.__init__(self)

        self.auth = tuple(auth)
        self.service = service
        self.host = host
        self.server = server

    def emit(self, record):
        """Emit a record."""
        if record.levelno < logging.INFO:
            return
        if record.levelno >= logging.INFO:
            status = 0
        if record.levelno >= logging.WARNING:
            status = 1
        if record.levelno >= logging.ERROR:
            status = 2
        jsondata = json.dumps({"host_name": self.host,
                               "service_description": self.service,
                               "status_code": status,
                               "plugin_output": self.format(record)})

        try:
            import http.client
            url = urlparse(self.server)
            if url.scheme == 'https':
                h = http.client.HTTPSConnection(url.netloc)
            elif url.scheme == "http":
                h = http.client.HTTPConnection(url.netloc)
            else:
                raise NotImplementedError(
                    "Can't create an OP5 logger with scheme {}".format(
                        url.scheme))
            h.putrequest('POST', url.path)
            h.putheader("Content-type",
                        "application/json")
            h.putheader("Content-length", str(len(jsondata)))
            if self.auth:
                import base64
                s = ('%s:%s' % self.auth).encode('utf-8')
                s = 'Basic ' + base64.b64encode(s).strip().decode('ascii')
                h.putheader('Authorization', s)
            h.endheaders()
            h.send(jsondata.encode('utf-8'))
            h.getresponse()  # nothing to do with the result
        except gaierror:
            sys.stderr.write("Can't reach %s !\n" % url.netloc)
            self.handleError(record)
        except Exception:
            self.handleError(record)


class AsyncHandler():
    """Asynchronous logging handler."""

    def __init__(self, *args, **kwargs):
        """Init the asynchronous handler with a queue and a thread."""
        super().__init__(*args, **kwargs)
        self.__queue = Queue()
        self.__thread = Thread(target=self.__loop)
        self.__thread.daemon = True
        self.__thread.start()

    def emit(self, record):
        """Emit the record."""
        self.__queue.put(record)

    def __loop(self):
        """Loop over the records and emit."""
        while True:
            record = self.__queue.get()
            super().emit(record)


class AsyncOP5Handler(AsyncHandler, OP5Handler):
    """Async version of the OP5Handler."""

    pass
