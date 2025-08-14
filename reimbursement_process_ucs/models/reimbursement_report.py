from odoo import models, fields, api, tools


class ReimbursementReport(models.Model):
    _name = "reimbursement.report"
    _description = "Reimbursement Report"
    _auto = False
    
    employee_id = fields.Many2one("hr.employee", string="Employee", readonly=True)
    reimbursement_type = fields.Selection([('fule', 'Fuel/Vehicle'),('uniform', 'Uniform'),('medical','Medical'),('helper','Helper'),('books_periodicals','Books and Periodicals')], string="Reimbursement Type")
    reimbusement_ytd = fields.Monetary(string='Reimbursement YTD', tracking=True, currency_field='currency_id')
    proof_submitted = fields.Monetary(string='Reimbursement YTD', tracking=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id.id)
    proof_approved = fields.Monetary(string='Reimbursement YTD', tracking=True, currency_field='currency_id')
    reimbusement_to_be_submitted = fields.Monetary(string='Reimbursement YTD', tracking=True, currency_field='currency_id')
    request_id = fields.Many2one('reimbursement.request', string='Reimbursement Request', ondelete='cascade', tracking=True)



    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER() AS id,
                    emp.id AS employee_id
                FROM hr_employee emp WHERE active = true)
        """ % self._table)
