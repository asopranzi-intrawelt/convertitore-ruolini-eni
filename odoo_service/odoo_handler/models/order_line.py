from odoo_handler.rpc.xml_rpc import XmlRpc


class SaleOrderLine:

    model = "sale.order.line"
    odoo = None
    pagination = {}
    fields = ['product_id', 'name', 'product_uom_qty', 'product_uom', 'price_unit', 'price_subtotal']

    def __init__(self):
        self.odoo = XmlRpc()
        self.pagination['fields'] = self.fields

    def get_list_item(self, partner="", state="sale", method="search_read"):
        param_search = [[['partner_id', '=', int(partner)], ['state', '=', state]]]
        order_ids = self.odoo.get_call(self.model, method, param_search, self.pagination)
        return order_ids

    def get_item(self, item_id, method="read"):
        param_search = [item_id]
        item_read = self.odoo.get_call(self.model, method, param_search, self.pagination)
        return item_read
