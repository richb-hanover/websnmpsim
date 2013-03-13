# SNMP Simulator, http://snmpsim.sourceforge.net
# Managed value variaton module
# Simulate a gauge value
import math
import time
import random

settingsCache = {}

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

    if 'function' in settingsCache[oid]:
        f = getattr(math, settingsCache[oid]['function'])
    else:
        f = lambda x: x
    v = f((time.time() - booted) * float(settingsCache[oid].get('rate', 1))) * float(settingsCache[oid].get('scale', 1)) + float(settingsCache[oid].get('offset', 0))
    
    d = int(settingsCache[oid].get('deviation', 0))
    if d:
        v += random.randomrange(-d, d)

    if v < int(settingsCache[oid].get('min', 0)):
        v = int(settingsCache[oid].get('min', 0))
    elif v > int(settingsCache[oid].get('max', 0xffffffff)):
        v = int(settingsCache[oid].get('max', 0xffffffff))

    return oid, v

def shutdown(snmpEngine, *args): pass 
