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
import sys
from queue import Queue
from socket import gaierror
from threading import Thread

from pytroll_monitor.monitor_hook import OP5Monitor

logger = logging.getLogger(__name__)


class OP5Handler(logging.Handler):
    """Monitoring handler."""

    def __init__(self, service, server, host, auth=None):
        """Init the handler."""
        super().__init__()

        self.server = server
        self.monitor = OP5Monitor(service, server, host, auth)

    def emit(self, record):
        """Emit a record."""
        if record.levelno >= logging.ERROR:
            status = 2
        elif record.levelno >= logging.WARNING:
            status = 1
        elif record.levelno >= logging.INFO:
            status = 0
        else:
            return
        try:
            self.monitor.send_message(status, self.format(record))
        except gaierror:
            sys.stderr.write("Can't reach %s !\n" % self.server)
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
