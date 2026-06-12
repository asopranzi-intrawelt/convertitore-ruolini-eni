from odoo_handler.rpc.xml_rpc import XmlRpc
from odoo_handler.models import product, order_line


class SaleOrder:

    model = "sale.order"
    odoo = None
    pagination = {}
    fields = ['name', 'partner_id', 'project_manager_id', 'applicant_id',
              'service_ids', 'order_langcomb', 'amount_untaxed', 'order_line',
              'service_request_customer_id', 'invoice_note', 'accounting_note',
              'flex_note']

    def __init__(self):
        self.odoo = XmlRpc()
        self.pagination['fields'] = self.fields
        self.product_model = product.Product()
        self.line_model = order_line.SaleOrderLine()

    def get_list(self, param_search="", method="search_read"):
        order_ids = self.odoo.get_call(self.model, method, param_search, self.pagination)
        service_ids = {}
        order_line = {}
        for order in order_ids:
            order['service_ids'] = self.get_service(order['service_ids'])
            order['order_line'] = self.get_line(order['order_line'])
        return order_ids

    def get_single(self, order_id, method="read"):
        param_search = [[int(order_id)]]
        return self.odoo.get_call(self.model, method, param_search, self.pagination)

    def get_service(self, service):
        item_value = self.product_model.get_item(service)
        if item_value and len(item_value) > 0:
            return item_value

    def get_line(self, lines):
        item_value = self.line_model.get_item(lines)
        if item_value and len(item_value) > 0:
            return item_value

    def get_count(self, param_search, method="search_count"):
        order_count = self.odoo.get_call(self.model, method, param_search)
        return order_count
