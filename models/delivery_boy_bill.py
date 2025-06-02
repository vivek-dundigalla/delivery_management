from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class DeliveryBoyBill(models.Model):
    _name = 'delivery.boy.bill'
    _description = 'Delivery Boy Bill'

    name = fields.Char(string="Bill Number")
    delivery_boy_name = fields.Char(string="Delivery Boy Name")
    commission_fees = fields.Float(string="Commission Fees (%)")
    commission_amount = fields.Float(string="Commission Amount")
    amount_total = fields.Float(string="Total Amount")
    bill_date = fields.Date(string="Bill Date", default=fields.Date.today)
    line_ids = fields.One2many('delivery.boy.bill.line', 'bill_id', string='Invoice Lines')

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id.id,
        readonly=True)

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('delivery.boy.bill') or 'New'
        return super().create(vals)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        active_ids = self.env.context.get('active_ids', [])
        quantity = len(active_ids)  # Number of selected invoices

        bill_number = self.env['ir.sequence'].next_by_code('delivery.boy.bill')
        if bill_number:
            res['name'] = bill_number

        # Search for "Service" product
        service_product = self.env['product.product'].search([('name', '=', 'Service')], limit=1)
        if not service_product:
            raise ValidationError("Product named 'Service' not found. Please create it first.")

        # Get the first delivery boy from the delivery orders
        delivery_orders = self.env['delivery.management'].browse(active_ids)
        first_delivery_boy = delivery_orders[0].delivery_boy if delivery_orders else False
        commission_fee = first_delivery_boy.commission_fee if first_delivery_boy else 0.0
        commission_fees = commission_fee * 100  # convert to percentage

        # Calculate total and commission amount
        total_in_currency_display = sum(order.total_in_currency_display for order in delivery_orders)
        commission_amount = (total_in_currency_display * (commission_fees / 100)) if total_in_currency_display else 0.0

        # Prepare the default line values
        line_vals = [(0, 0, {
            'product_id': service_product.id,
            'name': 'Service',
            'quantity': quantity,
            'commission_fees': commission_fees,
            'price_subtotal': commission_amount,
        })]

        # Set the default values in the form
        res.update({
            'delivery_boy_name': first_delivery_boy.name if first_delivery_boy else '',
            'commission_fees': commission_fees,
            'commission_amount': commission_amount,
            'amount_total': total_in_currency_display,
            'line_ids': line_vals,
        })

        return res


class DeliveryBoyBillLine(models.Model):
    _name = 'delivery.boy.bill.line'
    _description = 'Delivery Boy Bill Line'

    bill_id = fields.Many2one('delivery.boy.bill', string='Bill', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Label')
    account_id = fields.Many2one('account.account', string='Account')
    quantity = fields.Float(string='Quantity')
    commission_fees = fields.Float(string='Commission Fee (%)')
    commission_amount = fields.Float(string="Commission Amount")

    price_subtotal = fields.Float(string='Subtotal')

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id.id,
        readonly=True)

