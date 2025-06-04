from odoo import models, fields, api

class DeliveryDashboard(models.TransientModel):
    _name = 'delivery.dashboard'
    _description = 'Delivery Dashboard'

    delivery_invoice_count = fields.Integer(compute="_compute_counts")
    delivery_canceled_count = fields.Integer(compute="_compute_counts")
    delivery_on_way_count = fields.Integer(compute="_compute_counts")
    delivery_arrived_count = fields.Integer(compute="_compute_counts")
    delivery_assigned_count = fields.Integer(compute="_compute_counts")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if count:
            return 1
        return self.browse(1)

    def _compute_counts(self):
        self.delivery_invoice_count = self.env['delivery.management'].search_count([])
        self.delivery_canceled_count = self.env['delivery.management'].search_count([('delivery_state', '=', 'cancelled')])
        self.delivery_on_way_count = self.env['delivery.management'].search_count([('delivery_state', '=', 'on_way')])
        self.delivery_arrived_count = self.env['delivery.management'].search_count([('delivery_state', '=', 'arrived')])
        self.delivery_assigned_count = self.env['delivery.management'].search_count([('delivery_state', '=', 'assigned')])


# from odoo import models, fields, api
#
#
# class DeliveryOrder(models.Model):
#     _name = 'delivery.dashboard'
#     _description = 'Delivery Management Dashboard'
#
#     GROUP_SELECTION = [
#         ('draft', 'Invoice'),
#         ('transit', 'Delivery Assigned'),
#         ('onway', 'Delivery On way'),
#         ('arrived', 'Delivery SuccessFull'),
#         ('collection', 'Delivery Collection'),
#         ('cancel_delivery', 'Cancel Delivery'),
#     ]
#
#     name = fields.Char(string="Group Name", readonly=True)
#     group_type = fields.Selection(GROUP_SELECTION, required=True, readonly=True)
#     count = fields.Integer(string='Count', compute="_compute_count")
#
#     delivery_boys_count = fields.Integer(string="Total Delivery Boys", compute="_compute_overall_counts")
#     delivery_paid_count = fields.Integer(string="Total Paid Orders", compute="_compute_overall_counts")
#     delivery_not_paid_count = fields.Integer(string="Total Pending Orders Payments", compute="_compute_overall_counts")
#     delivery_assigned_count = fields.Integer(string="Total Assigned Orders", compute="_compute_overall_counts")
#     delivery_onway_count = fields.Integer(string="Total On Way Orders", compute="_compute_overall_counts")
#     delivery_canceled_count = fields.Integer(string="Total Canceled Orders", compute="_compute_overall_counts")
#     delivery_arrived_count = fields.Integer(string="Total Arrived Orders", compute="_compute_overall_counts")
#     delivery_invoice_count = fields.Integer(string="Total Invoice Orders", compute="_compute_overall_counts")
#
#     @api.depends('group_type')
#     def _compute_count(self):
#         for record in self:
#             Delivery = self.env['delivery.management']
#             # Assuming 'state' or similar field tracks delivery status in 'delivery.management' model
#             if record.group_type == 'draft':
#                 record.count = Delivery.search_count([('state', '=', 'draft')])
#             elif record.group_type == 'transit':
#                 record.count = Delivery.search_count([('state', '=', 'transit')])
#             elif record.group_type == 'onway':
#                 record.count = Delivery.search_count([('state', '=', 'onway')])
#             elif record.group_type == 'arrived':
#                 record.count = Delivery.search_count([('state', '=', 'arrived')])
#             elif record.group_type == 'collection':
#                 record.count = Delivery.search_count([('state', '=', 'collection')])
#             elif record.group_type == 'cancel_delivery':
#                 record.count = Delivery.search_count([('state', '=', 'cancel_delivery')])
#             else:
#                 record.count = 0
#
#     @api.depends()
#     def _compute_overall_counts(self):
#         Delivery = self.env['delivery.management']
#         DeliveryBoy = self.env['delivery.boy']  # Assuming a model exists for delivery boys
#
#         # Total delivery boys count
#         total_boys = DeliveryBoy.search_count([])
#
#         # Count paid orders (assuming a field 'is_paid' boolean in delivery.management)
#         paid_orders = Delivery.search_count([('is_paid', '=', True)])
#         not_paid_orders = Delivery.search_count([('is_paid', '=', False)])
#
#         # Assigned orders - assuming state = 'transit'
#         assigned_orders = Delivery.search_count([('state', '=', 'transit')])
#
#         # On way orders - assuming state = 'onway'
#         onway_orders = Delivery.search_count([('state', '=', 'onway')])
#
#         # Canceled orders - state = 'cancel_delivery'
#         canceled_orders = Delivery.search_count([('state', '=', 'cancel_delivery')])
#
#         # Arrived orders - state = 'arrived'
#         arrived_orders = Delivery.search_count([('state', '=', 'arrived')])
#
#         # Invoice orders - state = 'draft' (based on your GROUP_SELECTION label)
#         invoice_orders = Delivery.search_count([('state', '=', 'draft')])
#
#         for record in self:
#             record.delivery_boys_count = total_boys
#             record.delivery_paid_count = paid_orders
#             record.delivery_not_paid_count = not_paid_orders
#             record.delivery_assigned_count = assigned_orders
#             record.delivery_onway_count = onway_orders
#             record.delivery_canceled_count = canceled_orders
#             record.delivery_arrived_count = arrived_orders
#             record.delivery_invoice_count = invoice_orders
#
#
# # from odoo import models, fields, api
# # from datetime import datetime
# # from odoo.exceptions import UserError, ValidationError
# #
# #
# # class DeliveryOrder(models.Model):
# #     _name = 'delivery.dashboard'
# #     _description = 'Delivery Management Dashboard'
# #
# #     GROUP_SELECTION = [
# #         ('draft', 'Invoice'),
# #         ('transit', 'Delivery Assigned'),
# #         ('onway', 'Delivery On way'),
# #         ('arrived', 'Delivery SuccessFull'),
# #         ('collection', 'Delivery Collection'),
# #         ('cancel_delivery', 'Cancel Delivery'),
# #     ]
# #
# #     name = fields.Char(string="Group Name", readonly=True)
# #     group_type = fields.Selection(GROUP_SELECTION, required=True, readonly=True)
# #     count = fields.Integer(string='Count', compute="_compute_count", store=True)
# #
# #     delivery_boys_count = fields.Integer(string="Total Delivery Boys",
# #                                          compute="_compute_counts", store=True)
# #     delivery_paid_count = fields.Integer(string="Total Paid Orders",
# #                                          compute="_compute_counts", store=True)
# #     delivery_not_paid_count = fields.Integer(string="Total Pending orders payments",
# #                                              compute="_compute_counts", store=True)
# #     delivery_assigned_count = fields.Integer(string="Total Assigned orders",
# #                                              compute="_compute_counts", store=True)
# #     delivery_onway_count = fields.Integer(string="Total on way orders",
# #                                           compute="_compute_counts", store=True)
# #     delivery_canceled_count = fields.Integer(string="Total canceled orders",
# #                                              compute="_compute_counts", store=True)
# #     delivery_arrived_count = fields.Integer(string="Total Arrived orders",
# #                                             compute="_compute_counts", store=True)
# #     delivery_invoice_count = fields.Integer(string="Total Invoice orders",
# #                                             compute="_compute_counts", store=True)
# #
# #     @api.depends('group_type')
# #     def _compute_count(self):
# #         for record in self:
# #             if record.group_type == 'draft':
# #                 record.count = self.env['delivery.management'].search_count([])
# #             elif record.group_type == 'transit':
# #                 record.count = self.env['delivery.management'].search_count([])
# #             elif record.group_type == 'onway':
# #                 record.count = self.env['delivery.management'].search_count([])
# #             elif record.group_type == 'arrived':
# #                 record.count = self.env['delivery.management'].search_count([])
# #             elif record.group_type == 'collection':
# #                 record.count = self.env['delivery.management'].search_count([])
# #             elif record.group_type == 'cancel_delivery':
# #                 record.count = self.env['delivery.management'].search_count([])
# #             elif record.group_type == 'cancel_delivery':
# #                 record.count = self.env['delivery.management'].search_count([])
# #
# #     @api.depends()
# #     def _compute_counts(self):
# #         for record in self:
# #             record.delivery_paid_count = self.env['delivery.management'].search_count([])
# #             record.delivery_not_paid_count = self.env['delivery.management'].search_count([])
# #             record.delivery_assigned_count = self.env['delivery.management'].search_count([])
# #             record.delivery_onway_count = self.env['delivery.management'].search_count([])
# #             record.delivery_canceled_count = self.env['delivery.management'].search_count([])
# #             record.delivery_arrived_count = self.env['delivery.management'].search_count([])
