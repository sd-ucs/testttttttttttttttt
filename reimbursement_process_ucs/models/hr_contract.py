from odoo import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    fuel_vehicle_reimbursement = fields.Float(string="Fuel Vehicle Reimbursement")
    uniform_reimbursement = fields.Float(string="Uniform Reimbursement")
    helper_reimbursement = fields.Float(string="Helper Reimbursement")
    medical_reimbursement = fields.Float(string="Medical Reimbursement")
    periodicals_reimbursement = fields.Float(string="Periodicals Reimbursement")

    total_fuel_vehicle_reimbursement = fields.Float(string="Total Fuel Vehicle Reimbursement")
    previous_total_fuel_vehicle_reimbursement = fields.Float(string="Previous Total Fuel Vehicle Reimbursement")

    total_uniform_reimbursement = fields.Float(string="Total Uniform Reimbursement")
    previous_total_uniform_reimbursement = fields.Float(string="Previous Total Uniform Reimbursement")

    total_helper_reimbursement = fields.Float(string="Total Helper Reimbursement")
    previous_total_helper_reimbursement = fields.Float(string="Previous Total Helper Reimbursement")

    total_medical_reimbursement = fields.Float(string="Total Medical Reimbursement")
    previous_total_medical_reimbursement = fields.Float(string="Previous Total Medical Reimbursement")

    total_periodicals_reimbursement = fields.Float(string="Total Periodicals Reimbursement")
    previous_total_periodicals_reimbursement = fields.Float(string="Previous Total Periodicals Reimbursement")

    approved_fuel_vehicle_reimbursement = fields.Float(string="Approved Fuel Vehicle Reimbursement")
    approved_uniform_reimbursement = fields.Float(string="Approved Uniform Reimbursement")
    approved_helper_reimbursement = fields.Float(string="Approved Helper Reimbursement")
    approved_medical_reimbursement = fields.Float(string="Approved Medical Reimbursement")
    approved_periodicals_reimbursement = fields.Float(string="Approved Periodicals Reimbursement")
