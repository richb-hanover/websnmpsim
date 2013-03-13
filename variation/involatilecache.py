# SNMP Simulator, http://snmpsim.sourceforge.net
# Managed value variaton module
# Simulate a writable Agent
import shelve

involatileCache = None

def init(snmpEngine, *args):
    global involatileCache
    if not args:
        raise Exception('shelves filename is not specified')
    involatileCache = shelve.open(args[0])

def process(oid, tag, value, **context):
    if involatileCache is None:
        raise Exception('variation module not initialized')
    if not context['nextFlag'] and not context['exactMatch']:
        return context['origOid'], context['errorStatus']  # serve exact OIDs
    if context['setFlag']:
        involatileCache[str(oid)] = context['origValue']
    return oid, involatileCache.get(str(oid), value)

def shutdown(snmpEngine, *args):
    if involatileCache is not None:
        involatileCache.close()
