#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>

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

"""A generic OP5 post hook to be run to update the passive monitoring status."""

import os
import logging
import requests
import json
from six.moves.urllib.parse import urljoin

LOG = logging.getLogger(__name__)


class OP5Monitor(object):
    """A class to trigger the sending of a notification to an Op5 monitor server."""

    def __init__(self, monitor_service, monitor_server, monitor_host, monitor_auth=None):
        """Init the monitor."""
        self.monitor_auth = monitor_auth
        if self.monitor_auth:
            self.monitor_auth = tuple(monitor_auth)
        self.monitor_service = monitor_service
        self.monitor_server = monitor_server
        self.monitor_host = monitor_host

    def __getstate__(self):
        """Get state."""
        d__ = {'monitor_auth': self.monitor_auth,
               'monitor_service': self.monitor_service,
               'monitor_server': self.monitor_server,
               'monitor_host': self.monitor_host}
        return d__

    def __setstate__(self, mydict):
        """Set state."""
        monitor_auth = mydict.get('monitor_auth')
        if monitor_auth:
            self.monitor_auth = tuple(monitor_auth)
        self.monitor_service = mydict['monitor_service']
        self.monitor_server = mydict['monitor_server']
        self.monitor_host = mydict['monitor_host']

    def __call__(self, status, msg):
        """Call the hook and send a status."""
        LOG.debug("Service = %s", str(self.monitor_service))
        LOG.debug("Server = %s", str(self.monitor_server))
        LOG.debug("Host = %s", str(self.monitor_host))

        retv = self.send_message(status, msg)

        LOG.debug("Request done: %s", retv.text)

    def send_message(self, status, msg):
        """Send the message to the monitor server."""
        json_data = {"host_name": self.monitor_host,
                     "service_description": self.monitor_service,
                     "status_code": status,
                     "plugin_output": msg}
        with requests.post(self.monitor_server,
                           auth=self.monitor_auth,
                           json=json_data) as response:
            response.raise_for_status()
            return response
