#!/usr/bin/env python3
'''
Syslog Generator

Had a need to generate generic syslog messages to
test open source logging solutions.
'''

import logging
from logging.handlers import SysLogHandler
import socket
import argparse
import random
import sys
import time
from syslog_rfc5424_formatter import RFC5424Formatter

logging.socket = socket

"""
Modify these variables to change the hostname, domainame, and tag
that show up in the log messages.
"""
hostname = "host"
domain_name = ".example.com"
tag = ["kernel", "python", "ids", "ips"]
syslog_level = ["info", "error", "warn", "critical"]

def open_sample_log(sample_log):
    try:
        with open(sample_log, 'r') as sample_log_file:
            random_logs = random.choice(list(sample_log_file))
            return random_logs
    except FileNotFoundError:
        print("[+] ERROR: Please specify valid filename")
        return sys.exit()

def syslogs_sender():
    # Initalize SysLogHandler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    syslog = SysLogHandler(address=('localhost', '5514'), socktype=socket.SOCK_STREAM)
    logger.addHandler(syslog)

    random_level = random.choice(syslog_level)
    message = open_sample_log("/var/log/system.log")
    formatter = RFC5424Formatter()
    syslog.setFormatter(formatter)
    getattr(logger, random_level)(message)

    logger.removeHandler(syslog)
    syslog.close()

if __name__ == "__main__":
    try:
        while True:
            syslogs_sender()
            # time.sleep(1)
    except KeyboardInterrupt:
        # Use ctrl-c to stop the loop
        print("[+] Stopping syslog generator...")