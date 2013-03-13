# SNMP Simulator, http://snmpsim.sourceforge.net
# Managed value variation module
# Simulate a counted value
import math
import time
import random

settingsCache = {}
countersCache = {}

booted = time.time()

def init(snmpEngine, *args):
    random.seed()

def process(oid, tag, value, **context):
    if not context['nextFlag'] and not context['exactMatch']:
        return context['origOid'], context['errorStatus']  # serve exact OIDs
    if context['setFlag']:
        return context['origOid'], context['errorStatus']  # read-only mode

    if oid not in settingsCache:
        settingsCache[oid] = dict([ x.split('=') for x in value.split(',') ])
    if oid not in countersCache:
        countersCache[oid] = float(settingsCache[oid].get('min', 0)), booted

    if 'function' in settingsCache[oid]:
        f = getattr(math, settingsCache[oid]['function'])
    else:
        f = lambda x: x

    v, t = countersCache[oid]
    v += abs(f((time.time() - t) * float(settingsCache[oid].get('rate', 1)))) * float(settingsCache[oid].get('scale', 1)) + float(settingsCache[oid].get('offset', 0))

    d = int(settingsCache[oid].get('deviation', 0))
    if d:
        v += random.randrange(0, d)

    if v < int(settingsCache[oid].get('min', 0)):
        v = int(settingsCache[oid].get('min', 0))
    elif v > int(settingsCache[oid].get('max', 0xffffffff)):
        if int(settingsCache[oid].get('wrap', 1)):
            v = int(settingsCache[oid].get('min', 0))
        else:
            v = int(settingsCache[oid].get('max', 0xffffffff))

    countersCache[oid] = v, time.time()

    return oid, v

def shutdown(snmpEngine, *args): pass 
