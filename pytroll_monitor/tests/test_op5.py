#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pytroll_monitor.monitor_hook import OP5Monitor
from pytroll_monitor.op5_logger import OP5Handler
import yaml
import logging
import logging.config
import requests_mock


yaml_config = """version: 1
disable_existing_loggers: false
formatters:
  pytroll:
    format: '[%(asctime)s %(levelname)-8s %(name)s] %(message)s'
handlers:
  monitor:
    (): pytroll_monitor.op5_logger.OP5Handler
    auth: ['username', 'password']
    service: that_service_we_should_monitor
    server: http://myop5server.com/some/service
    host: server_we_run_stuff_on
root:
  level: DEBUG
  handlers: [monitor]
"""


class TestOp5Interfaces:
    """Test the Op5 monitor and handler."""
    def setup(self):
        self.service = "that_service_we_should_monitor"
        self.server = "http://myop5server.com/some/service"
        self.auth = ("username", "password")
        self.host = "server_we_run_stuff_on"
        self.message = "I didn't expect a kind of Spanish Inquisition."
        self.response_text = "Nobody expects the Spanish Inquisition!"
        self.status = 1

        self.expected_json = {"host_name": self.host,
                              "service_description": self.service,
                              "status_code": self.status,
                              "plugin_output": self.message}
        self.expected_auth = 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='

    def test_op5monitor_without_auth(self):
        """Test the monitor without authentication."""

        op5m = OP5Monitor(self.service, self.server, self.host, monitor_auth=None)

        with requests_mock.Mocker() as m:
            m.post(self.server, text=self.response_text)
            op5m.send_message(self.status, self.message)
            assert m.last_request.json() == self.expected_json
            assert m.last_request.url == self.server
            assert m.last_request.method == "POST"
            assert "Authorization" not in m.last_request.headers

    def test_op5monitor_with_auth(self):
        """Test the monitor with authentication."""
        op5m = OP5Monitor(self.service, self.server, self.host, self.auth)

        with requests_mock.Mocker() as m:
            m.post(self.server, text=self.response_text)
            op5m.send_message(self.status, self.message)
            assert m.last_request.headers["Authorization"] == self.expected_auth

    def test_op5handler(self):
        logger = logging.getLogger("test_loggin")

        log_dict = yaml.safe_load(yaml_config)
        logging.config.dictConfig(log_dict)

        with requests_mock.Mocker() as m:
            m.post(self.server, text=self.response_text)
            logger.warning(self.message)
            assert m.last_request.json() == self.expected_json
            assert m.last_request.headers["Authorization"] == self.expected_auth
