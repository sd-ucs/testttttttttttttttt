from odoo import fields,models,api,_

class ReimbursementHead(models.Model):
    _name = "reimbursement.head"
    _description = "Reimbursement Head"
    _rec_name = "head"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    head = fields.Char(string="Head",required="True", tracking=True)
    employee_ids = fields.Many2many("hr.employee",string="Employees", tracking=True)
