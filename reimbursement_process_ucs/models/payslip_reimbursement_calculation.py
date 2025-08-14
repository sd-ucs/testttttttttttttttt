from odoo import models, fields, api, _
from datetime import date


class PayslipReimbursementCalculation(models.Model):
    _name = 'payslip.reimbursement.calculation'
    _description = "Payslip Reimbursement Calculation"
    
    payslip_id = fields.Many2one('hr.payslip',string="Payslip")
    fuel_reimbursement_amount = fields.Float(string="Fuel Reimbursement Amount")
    uniform_reimbursement_amount = fields.Float(string="Uniform Reimbursement Amount")
    medical_reimbursement_amount = fields.Float(string="Medical Reimbursement Amount")
    helper_reimbursement_amount = fields.Float(string="Helper Reimbursement Amount")
    periodicals_reimbursement_amount = fields.Float(string="Periodicals Reimbursement Amount")
    