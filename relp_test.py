#!/usr/bin/env python
#from __future__ import print_function

import os
import unittest
from subprocess import *
import fcntl, os
import signal
import time
import syslog

class Rsyslog:
    def __init__(
            self,
            configFilename,
            rsyslogd='/usr/sbin/rsyslogd'):
        self.configFilename = configFilename
        self.rsyslogd = rsyslogd
        self.pid = '/tmp/' + os.path.basename(configFilename) + '.pid'
        try:
            os.remove(self.pid)
        except OSError:
            pass
        self.process = None

    def start(self):
        if self.process:
            if not self.process.returncode:
                raise Exception('Already started')

        params = [
                self.rsyslogd,
                '-c5',
                '-f',
                self.configFilename,
                '-dn',
                '-i',
                self.pid
            ]
        print(' '.join(params))
        self.process = Popen(
            params, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)


    def stop(self):
        if self.process:
            if self.process.returncode:
                print("Already stopped")
            else:
                self.process.send_signal(signal.SIGINT)
                try:
                    self.waitOutput('Clean shutdown completed, bye')
                except:
                    self.process.send_signal(signal.SIGKILL)

            self.process = None
        else:
            raise Exception('Not started!')

    def waitOutput(self, str, timeout=5):
        waitOutput(self.process.stdout, str, timeout)


def waitOutput(stream, str, timeout=5, echo=False):
    #print("LOOKING FOR %s" % str)
    fcntl.fcntl(stream.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
    lastLine = None
    start = time.time()
    buf = ""
    while time.time() - start < timeout:
        try:
            line = stream.readline().strip()
            if len(line) > 0:
                if echo:
                    print(line)
                buf = buf + line
                lastLine = line
            else:
                continue
        except IOError:
            continue

        if buf.find(str) != -1:
            #print ("FOUND %s" % str)
            return

    raise Exception("Timeout waiting for %s... last line read: %s" % (str, lastLine))

def deleteIgnoreError(filename):
    try:
        os.remove(filename)
    except OSError:
        pass

class TestRsyslogRELP(unittest.TestCase):
    INPUT_FILE = "/tmp/imfile"
    OUTPUT_FILE = "/tmp/server.log"
    STATE_FILE = "/tmp/imfile.state"

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVER_CONF = CURRENT_DIR + '/server.conf'
    CLIENT_CONF = CURRENT_DIR + '/client.conf'

    def setUp(self):
        # start client
        # start server
        deleteIgnoreError(self.INPUT_FILE)
        deleteIgnoreError(self.OUTPUT_FILE)
        deleteIgnoreError(self.STATE_FILE)

        self.input = open(self.INPUT_FILE, 'w+')
        self.output = open(self.OUTPUT_FILE, 'w+')

        self.server = Rsyslog(self.SERVER_CONF)
        self.server.start()
        self.server.waitOutput('worker IDLE, waiting for work')

        self.client = Rsyslog(self.CLIENT_CONF)
        self.client.start()
        self.client.waitOutput('worker IDLE, waiting for work')

    def tearDown(self):
        self.client.stop()
        self.server.stop()
        #deleteIgnoreError(self.INPUT_FILE)
        #deleteIgnoreError(self.OUTPUT_FILE)
        #deleteIgnoreError(self.STATE_FILE)

    def test_message_sending(self):
        print>>self.input, 'test_message_sending'
        self.input.flush()
        waitOutput(
            self.output, 'test_message_sending', timeout=5, echo=True)

    def test_message_send_shutdown_resume(self):
        self.server.stop()
        print>>self.input, 'test_message_send_shutdown_resume'
        self.input.flush()
        self.server.start()
        waitOutput(
            self.output, 'test_message_send_shutdown_resume',
            timeout=5, echo=True)


if __name__ == '__main__':
    unittest.main()