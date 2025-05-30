from odoo import models, fields, api

class CommisionBill(models.TransientModel):
    _name = 'commision.bill'
    _description = 'Vendor Bill Wizard'

    name = fields.Char(string="Vendor Name")
    amount_total = fields.Float(string="Amount Total")
    commission_fees = fields.Float(string="Commission Fees (%)")
    commission_amount = fields.Float(string="Commission Amount")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Add logic to populate default values if needed
        res['name'] = ''
        res['amount_total']=""
        res['commission_fees'] =""
        res['commission_amount'] =""
        return res

    def create_delivery_boy_bill(self):
        # Your logic for creating the bill
        print("Create Delivery Boy Bill")
        return {'type': 'ir.actions.act_window_close'}

    def create_and_view_delivery_boy_bill(self):
        # Your logic for creating & viewing the bill
        print("Create & View Delivery Boy Bill")
        return {'type': 'ir.actions.act_window_close'}

