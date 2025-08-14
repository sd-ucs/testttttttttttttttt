from odoo import models, fields, api
from datetime import date


class HrPayslip(models.Model):
    _inherit = "hr.payslip"
    
    def create(self, vals):
        res = super(HrPayslip, self).create(vals)
        return res
    
    def action_update_reimbursement(self):
        for rec in self:
            num_days = (rec.date_to - rec.date_from).days + 1
            contract_id = rec.contract_id
            
            if not contract_id:
                continue
            
            total_fuel = (
                                     contract_id.fuel_vehicle_reimbursement / num_days) * rec.no_of_worked_day if num_days > 0 and contract_id.fuel_vehicle_reimbursement else 0
            total_uniform = (
                                        contract_id.uniform_reimbursement / num_days) * rec.no_of_worked_day if num_days > 0 and contract_id.uniform_reimbursement else 0
            total_helper = (
                                       contract_id.helper_reimbursement / num_days) * rec.no_of_worked_day if num_days > 0 and contract_id.helper_reimbursement else 0
            total_medical = (
                                        contract_id.medical_reimbursement / num_days) * rec.no_of_worked_day if num_days > 0 and contract_id.medical_reimbursement else 0
            total_periodicals = (
                                            contract_id.periodicals_reimbursement / num_days) * rec.no_of_worked_day if num_days > 0 and contract_id.periodicals_reimbursement else 0
            
          
            
            # Find existing reimbursement record
            payslip_reimbursement_id = self.env['payslip.reimbursement.calculation'].search([
                ('payslip_id.employee_id', '=', rec.employee_id.id),
                ('payslip_id.date_from', '>=', rec.date_from.replace(day=1)),
                ('payslip_id.date_from', '<=', rec.date_to)
            ], limit=1)
            
            if rec.date_from.month == 4 and rec.date_from.year == date.today().year:
                contract_id.previous_total_fuel_vehicle_reimbursement = contract_id.total_fuel_vehicle_reimbursement
                contract_id.total_fuel_vehicle_reimbursement = 0
                contract_id.previous_total_helper_reimbursement = contract_id.total_helper_reimbursement
                contract_id.total_helper_reimbursement = 0
                contract_id.previous_total_medical_reimbursement = contract_id.total_medical_reimbursement
                contract_id.total_medical_reimbursement = 0
                contract_id.previous_total_periodicals_reimbursement = contract_id.total_periodicals_reimbursement
                contract_id.total_periodicals_reimbursement = 0
                contract_id.previous_total_uniform_reimbursement = contract_id.total_uniform_reimbursement
                contract_id.total_uniform_reimbursement = 0
            
            if payslip_reimbursement_id:
                payslip_month = payslip_reimbursement_id.payslip_id.date_from.month
                payslip_year = payslip_reimbursement_id.payslip_id.date_from.year
                current_year = date.today().year
                
                is_prev = payslip_month > 4 and payslip_year == (current_year - 1) or \
                          payslip_month < 4 and payslip_year == current_year
                
                if is_prev:
                    contract_id.previous_total_fuel_vehicle_reimbursement -= payslip_reimbursement_id.fuel_reimbursement_amount
                    contract_id.previous_total_helper_reimbursement -= payslip_reimbursement_id.helper_reimbursement_amount
                    contract_id.previous_total_medical_reimbursement -= payslip_reimbursement_id.medical_reimbursement_amount
                    contract_id.previous_total_uniform_reimbursement -= payslip_reimbursement_id.uniform_reimbursement_amount
                    contract_id.previous_total_periodicals_reimbursement -= payslip_reimbursement_id.periodicals_reimbursement_amount
                else:
                    contract_id.total_fuel_vehicle_reimbursement -= payslip_reimbursement_id.fuel_reimbursement_amount
                    contract_id.total_helper_reimbursement -= payslip_reimbursement_id.helper_reimbursement_amount
                    contract_id.total_medical_reimbursement -= payslip_reimbursement_id.medical_reimbursement_amount
                    contract_id.total_uniform_reimbursement -= payslip_reimbursement_id.uniform_reimbursement_amount
                    contract_id.total_periodicals_reimbursement -= payslip_reimbursement_id.periodicals_reimbursement_amount
                
                payslip_reimbursement_id.write({
                    'payslip_id': rec.id,
                    'fuel_reimbursement_amount': total_fuel,
                    'uniform_reimbursement_amount': total_uniform,
                    'medical_reimbursement_amount': total_medical,
                    'helper_reimbursement_amount': total_helper,
                    'periodicals_reimbursement_amount': total_periodicals,
                })
            else:
                payslip_reimbursement_id = self.env['payslip.reimbursement.calculation'].create({
                    'payslip_id': rec.id,
                    'fuel_reimbursement_amount': total_fuel,
                    'uniform_reimbursement_amount': total_uniform,
                    'medical_reimbursement_amount': total_medical,
                    'helper_reimbursement_amount': total_helper,
                    'periodicals_reimbursement_amount': total_periodicals,
                })
            
            payslip_month = payslip_reimbursement_id.payslip_id.date_from.month
            payslip_year = payslip_reimbursement_id.payslip_id.date_from.year
            current_year = date.today().year
            
            is_prev = payslip_month > 4 and payslip_year == (current_year - 1) or \
                      payslip_month < 4 and payslip_year == current_year
            
            if is_prev:
                contract_id.previous_total_fuel_vehicle_reimbursement += payslip_reimbursement_id.fuel_reimbursement_amount
                contract_id.previous_total_helper_reimbursement += payslip_reimbursement_id.helper_reimbursement_amount
                contract_id.previous_total_medical_reimbursement += payslip_reimbursement_id.medical_reimbursement_amount
                contract_id.previous_total_uniform_reimbursement += payslip_reimbursement_id.uniform_reimbursement_amount
                contract_id.previous_total_periodicals_reimbursement += payslip_reimbursement_id.periodicals_reimbursement_amount
            else:
                contract_id.total_fuel_vehicle_reimbursement += payslip_reimbursement_id.fuel_reimbursement_amount
                contract_id.total_helper_reimbursement += payslip_reimbursement_id.helper_reimbursement_amount
                contract_id.total_medical_reimbursement += payslip_reimbursement_id.medical_reimbursement_amount
                contract_id.total_uniform_reimbursement += payslip_reimbursement_id.uniform_reimbursement_amount
                contract_id.total_periodicals_reimbursement += payslip_reimbursement_id.periodicals_reimbursement_amount
            
