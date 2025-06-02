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
        active_ids = self.env.context.get('active_ids', [])  # Correct here: plural and default to empty list
        if active_ids:
            delivery_orders = self.env['delivery.management'].browse(active_ids)
            # total_in_currency_display = sum(order.total_in_currency_display_sum for order in delivery_orders)  # Use the correct field here
            total_in_currency_display = sum(order.total_in_currency_display for order in delivery_orders)

            # Use first record's delivery boy
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


    # @api.model
    # def default_get(self, fields_list):
    #     res = super().default_get(fields_list)
    #     active_id = self.env.context.get('active_id',[])
    #     if active_id:
    #         delivery_order = self.env['delivery.management'].browse(active_id)
    #         total_in_currency_display = sum(order.total_in_currency_display_sum for order in delivery_order)
    #
    #         res['name'] = delivery_order.delivery_boy.name if delivery_order.delivery_boy else ''
    #         res['amount_total'] = delivery_order.total_in_currency_display or 0.0
    #         res['commission_fees'] = delivery_order.delivery_boy.commission_fee * 100 if delivery_order.delivery_boy.commission_fee else 0.0
    #         res['commission_amount'] = (res['amount_total'] * (res['commission_fees'] / 100)) if res[
    #             'amount_total'] else 0.0
    #
    #     return res

    # def create_delivery_boy_bill(self):
    #     self.ensure_one()
    #
    #     # Generate bill number
    #     bill_number = self.env['ir.sequence'].next_by_code('delivery.boy.bill')
    #
    #     today = fields.Date.context_today(self)
    #     active_ids = self.env.context.get('active_ids', [])
    #     quantity = len(active_ids)
    #
    #     # Fetch delivery boy record (assuming a delivery.boy_id Many2one field on the wizard)
    #     delivery_boy = self.env['delivery.boy'].search([('name', '=', self.name)], limit=1)
    #     if not delivery_boy:
    #         raise ValidationError("No delivery boy found with name: %s" % self.name)
    #
    #     if not delivery_boy.partner_id:
    #         raise ValidationError("No linked vendor (partner_id) for delivery boy: %s" % self.name)
    #
    #     # Get the Service product
    #     product_service = self.env['product.product'].search([('name', '=', 'Service')], limit=1)
    #     if not product_service:
    #         raise ValidationError("No product found with name 'Service'.")
    #
    #     bill_vals = {
    #         'move_type': 'in_invoice',
    #         'name': bill_number,
    #         'partner_id': delivery_boy.partner_id.id,  # Use the linked vendor
    #         'invoice_origin': self.name,
    #         'invoice_date': today,
    #         'invoice_date_due': today,
    #         'journal_id': self.env['account.journal'].search([('type', '=', 'purchase')], limit=1).id,
    #         'invoice_line_ids': [(0, 0, {
    #             'product_id': product_service.id,
    #             'name': 'Service',
    #             'quantity': quantity,
    #             'price_unit': self.commission_amount,
    #             'price_subtotal': self.commission_amount,
    #         })],
    #     }
    #
    #     bill = self.env['account.move'].create(bill_vals)
    #
    #     # Return form view of created bill
    #     return {
    #         'name': 'Delivery Boy Bill',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.move',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('delivery_management.view_account_move_delivery_boy_bill_form').id,
    #         'res_id': bill.id,
    #         'target': 'current',
    #     }

    # def create_delivery_boy_bill(self):
    #     self.ensure_one()
    #     # Retrieve the delivery management orders from context
    #     active_ids = self.env.context.get('active_ids', [])
    #     if not active_ids:
    #         raise UserError("No delivery orders selected!")
    #
    #     delivery_orders = self.env['delivery.management'].browse(active_ids)
    #
    #     # Choose a journal (e.g., first purchase journal)
    #     purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
    #     if not purchase_journal:
    #         raise UserError("No purchase journal found!")
    #
    #     # Create a vendor bill
    #     bill_vals = {
    #         'move_type': 'in_invoice',
    #         'partner_id': delivery_orders[0].delivery_boy.id if delivery_orders[0].delivery_boy else False,
    #         'invoice_date': fields.Date.context_today(self),
    #         'date': fields.Date.context_today(self),
    #         'journal_id': purchase_journal.id,
    #         'invoice_origin': self.name,
    #         'invoice_line_ids': [],
    #     }
    #
    #     # Prepare invoice lines: one example line for the commission
    #     product = self.env['product.product'].search([('type', '=', 'service')], limit=1)
    #     if not product:
    #         raise UserError("Please define a service product to create the vendor bill line.")
    #
    #     line_vals = (0, 0, {
    #         'product_id': product.id,
    #         'name': 'Commission Payment',
    #         'quantity': 1.0,
    #         'price_unit': self.commission_amount,
    #         'account_id': product.property_account_expense_id.id or product.categ_id.property_account_expense_categ_id.id,
    #     })
    #     bill_vals['invoice_line_ids'].append(line_vals)
    #
    #     # Create the vendor bill
    #     bill = self.env['account.move'].create(bill_vals)
    #
    #     # Return an action to open the form view of the created bill
    #     return {
    #         'name': 'Vendor Bill',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.move',
    #         'view_mode': 'form',
    #         'res_id': bill.id,
    #         'target': 'current',
    #     }
