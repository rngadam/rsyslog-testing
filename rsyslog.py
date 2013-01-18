import os
from subprocess import *
import fcntl, os
import signal
import time

class Rsyslog:
    def __init__(
            self,
            configFilename,
            rsyslogd='/usr/sbin/rsyslogd'):
        self.configFilename = configFilename
        self.rsyslogd = rsyslogd
        self.pid = '/tmp/rsyslog-testing/' + os.path.basename(configFilename) + '.pid'
        try:
            os.remove(self.pid)
        except OSError,e:
            print e
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
        print 'Removing %s' % filename
        os.remove(filename)
    except OSError,e:
        print e

def mkdirIgnoreError(directory):
    try:
        print 'Creating %s' % directory
        os.mkdir(directory)
    except OSError,e:
        print e
