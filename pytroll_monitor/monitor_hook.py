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

MODE = os.getenv("SMHI_MODE")
if MODE is None:
    MODE = "offline"


class OP5Monitor(object):
    """A class to trigger the sending of a notifcation to the SMHI monitor server."""

    def __init__(self, monitor_auth, monitor_service, monitor_server, monitor_host):
        """Init the monitor."""
        # __init__ is not run when created from yaml
        # See http://pyyaml.org/ticket/48
        self.monitor_auth = monitor_auth
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
        self.monitor_auth = mydict['monitor_auth']
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
        api_command = urljoin(self.monitor_server, '/api/command/PROCESS_SERVICE_CHECK_RESULT')
        # LOG.debug("API command: <%s>", api_command)
        # LOG.debug("monitor host: %s", self.monitor_host)
        # LOG.debug("monitor service: %s", self.monitor_service)
        # LOG.debug("status code: %d", status)
        # LOG.debug("Message: %s", msg)
        jsondata = json.dumps({"host_name": self.monitor_host,
                               "service_description": self.monitor_service,
                               "status_code": status,
                               "plugin_output": msg})
        retv = requests.post(api_command,
                             headers={'content-type': 'application/json'},
                             auth=tuple(self.monitor_auth),
                             data=jsondata)
        return retv
