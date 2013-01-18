* rsyslog5 configuration file are insane
* rsyslog7 is buggy as hell

this is a set of tests to help with both...

# testing manually

full path to configuration file needed:

```
rsyslogd -c5 -f `pwd`/server3.conf -dn -i /tmp/rsyslog-testing/server3.conf.pid
```