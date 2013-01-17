#!/usr/bin/env python
#from __future__ import print_function
import rsyslog
import unittest
import os
import pyinotify
import time

class TestRsyslogPerformance:
    INPUT_FILE = "/tmp/rsyslog-testing/imfile"
    OUTPUT_FILE = "/tmp/rsyslog-testing/server.log"
    STATE_FILE = "/tmp/rsyslog-testing/imfile.state"

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
        print>>self.input, "(%d) %s" % (self.uid, message)
        self.uid = self.uid + 1
        self.input.flush()


class PTmp(pyinotify.ProcessEvent):
    received = 0
    def __init__(self, filename):
        self.filename = filename
        self.fh = open(filename, 'r')

    def process_IN_MODIFY(self, event):
        print '!',
        filename = os.path.join(event.path, event.name)
        #print filename
        if self.filename not in filename:
            print '?',
            return
        else:
            print '.',
            print self.fh.readline().rstrip()
            self.received = self.received + 1

def setupNotifier(filename):
    wm = pyinotify.WatchManager()
    dirmask = pyinotify.IN_MODIFY
    fh = open(filename, 'r')
    index = filename.rfind('/')
    fh.seek(0,2)
    ptmp = PTmp(filename)
    #notifier = pyinotify.ThreadedNotifier(wm, ptmp)
    #notifier.start()
    notifier = pyinotify.Notifier(wm, ptmp)
    wm.add_watch(filename[:index], dirmask)
    return (ptmp, notifier, fh)

if __name__ == '__main__':
    benchmark = TestRsyslogPerformance()
    notifier = None
    fh = None
    try:
        count = 1000
        print "Benchmark setup with count %d" % count
        benchmark.setUp()
        (ptmp, notifier, fh) = setupNotifier(benchmark.OUTPUT_FILE)
        for i in xrange(0, count):
            print "%d" % i,
            benchmark.queue('message')

        while count > ptmp.received:
            print '#%d' % ptmp.received,
            print "processing events"
            notifier.process_events()
            if notifier.check_events():
                 print "reading events"
                 notifier.read_events()
    except Exception, e:
        print e
    finally:
        print 'cleaning up'
        benchmark.tearDown()
        notifier.stop()
        fh.close()
