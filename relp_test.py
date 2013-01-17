#!/usr/bin/env python
#from __future__ import print_function
import rsyslog
import unittest
import os


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
        rsyslog.deleteIgnoreError(self.INPUT_FILE)
        rsyslog.deleteIgnoreError(self.OUTPUT_FILE)
        rsyslog.deleteIgnoreError(self.STATE_FILE)

        self.input = open(self.INPUT_FILE, 'w+')
        self.output = open(self.OUTPUT_FILE, 'w+')

        self.server = rsyslog.Rsyslog(self.SERVER_CONF)
        self.server.start()
        self.server.waitOutput('worker IDLE, waiting for work')

        self.client = rsyslog.Rsyslog(self.CLIENT_CONF)
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
        rsyslog.waitOutput(
            self.output, 'test_message_sending', timeout=5, echo=True)

    def test_message_send_shutdown_resume(self):
        self.server.stop()
        print>>self.input, 'test_message_send_shutdown_resume'
        self.input.flush()
        self.server.start()
        rsyslog.waitOutput(
            self.output, 'test_message_send_shutdown_resume',
            timeout=5, echo=True)


if __name__ == '__main__':
    unittest.main()