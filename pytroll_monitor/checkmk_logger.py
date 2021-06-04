#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2021

# Author(s):

#   Gerrit Holl <gerrit.holl@dwd.de>

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

"""Logger to report status to checkmk local checks.

This module contains a logging handler that will gather information based on
logging messages and report the status to a checkmk local check file.  It is
still a work in progress.  So far it just writes a single line to the indicated
status_line, and the only thing that changes is the initial digit, where 0 =
OK, 1 = WARN, 2 = CRIT, and 3 = UNKNOWN.  Status starts at unknown.  When a
message is logged with level warn, status is set to warn.  When a message is
logged with level error or critical, status is set to critical.  When the
message "All n files produced nominally" for n>0 is logged, status is set to
OK.

For more information on checkmk local checks, see
https://docs.checkmk.com/latest/en/localchecks.html

An example logging config illustrating how to use this::

    version: 1
    disable_existing_loggers: false
    formatters:
      pytroll:
        format: '[%(asctime)s %(levelname)-8s %(name)s] %(message)s'
    handlers:
      console:
        class: logging.StreamHandler
        level: DEBUG
        formatter: pytroll
        stream: ext://sys.stdout
      monitor:
        (): pytroll_monitor.checkmk_logger.Trollflow2CheckMKHandler
        level: DEBUG
        formatter: pytroll
        status_file: /opt/pytroll/pytroll_inst/pytroll_status
    root:
      level: DEBUG
      handlers:
        - console
        - monitor

Pass this to the logging config option for supported pytroll packages,
such as::

    satpy_launcher.py -n localhost trollflow2.yaml -c logging.yaml
"""

import logging

from enum import IntEnum


class ServiceStatus(IntEnum):
    """Service status according to checkmk local checks.

    Enumerate the service status according to checkmk local checks.
    """

    OK = 0
    WARN = 1
    CRIT = 2
    UNKNOWN = 3


class Trollflow2CheckMKHandler(logging.Handler):
    """Handler to report checkmk local for use with trollflow2.

    This handler abuses logging messages for a status report.  If any message
    is logged with level WARNING, it will set a checkmk status to WARN.  If any
    message is logged with a worse level, it will set a checkmk status to
    CRITICAL.  When trollflow2 reports that all files are produced nominally,
    it will set status to OK, unless the number is zero.
    """

    service_name = '"Pytroll status report"'

    def __init__(self, status_file):
        """Initialise the logger.

        The status_file should be the file where checkmk will check the status.
        """
        super().__init__()
        self.status_file = status_file
        self.status = ServiceStatus.UNKNOWN
        self.write_status_to_file()

    def emit(self, record):
        """Update the status based on the logging.

        Update the state based on the logging.  If a message is logged with
        level error or worse, set it to critical.  If logged with level
        warning, set it to warning.  If a message that all non-zero files are
        produced nominally is emitted, set it to all OK.  Update the status
        file if the status has changed.  Also update the status if all is still
        good, so the status does not become too old.
        """
        update = False
        stat = self.status
        if record.levelno >= logging.ERROR:
            stat = ServiceStatus.CRIT
        elif record.levelno >= logging.WARNING:
            stat = ServiceStatus.WARN
        elif record.levelno <= logging.INFO:
            if record.msg.startswith("All 0 files produced nominally"):
                stat = ServiceStatus.WARN
            elif "files produced nominally" in record.msg:
                stat = ServiceStatus.OK
                update = True
        if update or stat != self.status:  # status has changed, update file
            self.status = stat
            self.write_status_to_file()

    def get_status_line(self):
        """Get the checkmk status line.

        Format is defined at
        https://docs.checkmk.com/latest/en/localchecks.html
        """
        return (f"{self.status:d} {self.service_name:s} "
                "- Pytroll lives!")

    def write_status_to_file(self):
        """Update the status in the status file."""
        status_line = self.get_status_line()
        with open(self.status_file, "wt", encoding="ascii") as fp:
            fp.write(status_line)
