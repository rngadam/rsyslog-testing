#!/bin/sh
/usr/sbin/rsyslogd -c5 -f `pwd`/$1 -N1
