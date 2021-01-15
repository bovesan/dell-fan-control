#!/usr/bin/env python

import subprocess
import re
import time
import signal
import sys

targetTemp = 50
currentSpeed = 50

def onStart():
  print 'Disabling automatic fan control'
  subprocess.call(['ipmitool', 'raw','0x30','0x30','0x01','0x00'])

def onClose(sig, frame):
  print 'Re-enabling automatic fan control'
  subprocess.call(['ipmitool', 'raw','0x30','0x30','0x01','0x01'])
  sys.exit(0)

def decreaseSpeed():
  global currentSpeed
  if currentSpeed <= 0:
    return
  currentSpeed -= 2
  currentSpeed = max(currentSpeed, 0)
  print 'Decrease fan speed to %d%%' % currentSpeed
  cmd = ['ipmitool', 'raw','0x30','0x30','0x02','0xff', hex(currentSpeed)]
  # print ' '.join(cmd)
  subprocess.call(cmd)

def increaseSpeed():
  global currentSpeed
  if currentSpeed >= 100:
    return
  currentSpeed += 20
  currentSpeed = min(currentSpeed, 100)
  print 'Increase fan speed to %d%%' % currentSpeed
  cmd = ['ipmitool', 'raw','0x30','0x30','0x02','0xff', hex(currentSpeed)]
  # print ' '.join(cmd)
  subprocess.call(cmd)

def loop():
  lines = subprocess.Popen(['sensors'], stdout=subprocess.PIPE).communicate()[0]
#   lines = '''coretemp-isa-0000
# Adapter: ISA adapter
# Core 0:        +3.0 C  (high = +81.0 C, crit = +101.0 C)
# Core 1:        -1.0 C  (high = +81.0 C, crit = +101.0 C)
# Core 2:        +1.0 C  (high = +81.0 C, crit = +101.0 C)
# Core 8:        -9.0 C  (high = +81.0 C, crit = +101.0 C)
# Core 9:        -3.0 C  (high = +81.0 C, crit = +101.0 C)
# Core 10:       +2.0 C  (high = +81.0 C, crit = +101.0 C)

# coretemp-isa-0001
# Adapter: ISA adapter
# Core 0:        +1.0 C  (high = -1.0 C, crit = +101.0 C)
# Core 1:        +0.0 C  (high = +81.0 C, crit = +101.0 C)
# Core 2:        +1.0 C  (high = +81.0 C, crit = +101.0 C)
# Core 8:        +2.0 C  (high = +81.0 C, crit = +101.0 C)
# Core 9:        -1.0 C  (high = +81.0 C, crit = +101.0 C)
# Core 10:       -4.0 C  (high = +81.0 C, crit = +101.0 C)'''
  maxTemp = None
  hasOverheatingSensor = False
  for line in lines.splitlines():
      match = re.search(r"((\+|\-)*[\d\.]+)(?:\ +C)", line)
      if match:
          temp = float(match.group(1))
          if maxTemp == None or temp > maxTemp:
              maxTemp = temp
          limitMatch = re.search(r"(?:high = )((\+|\-)*[\d\.]+)(?:\ +C)", line)
          if limitMatch:
            limit = float(limitMatch.group(1))
            if temp > limit:
              print line+' above limit!'
              hasOverheatingSensor = True
  # print 'Current temperature: ', maxTemp
  if hasOverheatingSensor or maxTemp > targetTemp:
    increaseSpeed()
  elif maxTemp < targetTemp:
    decreaseSpeed()
  time.sleep(15)

onStart()

signal.signal(signal.SIGINT, onClose)

while True:
  loop()