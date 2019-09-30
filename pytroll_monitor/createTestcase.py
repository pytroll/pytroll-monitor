# -*- coding: utf-8 -*-
import json
import requests

monitorHost = 'monitor-utvtst.smhi.se'
host_name = 'testHostSattelit'
service_description = 'testServiceSatellit'



def hostsToCreate(monitorHost, host_name):
    print 'Running hostsToCreate, status code:'
    host_payload = json.dumps(
        {"file_id": "etc/hosts.cfg",
         "host_name": host_name,
         "check_command": "check_dummy",
         "check_command_args": "0",
         "template": "default-host-template", })


    try:
        update = requests.post(
            'https://%s/api/config/host' % monitorHost,
            headers={'content-type': 'application/json'},
            data=host_payload)
    finally:
        print update.status_code

def hostsWithSevicesToCreate(monitorHost, host_name, service_description):
    print 'Running hostsWithSevicesToCreate, status code:'
    service_payload = json.dumps(
        {"file_id": "etc/services.cfg",
         "host_name": host_name,
         "service_description": service_description,
         "check_command": "check_dummy",
         "check_command_args": "2",
         "active_checks_enabled": "0",
         "check_freshness": "1",
         "freshness_threshold": "3600",
         "template": "default-service"})

    try:
        update = requests.post(
            'https://%s/api/config/service' % monitorHost,
            headers={'content-type': 'application/json'},
            data=service_payload)
    finally:
        print update.status_code


def save_config(monitorHost):

    print 'Saving config in: "%s", status code:' % monitorHost
    try:
        update = requests.post(
            'https://%s/api/config/change' % monitorHost,
            headers={'content-type': 'application/json'})
    finally:
        print update.status_code


def main():
    hostsToCreate(monitorHost, host_name)
    hostsWithSevicesToCreate(monitorHost, host_name, service_description)

    save_config(monitorHost)


if __name__ == '__main__':
   main()