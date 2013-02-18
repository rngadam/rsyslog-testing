PIDFILE=/tmp/rsyslog-testing/`basename $1`.pid
~/local/sbin/rsyslogd -i $PIDFILE -d -n -M /home/rngadam/local/lib/rsyslog/ -f $1

