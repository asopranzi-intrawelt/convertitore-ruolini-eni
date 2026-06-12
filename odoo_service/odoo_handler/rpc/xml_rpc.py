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

    def __init__(self, url=None, db=None):
        self.url = url or os.getenv('ODOO_URL', 'https://trex.intrawelt.com')
        self.db = db or os.getenv('ODOO_DB', 'intrawelt')
        self.url = url
        self.db = db
        self.inizializza_odoo_rpc()

    def inizializza_odoo_rpc(self):
        info = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        self.uid = info.authenticate(self.db, self.username, self.password, {})
        self.info = info

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

