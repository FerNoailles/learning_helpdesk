# -*- coding: utf-8 -*-
# © 2015 Fernando Vasconcellos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, _
import datetime

class HelpdeskTicketTag(models.Model):
    _name = 'helpdesk.ticket.tag'

    name = fields.Char(
        string = 'Tittle',
    )

    description = fields.Html(
        string = 'Description',
    )