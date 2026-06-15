import xmlrpc.client
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))


class XmlRpc:

    url = ""
    db = ""
    username = os.getenv('ODOO_USERNAME', '')
    password = os.getenv('ODOO_PASSWORD', '')
    uid = ""
    info = ""
    # sessione Odoo condivisa fra istanze: chiave (url, db, utente) -> (uid, info)
    _session_cache = {}

    def __init__(self, url=None, db=None):
        self.url = url or os.getenv('ODOO_URL', 'https://trex.intrawelt.com')
        self.db = db or os.getenv('ODOO_DB', 'intrawelt')
        self.inizializza_odoo_rpc()

    def inizializza_odoo_rpc(self):
        # Autentica una sola volta per (url, db, utente) e riusa la sessione: evita
        # le centinaia di authenticate() ridondanti della conversione riga per riga.
        key = (self.url, self.db, self.username)
        cached = XmlRpc._session_cache.get(key)
        if cached is not None:
            self.uid, self.info = cached
            return
        info = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        self.uid = info.authenticate(self.db, self.username, self.password, {})
        self.info = info
        XmlRpc._session_cache[key] = (self.uid, self.info)

    def get_endpoint(self):
        return xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

    def get_call(self, model, method, parameters, pagination=""):
        models = self.get_endpoint()
        results = models.execute_kw(self.db,
                                    self.uid,
                                    self.password,
                                    model,
                                    method,
                                    parameters,
                                    pagination)
        return results

