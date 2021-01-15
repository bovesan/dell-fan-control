#!/usr/bin/env python

import subprocess
import re
import time
import signal
import sys
import os

fail = False
print 'Testing ipmitool ...'
try:
	ipmi = subprocess.Popen(['ipmitool', 'sensor'], stdout=subprocess.PIPE).communicate()[0]
	print 'ipmitool ok'
	for line in ipmi.splitlines():
		if line.startswith('Ambient Temp'):
			print line
		if line.startswith('FAN'):
			print line
		if line.startswith('System Level'):
			print line
except:
	print 'ipmitool not found. Try running: apt-get install ipmitool'
	fail = True

print 'Testing sensors ...'
try:
	sensors = subprocess.Popen(['sensors'], stdout=subprocess.PIPE).communicate()[0]
	print 'sensors ok'
	for line in sensors.splitlines():
		print line
except:
	print 'sensors not found. Try running: apt-get install lm-sensors'
	fail = True

if fail:
	sys.exit(1)

outlines = []
for line in open('dell-fan-control.service'):
	if line.startswith('ExecStart'):
		outlines.append('ExecStart='+os.path.realpath('dell-fan-control.py'))
	else:
		outlines.append(line)

print 'Writing /etc/systemd/system/dell-fan-control.service'
open('/etc/systemd/system/dell-fan-control.service', 'w').write("\n".join(outlines))
cmd = ['systemctl', 'enable','dell-fan-control.service']
print ' '.join(cmd)
subprocess.call(cmd)
cmd = ['systemctl', 'start', 'dell-fan-control']
print ' '.join(cmd)
subprocess.call(cmd)
cmd = ['systemctl', 'status', 'dell-fan-control']
subprocess.call(cmd)