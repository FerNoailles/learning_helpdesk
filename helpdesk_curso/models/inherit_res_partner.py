# -*- coding: utf-8 -*-
# © 2015 Fernando Vasconcellos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, _, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    helpdesk_ticket_ids  = fields.One2many(
        comodel_name = 'helpdesk.ticket',
        inverse_name = 'partner_id',
        string='Tickets'
    )
    count_tickets = fields.Integer(
        string = 'Number of tickets',
        compute = '_compute_count_tickets'
    )
    count_tickets_active = fields.Integer(
        string = 'Number of active tickets',
        compute = '_compute_count_tickets_active'
    )

    @api.multi
    def _compute_count_tickets(self):
        for record in self:
            
            ticket_ids = self.env["helpdesk.ticket"].search(
                [("partner_id", "child_of", record.id)]
            )
            
            record.count_tickets = len(record.helpdesk_ticket_ids)
            
            record.count_tickets_active = len(
                ticket_ids.filtered(
                    lambda ticket: not ticket.stage_id.closed
                )
            )