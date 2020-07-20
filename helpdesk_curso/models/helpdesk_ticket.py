# -*- coding: utf-8 -*-
# © 2015 Fernando Vasconcellos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, _, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_stage_id(self):
        return self.env['helpdesk.ticket.stage'].search([], limit=1).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['helpdesk.ticket.stage'].search([])
        return stage_ids
    
    name = fields.Char(
        string = 'Tittle',
        required = True,
    )

    description = fields.Html(
        string = 'Description',
    )

    priority = fields.Selection([
        ('zero',_('Zero')),
        ('low',_('Low')),
        ('medium',_('Medium')),
        ('high',_('High')),
        ],
        string="Priority",
        default="medium")

    assigned_date = fields.Datetime(
        string='Start Date',
        compute='_compute_assigned_date',
        store=True,
    )

    end_date = fields.Date(
        string='End Date',
        required=True
    )
    
    closed = fields.Boolean(
        related='stage_id.closed'
    )
    
    unattended = fields.Boolean(
        related='stage_id.unattended'
    )

    user_id = fields.Many2one(
        string = "Assigned to",
        comodel_name = "res.users",
        ondelete = "restrict",
    )
    
    user_ids = fields.Many2many(
        comodel_name = "res.users",
        string="Members",
        related="team_id.user_ids",
    )

    partner_id = fields.Many2one(
        string = "Customer",
        comodel_name = "res.partner",
        ondelete = "restrict",
    )

    customer_name  =fields.Char(
        string = "Customer name",
    )

    customer_mail  =fields.Char(
        string = "Customer mail",     
    )

    tag_ids = fields.Many2many(
        name = "Tags",
        comodel_name = "helpdesk.ticket.tag",
    )

    color = fields.Integer(
        default= 0,
        compute = '_compute_deadline',
    )

    stage_id = fields.Many2one(
        'helpdesk.ticket.stage',
        string='Stage',
        group_expand='_read_group_stage_ids',
        default=_get_default_stage_id,
        track_visibility='onchange',
    )
    
    team_id = fields.Many2one(
        'helpdesk.ticket.team',
        string = 'Team',
    )

    @api.multi
    def assign_to_me (self):
        self.write({
            'user_id' : self.env.user.id
        })

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for record in self:
            partner = record.partner_id
            if partner:
                record.update({
                    'customer_name' : partner.name,
                    'customer_mail' : partner.email,
                })
    
    @api.multi
    @api.onchange('team_id', 'user_id')
    def _onchange_dominion_user_id(self):
        if self.user_id:
            if self.user_id and self.user_ids and \
                    self.user_id not in self.user_ids:
                self.update({
                    'user_id': False
                })
                return {'domain': {'user_id': []}}
        if self.team_id:
            return {'domain': {'user_id': [('id', 'in', self.user_ids.ids)]}}
        else:
            return {'domain': {'user_id': []}}

    @api.model
    @api.onchange('team_id')
    def _onchange_user_from_team(self):
        if self.team_id.user_ids:
            min_tickets = None; user_min_tickets = None
            for record in self.team_id.user_ids:
                    number_of_tickets = self.search_count([
                            ('team_id','=',self.team_id.id),
                            ('user_id','=',record.id)
                    ])
                    if (min_tickets is None) or (number_of_tickets < min_tickets) :
                        min_tickets = number_of_tickets
                        user_min_tickets = record
            self.user_id = user_min_tickets  
    
    @api.depends('user_id')
    def _compute_assigned_date(self):
        for tickets in self:
            tickets.assigned_date = fields.Datetime.now()

    @api.model
    def create(self,vals):
        if vals.get("partner_id") and (
            "customer_name" not in vals or "customer_mail" not in vals
        ):
            partner = self.env("res.partner").browse(vals["partner_id"])
            vals.setdefault("customer_name", partner.name)
            vals.setdefault("customer_mail", partner.email)
        
        res = super().create(vals)
        return res

    @api.model
    def _compute_deadline(self):
        for record in self:
            dnow = datetime.now()
            dout = datetime.strptime(record.end_date, '%Y-%m-%d')
            color_calculated = 10
            _logger.info(record.stage_id.name)
            if record.stage_id.name in ['New', 'In Progress', 'Awaiting']:
                if (dout - dnow).days < 0 :
                    color_calculated = 1
                elif (dout-dnow).days < 3 :
                    color_calculated = 3
            else:
                color_calculated = 0
            _logger.info('Color calculated : ' + str(color_calculated))
            _logger.info("It's unattended? " + str(record.unattended) )
            record.update({
                'color':color_calculated
            })