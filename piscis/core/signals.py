from blinker import Namespace

piscis_signals = Namespace()

initialized = piscis_signals.signal("piscis-initialized")

blueprint_loaded = piscis_signals.signal("piscis-blueprint-loaded")
