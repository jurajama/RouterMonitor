#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import datetime
import io
import time
import traceback
import requests

import logging
from logging.handlers import RotatingFileHandler

from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.Connection import Connection

log = None

# How often ping test is performed
G_PING_INTERVAL = 900

# Host to ping
G_PING_HOST = "8.8.8.8"

# How many pings are sent per round
G_PING_COUNT = 3

# How many failed rounds until recovery is attempted
G_FAIL_THRESHOLD = 4

# Router IP and credentials
G_ROUTER_IP = "192.168.1.1"
G_ROUTER_PASSWORD = "verysecret"

class RouterMonitor():

    def __init__(self, run_as_service = False):
        self.failcount = 0
        self.run_as_service = run_as_service
        self._running = False
        if run_as_service:
            self.write_pid_file()

    def start(self):
        self._running = True
        while(self._running):
            time.sleep(G_PING_INTERVAL)
            self.ping_test()

    def write_pid_file(self):
        pid = str(os.getpid())
        f = open('/var/run/routermonitor.pid', 'w')
        f.write(pid)
        f.close()

    def performRecovery(self):
        print("routermonitor.py: In performRecovery, rebooting modem")
        connection = AuthorizedConnection('http://admin:' + G_ROUTER_PASSWORD + '@' + G_ROUTER_IP + '/')

        client = Client(connection)
        client.device.reboot()


    def ping_test(self):
        exitcode = 0

        if os.system("ping -c " + str(G_PING_COUNT) + " " + G_PING_HOST + " >/dev/null 2>&1") != 0:
            logger.error("routermonitor.py: Ping test failed")
#            print("ping fail")
            self.failcount = self.failcount+1

            if self.failcount>=G_FAIL_THRESHOLD:
                logger.error("routermonitor: Performing recovery by router reboot")
                self.failcount = 0
                self.performRecovery()

            return False
        else:
#            print("ping ok")
            if self.failcount>0:
                logger.error("routermonitor: ping test ok, resetting failcount")

            self.failcount = 0
            return True

###########################################
# Main function
###########################################

if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler(address = '/dev/log')
    formatter = logging.Formatter('%(module)s.%(funcName)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.error("Routermonitor starting")

    monitor = RouterMonitor(run_as_service = True)

    try:
        monitor.start()
    except KeyboardInterrupt:
        logger.error("Shutting down after KeyboardInterrupt")
    except:
        logger.error("Exception in router_monitor")
        logger.error(traceback.format_exc())
        raise
