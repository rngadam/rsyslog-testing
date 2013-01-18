#!/usr/bin/env python
#from __future__ import print_function
import re
import traceback
import rsyslog
import unittest
import os
import time
import syslog
import logging
from logging.handlers import SysLogHandler
import socket

class TestRsyslogTopology:
    BASE_DIR = "/tmp/rsyslog-testing"
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

    OUTPUT_FILE = "%s/server.log" % BASE_DIR
    QUEUE = "%s/srvrfwd.00000001" % BASE_DIR
    QI = "%s/srvrfwd.qi" % BASE_DIR

    SERVER_CONF = CURRENT_DIR + '/server3.conf'
    CLIENT_CONF = CURRENT_DIR + '/client3.conf'

    def setUp(self):
        # start client
        # start server
        rsyslog.deleteIgnoreError(self.OUTPUT_FILE)
        rsyslog.deleteIgnoreError(self.QUEUE)
        rsyslog.deleteIgnoreError(self.QI)
        rsyslog.mkdirIgnoreError(self.BASE_DIR)

        self.output = open(self.OUTPUT_FILE, 'w+')

        self.server = rsyslog.Rsyslog(self.SERVER_CONF)
        self.server.start()
        self.server.waitOutput('worker IDLE, waiting for work')

        self.client = rsyslog.Rsyslog(self.CLIENT_CONF)
        self.client.start()
        self.client.waitOutput('worker IDLE, waiting for work')

    def tearDown(self):
        if 'client' in self:
            self.client.stop()
        if 'server' in self:
            self.server.stop()

    def readLogs(self):
        try:
            if benchmark.client.process.returncode:
                print 'client exited with %d' % benchmark.client.process.returncode
            if benchmark.server.process.returncode:
                print 'client exited with %d' % benchmark.server.process.returncode
            # must read otherwise pipe blows up
            client = benchmark.client.process.stdout.readall()
            server = benchmark.server.process.stdout.readall()
            print 'CLIENT:' + client,
            print 'SERVER:' + server,
        except:
            pass


if __name__ == '__main__':
    benchmark = TestRsyslogTopology()
    fh = None
    SESSION = time.time()
    DEBUG = True
    count = 10000

    print 'this session %d' % SESSION
    try:
        print "Benchmark setup with count %d" % count
        benchmark.setUp()

        syslog = SysLogHandler(
            address=('127.0.0.1', 50140),
            facility=SysLogHandler.LOG_USER,
            socktype=socket.SOCK_DGRAM)
        syslog.setLevel(logging.INFO)
        logging.getLogger('').addHandler(syslog)
        formatter = logging.Formatter('%(message)s')
        syslog.setFormatter(formatter)

        for i in xrange(0, count):
            logging.info('uid:%d session:%d' % (i, SESSION))
            print i,
            benchmark.readLogs()

        print "Sent %d" % count
        received = 0
        fh = open(benchmark.OUTPUT_FILE, 'r')

        start = time.time()
        while count > received:
            line = fh.readline().rstrip()

            if len(line) > 0:
                if DEBUG:
                    print line
                s = re.search("uid:(\d+)", line)
                if s:
                    uid = int(s.group(1))
                    if DEBUG:
                        print '#%d[%d]' % (received, uid),
                    received = received + 1
            benchmark.readLogs()

        delta = time.time() - start
        per_thousand = (delta/count) * 1000
        per_second = count/delta
        print "elapsed: %.3f s per_thousand:%.3f per_second:%.3f" % (delta, per_thousand, per_second)
    except Exception, e:
        print 'Main loop exception ', e
        traceback.print_exc()
    finally:
        print 'cleaning up'
        benchmark.tearDown()
        if fh:
            fh.close()
