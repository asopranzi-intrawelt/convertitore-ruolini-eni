from odoo_handler.rpc.xml_rpc import XmlRpc


class AccountInvoice:

    model = "account.invoice"
    odoo = None
    pagination = {}
    fields = ['number', 'partner_id', 'date_invoice', 'date_due', 'residual']

    def __init__(self):
        self.odoo = XmlRpc()
        self.pagination['fields'] = self.fields

    def get_list(self, param_search="", method="search_read"):
        order_ids = self.odoo.get_call(self.model, method, param_search, self.pagination)
        #for order in order_ids:
        #    order['service_ids'] = self.get_service(order['service_ids'])
        return order_ids

    def get_single(self, order_id, method="read"):
        param_search = [[int(order_id)]]
        return self.odoo.get_call(self.model, method, param_search, self.pagination)

    def get_count(self, param_search, method="search_count"):
        order_count = self.odoo.get_call(self.model, method, param_search)
        return order_count
