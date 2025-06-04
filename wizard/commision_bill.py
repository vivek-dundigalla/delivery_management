from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class CommisionBill(models.TransientModel):
    _name = 'commision.bill'
    _description = 'Vendor Bill Wizard'

    name = fields.Char(string="Name")
    amount_total = fields.Float(string="Amount Total")
    commission_fees = fields.Float(string="Commission Fees (%)")
    commission_amount = fields.Float(string="Commission Amount")
    total_in_currency_display = fields.Float(string="Total amount")



    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            delivery_orders = self.env['delivery.management'].browse(active_ids)
            total_in_currency_display = sum(order.total_in_currency_display for order in delivery_orders)

            first_delivery_boy = delivery_orders[0].delivery_boy if delivery_orders else False
            commission_fee = first_delivery_boy.commission_fee if first_delivery_boy else 0.0
            commission_fees = commission_fee * 100  # convert to percentage
            commission_amount = (total_in_currency_display * (commission_fees / 100)) if total_in_currency_display else 0.0

            res.update({
                'name': first_delivery_boy.name if first_delivery_boy else '',
                'amount_total': total_in_currency_display,
                'commission_fees': commission_fees,
                'commission_amount': commission_amount,
            })
        return res

    def create_delivery_boy_bill(self):
        self.ensure_one()

        bill_number = self.env['ir.sequence'].next_by_code('delivery.boy.bill')
        today = fields.Date.context_today(self)

        bill_vals = {
            'name': bill_number,
            'delivery_boy_name': self.name,
            'commission_fees': self.commission_fees,
            'commission_amount': self.commission_amount,
            'amount_total': self.amount_total,
            'bill_date': today,
        }

        bill = self.env['delivery.boy.bill'].create(bill_vals)

        return {
            'name': 'Delivery Boy Bill',
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.boy.bill',
            'view_mode': 'form',
            'view_id': self.env.ref('delivery_management.view_delivery_boy_bill_form').id,
            'res_id': bill.id,
            'target': 'current',
        }