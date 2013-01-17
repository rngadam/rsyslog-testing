#!/usr/bin/env python
#from __future__ import print_function
import re
import traceback
import rsyslog
import unittest
import os
import pyinotify
import time

class TestRsyslogPerformance:
    INPUT_FILE = "/tmp/rsyslog-testing/imfile"
    OUTPUT_FILE = "/tmp/rsyslog-testing/server.log"
    STATE_FILE = "/tmp/rsyslog-testing/imfile.state"
    QUEUE = "/tmp/rsyslog-testing/srvrfwd.00000001"
    QI = "/tmp/rsyslog-testing/srvrfwd.qi"

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVER_CONF = CURRENT_DIR + '/server2.conf'
    CLIENT_CONF = CURRENT_DIR + '/client2.conf'

    uid = 0

    def setUp(self):
        # start client
        # start server
        rsyslog.deleteIgnoreError(self.INPUT_FILE)
        rsyslog.deleteIgnoreError(self.OUTPUT_FILE)
        rsyslog.deleteIgnoreError(self.STATE_FILE)
        rsyslog.deleteIgnoreError(self.QUEUE)
        rsyslog.deleteIgnoreError(self.QI)

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

    def queue(self, message):
        print>>self.input, "(uid:%d) %s" % (self.uid, message)
        self.uid = self.uid + 1
        self.input.flush()


if __name__ == '__main__':
    benchmark = TestRsyslogPerformance()
    fh = None
    SESSION = time.time()
    DEBUG = False
    count = 10000

    print 'this session %d' % SESSION
    try:
        print "Benchmark setup with count %d" % count
        benchmark.setUp()
        for i in xrange(0, count):
            #print "%d" % i,
            benchmark.queue('session:%d' % SESSION)
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
            try:
                if benchmark.client.process.returncode:
                    print 'client exited with %d' % benchmark.client.process.returncode
                if benchmark.server.process.returncode:
                    print 'client exited with %d' % benchmark.server.process.returncode
                # must read otherwise pipe blows up
                client = benchmark.client.process.stdout.readline()
                server = benchmark.server.process.stdout.readline()
                #print 'CLIENT:' + client,
                #print 'SERVER:' + server,
            except:
                pass
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
