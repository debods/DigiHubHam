"""
fldigi_client.py
Minimal XML-RPC client for FLDigi's built-in control interface
(http://127.0.0.1:7362/RPC2 by default). Method names and signatures
are FLDigi's own -- see the XML-RPC Control page in the FLDigi User's
Manual.

Not a standalone command; imported by dhweb's app.py. FLDigi is a GUI
application with no headless mode; this module only talks to an
already-running local instance and never starts/stops it.
"""

import http.client
import xmlrpc.client

DEFAULT_URL = "http://127.0.0.1:7362/RPC2"
TIMEOUT = 2


class _TimeoutTransport(xmlrpc.client.Transport):
    def __init__(self, timeout, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        return http.client.HTTPConnection(host, timeout=self.timeout)


def _proxy(url=DEFAULT_URL, timeout=TIMEOUT):
    return xmlrpc.client.ServerProxy(url, transport=_TimeoutTransport(timeout))


def _call(method, *args, url=DEFAULT_URL):
    """Call a dotted XML-RPC method (e.g. "main.tx"). Returns (ok, result)."""
    try:
        obj = _proxy(url)
        for part in method.split("."):
            obj = getattr(obj, part)
        return True, obj(*args)
    except (OSError, xmlrpc.client.Error) as e:
        return False, str(e)


def get_status(url=DEFAULT_URL):
    """Return a status dict, or None if FLDigi isn't reachable."""
    ok, version = _call("fldigi.version", url=url)
    if not ok:
        return None

    _, trx_status = _call("main.get_trx_status", url=url)
    _, modem = _call("modem.get_name", url=url)
    _, frequency = _call("rig.get_frequency", url=url)

    return {
        "version": version,
        "trx_status": trx_status or "unknown",
        "modem": modem or "unknown",
        "frequency": frequency,
    }


def list_modems(url=DEFAULT_URL):
    ok, names = _call("modem.get_names", url=url)
    return list(names) if ok and names else []


def set_modem(name, url=DEFAULT_URL):
    ok, _ = _call("modem.set_by_name", name, url=url)
    return ok


def set_frequency(hz, url=DEFAULT_URL):
    try:
        hz = float(hz)
    except (TypeError, ValueError):
        return False
    ok, _ = _call("rig.set_frequency", hz, url=url)
    return ok


def tx(url=DEFAULT_URL):
    ok, _ = _call("main.tx", url=url)
    return ok


def rx(url=DEFAULT_URL):
    ok, _ = _call("main.rx", url=url)
    return ok


def abort(url=DEFAULT_URL):
    ok, _ = _call("main.abort", url=url)
    return ok
