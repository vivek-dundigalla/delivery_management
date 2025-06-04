from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class DeliveryOrder(models.Model):
    _name = 'delivery.management'
    _description = 'Delivery Management'

    number = fields.Char(string="Invoice Number")
    due_date = fields.Char(string="Due Date")
    next_activity = fields.Char(string="Next Activity")

    tax_excluded = fields.Monetary(string="Tax Excluded", currency_field='currency_id')
    total = fields.Monetary(string="Total", currency_field='currency_id')
    total_in_currency = fields.Monetary(string="Total In Currency", currency_field='currency_id')
    order_amount_due = fields.Monetary(string="Order Amount Due", currency_field='currency_id')

    delivery_boy = fields.Many2one('delivery.boy', string="Delivery Boy")

    customer_name = fields.Many2one("res.partner", string="Customer Name")
    customer_mobile = fields.Char(string="Mobile Number")
    customer_address = fields.Text(string="Address")
    customer_address1 = fields.Text(string=" ")
    customer_address2 = fields.Text(string=" ")
    customer_address3 = fields.Text(string=" ")
    customer_address4 = fields.Text(string=" ")
    customer_address5 = fields.Text(string=" ")

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    tax_excluded_display = fields.Float(string="Tax Excluded Display", compute='_compute_currency_display', store=True)
    total_display = fields.Float(string="Total Display", compute='_compute_currency_display', store=True)
    total_in_currency_display = fields.Float(string="Total In Currency Display", compute='_compute_currency_display',
                                             store=True)
    order_amount_due_display = fields.Float(string="Order Amount Due Display", compute='_compute_currency_display',
                                            store=True)

    total_tax_excluded_sum = fields.Float(string="Total Tax Excluded Sum", compute='_compute_total_sums')
    total_amount_sum = fields.Float(string="Total Amount Sum", compute='_compute_total_sums')

    delivery_state = fields.Selection([
        ('draft', 'Invoice'),
        ('transit', 'Delivery Assigned'),
        ('onway', 'Delivery Onway'),
        ('arrived', 'Delivery SuccessFull'),
        ('collection', 'Delivery Collection'),
        ('cancel_delivery', 'Cancel Delivery'),
    ], default='draft', string="Delivery Status")

    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        compute='_compute_invoice',
        store=True,
        readonly=True
    )

    payment_state = fields.Selection([
        ('not_paid', 'Cash On Delivery'),
        ('paid', 'Paid'),
        ('denied', 'Not Paid'),
    ], string="Payment State", compute='_compute_payment_state', store=True, readonly=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
    ], string="Status")

    order_line_ids = fields.One2many('delivery.management.line', 'delivery_id', string='Order Lines')

    amount_residual = fields.Monetary(string="Due Amount", currency_field='currency_id',
                                      compute='_compute_amount_residual', store=False)

    is_denied = fields.Boolean(string="Manually Denied", default=False)

    @api.depends('invoice_id.payment_state', 'is_denied')
    def _compute_payment_state(self):
        for record in self:
            if record.is_denied:
                record.payment_state = 'denied'
            elif record.invoice_id:
                if record.invoice_id.payment_state == 'paid':
                    record.payment_state = 'paid'
                else:
                    record.payment_state = 'not_paid'
            else:
                record.payment_state = 'not_paid'

    def action_denied_delivery(self):
        for record in self:
            record.is_denied = True
            record.delivery_state = 'cancel_delivery'
            record._compute_payment_state()

    @api.depends('number')
    def _compute_invoice(self):
        for record in self:
            invoice = self.env['account.move'].search([('name', '=', record.number)], limit=1)
            record.invoice_id = invoice.id if invoice else False

    def action_delivery_arrived(self):
        for record in self:
            record.delivery_state = "arrived"

    @api.depends('number')
    def _compute_amount_residual(self):
        for record in self:
            invoice = self.env['account.move'].search([('name', '=', record.number)], limit=1)
            record.amount_residual = invoice.amount_residual if invoice else 0.0

    def action_collect_delivery(self):
        for record in self:
            if record.amount_residual != 0:
                record.delivery_state = 'collection'
                record.payment_state = 'paid'

                invoice = self.env['account.move'].search([('name', '=', record.number)], limit=1)
                if invoice:
                    invoice.payment_state = 'paid'
                    invoice.write({'amount_residual': 0.0})

            else:
                raise UserError("Amount already Paid; nothing to collect.")

    def action_fill_order_lines_from_invoice(self):
        pass

    @api.depends('tax_excluded', 'total', 'total_in_currency', 'order_amount_due')
    def _compute_currency_display(self):
        for record in self:
            record.tax_excluded_display = float(record.tax_excluded or 0.0)
            record.total_display = float(record.total or 0.0)
            record.total_in_currency_display = float(record.total_in_currency or 0.0)
            record.order_amount_due_display = float(record.order_amount_due or 0.0)

    @api.depends('tax_excluded', 'total')
    def _compute_total_sums(self):
        all_records = self.env['delivery.management'].search([])
        for record in self:
            record.total_tax_excluded_sum = sum(r.tax_excluded or 0.0 for r in all_records)
            record.total_amount_sum = sum(r.total or 0.0 for r in all_records)

    @api.model
    def create(self, vals):
        if vals.get('delivery_boy'):
            vals['delivery_state'] = 'transit'
        record = super().create(vals)
        if record.number:
            record.action_fill_order_lines_from_invoice()
        return record

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if vals.get('delivery_boy'):
                record.delivery_state = 'transit'
            elif 'delivery_boy' in vals and not vals.get('delivery_boy'):
                record.delivery_state = 'draft'
            if 'number' in vals or not record.order_line_ids:
                record.action_fill_order_lines_from_invoice()
        return res

    def action_cancel_delivery(self):
        for record in self:
            record.delivery_state = 'cancel_delivery'

    def action_onway_delivery(self):
        for record in self:
            record.delivery_state = "onway"

    @api.depends('number')
    def update_payment_state(self):
        for record in self:
            if record.number:
                invoice = self.env['account.move'].search([('name', '=', record.number)], limit=1)
                record.payment_state = invoice.payment_state if invoice else 'not_paid'


class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_management = fields.Many2one('delivery.management', 'delivery Management')

    def _update_delivery_management_record(self, move):

        if move.move_type != 'out_invoice':
            return

        relative_due_date = self._get_relative_date(move.invoice_date_due)

        delivery_data = {
            'due_date': relative_due_date,
            'total': move.amount_total,
            'total_in_currency': move.amount_total,
            'tax_excluded': move.amount_untaxed_in_currency_signed,
            'order_amount_due': move.amount_residual,
            'payment_state': move.payment_state,
            'status': move.state,
            'currency_id': self.env.company.currency_id.id,
            'customer_name': move.partner_id.id or '',
            'customer_mobile': move.partner_id.mobile or '',
            'customer_address': move.partner_id.street or '',
            'customer_address1': move.partner_id.street2 or '',
            'customer_address2': move.partner_id.zip or '',
            'customer_address3': move.partner_id.city or '',
            'customer_address4': move.partner_id.state_id.name or '',
            'customer_address5': move.partner_id.country_id.name or '',
            'number': move.name,
            'amount_residual': move.amount_residual,
        }

        if move.delivery_management:
            move.delivery_management.order_line_ids.unlink()
            move.delivery_management.write(delivery_data)
            for line in move.invoice_line_ids:
                self.env['delivery.management.line'].create({
                    'delivery_id': move.delivery_management.id,
                    'product_id': line.product_id.id,
                    'description': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'taxes': [(6, 0, line.tax_ids.ids)],
                    'price_subtotal': line.price_subtotal,
                })
        else:
            delivery_data['order_line_ids'] = [
                (0, 0, {
                    'product_id': line.product_id.id,
                    'description': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'taxes': [(6, 0, line.tax_ids.ids)],
                    'price_subtotal': line.price_subtotal, })
                for line in move.invoice_line_ids
            ]
            delivery = self.env['delivery.management'].create(delivery_data)
            move.delivery_management = delivery

    def write(self, vals):
        res = super().write(vals)
        for move in self:
            if move.move_type == 'out_invoice' and (
                    'invoice_date_due' in vals or 'amount_total' in vals or
                    'amount_untaxed_in_currency_signed' in vals or 'amount_residual' in vals or
                    'payment_state' in vals or 'state' in vals or
                    'partner_id' in vals or 'name' in vals
            ):
                self._update_delivery_management_record(move)

                delivery = self.env['delivery.management'].search([('number', '=', move.name)], limit=1)
                if delivery:
                    delivery.update_payment_state()

        return res

    def action_post(self):
        res = super().action_post()
        for move in self:
            if move.move_type == 'out_invoice':
                self._update_delivery_management_record(move)
        return res

    def _get_relative_date(self, due_date):
        if not due_date:
            return "No Due Date"
        today = datetime.today().date()
        diff = (due_date - today).days
        if diff == 0:
            return "Today"
        elif diff == -1:
            return "Yesterday"
        elif diff == 1:
            return "Tomorrow"
        elif diff < 0:
            return f"{abs(diff)} days ago"
        else:
            return f"In {diff} days"


class DeliveryManagementLine(models.Model):
    _name = 'delivery.management.line'
    _description = 'Delivery Order Line'

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)

    delivery_id = fields.Many2one('delivery.management', string='Delivery Reference', ondelete='cascade')
    product_id = fields.Many2one('product.product', 'product')
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Price Unit')
    taxes = fields.Many2many('account.tax', string='Taxes')
    price_subtotal = fields.Monetary(string='Amount', currency_field='currency_id')

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
