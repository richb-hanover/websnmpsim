# SNMP Simulator, http://snmpsim.sourceforge.net
# Managed value variation module
# Simulate a writable Agent

volatileCache = {}

def init(snmpEngine, *args): pass 

def process(oid, tag, value, **context):
    if not context['nextFlag'] and not context['exactMatch']:
        return context['origOid'], context['errorStatus']  # serve exact OIDs
    if context['setFlag']:
        volatileCache[oid] = context['origValue']
    return oid, volatileCache.get(oid, value)

def shutdown(snmpEngine, *args): pass 
