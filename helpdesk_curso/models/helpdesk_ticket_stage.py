from odoo import fields, models, _, api
from datetime import datetime

class HelpdeskTicketStage(models.Model):
    _name = 'helpdesk.ticket.stage'

    name = fields.Char(
        string='Stage Name',
        required=True,
        translate=True
    )
    
    description = fields.Html(
        translate=True,
        sanitize_style=True
    )

    sequence = fields.Integer(default=1)

    active = fields.Boolean(default=True)

    unattended = fields.Boolean(
        string='Unattended')

    closed = fields.Boolean(
        string='Closed')

    fold = fields.Boolean(
        string='Folded in Kanban',
        help="This stage is folded in the kanban view "
             "when there are no records in that stage "
             "to display.")   
