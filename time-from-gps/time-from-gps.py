#!/usr/bin/python
# -*- coding: UTF-8 -*-

import gps
import os
import xmlrpclib
import time
#import datetime
#import dateutil.parser

SUPERVISOR_AUTH = "auth"

# write a temporary html report
HTML_OUTPUT_DIR = "/run/www"
HTML_OUTPUT_FILE = "/index.html"
if not os.path.exists(HTML_OUTPUT_DIR):
    os.makedirs(HTML_OUTPUT_DIR)
fout = open(HTML_OUTPUT_DIR+HTML_OUTPUT_FILE, "w")
fout.write("""
<html>
  <title>ntpi info</title>
  <meta content="text/html; charset=utf-8;" http-equiv="Content-Type">
  <body>
    <h1>ntpi info</h1>
    <h3>No GPS connection yet</h3>
    <a href="/cgi-bin/serverconfig.py">Further server info and configuration</a>
    <blockquote>(Will take a second or two to load.)</blockquote>
  </body>
</html>
""")
fout.close()

# wait for gpsd to come up
time.sleep(1)

# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

# preparation: read the supervisor user and pass
if os.path.isfile(SUPERVISOR_AUTH):
    with open(SUPERVISOR_AUTH) as f:
        supervisor_namepass = f.readline().strip() + "@"
else:
    supervisor_namepass = ""


# main loop: wait for a time report from GPS
while True:
    try:
        report = session.next()
                # Wait for a 'TPV' report and display the current time
                # To see all report data, uncomment the line below
                # print report
        if report['class'] == 'TPV':
            if hasattr(report, 'time'):
                # this is a hacky way to add 0.7sec (which is more-less the time
                #   it takes from the GPS report to get to here)
                os.system('date --set="'+report.time[:20]+'7'+report.time[21:]+'"')
                # testing stuff:
                #print report.time
                #gpstime = dateutil.parser.parse(report.time)
                #print gpstime.isoformat('T')
                #print datetime.datetime.now().isoformat('T')
                # connect to supervisor
                supervisord = xmlrpclib.Server("http://"+supervisor_namepass+"localhost:9001/RPC2")
                # start the watcher daemon
                supervisord.supervisor.startProcess('gps-watcher')
                break
    except KeyError:
                pass
    except KeyboardInterrupt:
                quit()
    except StopIteration:
                session = None
                print "GPSD has terminated"
