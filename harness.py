#!/usr/bin/env python
import argparse
import os
import rsyslog
import time

class RsyslogHarness:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


    def __init__(self, config, baseDir="/tmp/rsyslog-testing"):
        self.config = os.path.join(self.CURRENT_DIR, config)
        self.baseName = os.path.basename(self.config)
        self.baseDir = baseDir
        self.logFile = '%s/%s.log' % (self.baseDir, self.baseName)
        self.queue = "%s/%s.queue.00000001" % (self.baseDir, self.baseName)
        self.qi = "%s/%s.queue.qi" % (self.baseDir, self.baseName)
        self.server = None

    def setUp(self):
        print "Cleaning up environment"
        #rsyslog.deleteIgnoreError(self.logFile)
        rsyslog.deleteIgnoreError(self.queue)
        rsyslog.deleteIgnoreError(self.qi)
        rsyslog.mkdirIgnoreError(self.baseDir)

        self.output = open(self.logFile, 'w+')

        print "Starting rsyslogd with config %s" % self.baseName
        self.server = rsyslog.Rsyslog(self.config)
        self.server.start()
        self.server.waitOutput('worker IDLE, waiting for work')
        print "Started rsyslogd with config %s" % self.baseName

    def tearDown(self):
        print "Shutting down rsyslogd with config %s" % self.baseName
        if self.server  :
            self.server.stop()

    def update(self):
        # must read otherwise pipe blows up
        try:
            if self.server.process.returncode:
                print 'server exited with %d' % self.server.process.returncode
            output = self.server.process.stdout.read()
            print '%s: %s' % (self.config, output),
        except Exception,e:
            if not hasattr(e, 'errno') or e.errno != 11:
                print e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("conf")
    args = parser.parse_args()

    harness = RsyslogHarness(args.conf)
    harness.setUp()
    try:
        while True:
            time.sleep(1)
            harness.update()
    except Exception,e:
        print e
    finally:
        harness.tearDown()