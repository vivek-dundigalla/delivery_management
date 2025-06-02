from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class CommisionBill(models.TransientModel):
    _name = 'commision.bill'
    _description = 'Vendor Bill Wizard'

    name = fields.Char(string="Name")
    amount_total = fields.Float(string="Amount Total")
    commission_fees = fields.Float(string="Commission Fees (%)")
    commission_amount = fields.Float(string="Commission Amount")
    total_amount = fields.Float(string="Total amount")

    # @api.model
    # def default_get(self, fields_list):
    #     res = super().default_get(fields_list)
    #     active_id = self.env.context.get('active_id',[])
    #     if active_id:
    #         delivery_order = self.env['delivery.management'].browse(active_id)
    #         total_amount = sum(order.total_amount_sum for order in delivery_order)
    #
    #         res['name'] = delivery_order.delivery_boy.name if delivery_order.delivery_boy else ''
    #         res['amount_total'] = delivery_order.total_amount or 0.0
    #         res['commission_fees'] = delivery_order.delivery_boy.commission_fee * 100 if delivery_order.delivery_boy.commission_fee else 0.0
    #         res['commission_amount'] = (res['amount_total'] * (res['commission_fees'] / 100)) if res[
    #             'amount_total'] else 0.0
    #
    #     return res

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])  # Correct here: plural and default to empty list
        if active_ids:
            delivery_orders = self.env['delivery.management'].browse(active_ids)
            total_amount = sum(order.total_amount_sum for order in delivery_orders)  # Use the correct field here

            # Use first record's delivery boy
            first_delivery_boy = delivery_orders[0].delivery_boy if delivery_orders else False
            commission_fee = first_delivery_boy.commission_fee if first_delivery_boy else 0.0
            commission_fees = commission_fee * 100  # convert to percentage
            commission_amount = (total_amount * (commission_fees / 100)) if total_amount else 0.0

            res.update({
                'name': first_delivery_boy.name if first_delivery_boy else '',
                'amount_total': total_amount,
                'commission_fees': commission_fees,
                'commission_amount': commission_amount,
            })
        return res

    def create_delivery_boy_bill(self):
        # Your logic to create a vendor bill or any related action
        print("Delivery Boy:", self.name)
        print("Amount Total:", self.amount_total)
        print("Commission Fees:", self.commission_fees)
        print("Commission:", self.commission_amount)
        # Here you can create an actual vendor bill or other logic as needed
        return {'type': 'ir.actions.act_window_close'}
