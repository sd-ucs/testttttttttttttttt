from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from datetime import date
import calendar


class ReimbursementRequest(models.Model):
    _name = 'reimbursement.request'
    _description = 'Reimbursement Request'
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_current_date(self):
        today = date.today()
        return today

    @api.model
    def default_get(self, fields):
        res = super(ReimbursementRequest, self).default_get(fields)
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if employee:
            res['employee_id'] = employee.id
        return res

    def _get_employee_domain(self):
        if self.env.user.has_group('reimbursement_process_ucs.group_reimbursement_user') and not self.env.user.has_group('reimbursement_process_ucs.group_reimbursement_admin'):
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            return [('id', '=', employee.id)]
        return []

    name = fields.Char(string='Request Reference', required=True, copy=False, readonly=True, default='Draft')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True, domain=lambda self: self._get_employee_domain())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )
    line_ids = fields.One2many('reimbursement.line', 'request_id', string='Reimbursement Details')
    date = fields.Date(string='Date', default=lambda self: self._get_default_current_date(), tracking=True)
    reason = fields.Text(string="Reason", readonly=True, tracking=True)
    month = fields.Char(string='Month', compute="_compute_month", store=True, tracking=True)
    total_amount = fields.Monetary(
        string="Total Amount", compute="_compute_total_amount",
        store=True, tracking=True, currency_field='currency_id'
    )
    approve_total_amount = fields.Monetary(
        string="Approved Amount", compute="_compute_total_amount",
        store=True, tracking=True, currency_field='currency_id'
    )
    manager_id = fields.Many2one('hr.employee', string='Manager', tracking=True)

    work_email = fields.Char(string="Work Email", readonly=True)
    department_id = fields.Many2one('hr.department', string="Department", readonly=True)
    mobile_phone = fields.Char(string="Mobile", readonly=True)
    job_position_id = fields.Many2one('hr.job', string='Job Position')
    note = fields.Char(string="note")

    @api.depends('date')
    def _compute_month(self):
        for rec in self:
            rec.month = ''
            if rec.date:
                rec.month = rec.date.strftime('%B %Y')

    @api.depends('line_ids.amount','line_ids.approved_amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped('amount'))
            rec.approve_total_amount = sum(rec.line_ids.mapped('approved_amount'))

    def action_submit(self):
        for rec in self:
            for line in rec.line_ids:
                if line.amount <= 0:
                    raise ValidationError(_("Please enter a valid amount for each reimbursement line."))
                if not line.attachment_ids:
                    raise ValidationError(_("Each reimbursement line must have at least one attachment."))

            if rec.name == 'Draft':
                rec.name = self.env['ir.sequence'].next_by_code('reimbursement.request') or _('New')
            rec.state = 'submitted'

            template = self.env.ref('reimbursement_process_ucs.reimbursement_submission_template')  
            template.send_mail(rec.id, force_send=True)


    def action_approve(self):
        
        current_month = date.today().month
        current_year = date.today().year
        
        for rec in self:
            contract_id = rec.employee_id.sudo().contract_id
            for line in rec.line_ids:
                if line.approved_amount <= 0:
                    raise ValidationError("Please enter approved amount for all lines before approving.")
                if line.approved_amount < line.amount and not line.exceed_reason:
                    raise ValidationError("Please provide a reason for approving less than the requested amount.")
                
                reimbursement_month = line.date.month
                reimbursement_year = line.date.year
        
                is_prev = False
                if reimbursement_month > 4 and reimbursement_year == (current_year - 1):
                    is_prev = True
                
                if reimbursement_month < 4 and reimbursement_year == current_year :
                    is_prev = True
                    
                if reimbursement_month >= 4 and reimbursement_year == current_year:
                    is_prev = False
                    
                if reimbursement_month < 4 and reimbursement_year == (current_year + 1):
                    is_prev = False

                if line.reimbursement_type == 'fule':
                    if is_prev:
                        contract_id.previous_approved_fuel_vehicle_reimbursement += line.approved_amount
                        line.reimbusement_to_submitted = contract_id.previous_total_fuel_vehicle_reimbursement - contract_id.previous_approved_fuel_vehicle_reimbursement
                    else:
                        contract_id.approved_fuel_vehicle_reimbursement += line.approved_amount
                        line.reimbusement_to_submitted = contract_id.total_fuel_vehicle_reimbursement - contract_id.approved_fuel_vehicle_reimbursement
                
                if line.reimbursement_type == 'uniform':
                    if is_prev:
                        contract_id.previous_approved_uniform_reimbursement += line.approved_amount
                        line.reimbusement_to_submitted = contract_id.previous_total_uniform_reimbursement - contract_id.previous_approved_uniform_reimbursement
                    else:
                        contract_id.approved_uniform_reimbursement += line.approved_amount
                        line.reimbusement_to_submitted = contract_id.total_uniform_reimbursement - contract_id.approved_uniform_reimbursement
                    
                if line.reimbursement_type == 'medical':
                    if is_prev:
                        contract_id.previous_approved_medical_reimbursement += line.approved_amount
                        line.reimbusement_to_submitted = contract_id.previous_total_medical_reimbursement - contract_id.previous_approved_medical_reimbursement
                    else:
                        contract_id.approved_medical_reimbursement += line.approved_amount
                        line.reimbusement_to_submitted = contract_id.total_medical_reimbursement - contract_id.approved_medical_reimbursement
                
                if line.reimbursement_type == 'helper':
                    if is_prev:
                        contract_id.previous_approved_helper_reimbursement += line.approved_amount
                        line.reimbusement_to_submitted = contract_id.previous_total_helper_reimbursement - contract_id.previous_approved_helper_reimbursement
                    else:
                        contract_id.approved_helper_reimbursement += line.approved_amount
                        line.reimbusement_to_submitted = contract_id.total_helper_reimbursement - contract_id.approved_helper_reimbursement
                
                if line.reimbursement_type == 'books_periodicals':
                    if is_prev:
                        contract_id.previous_approved_periodicals_reimbursement += line.approved_amount
                        line.reimbusement_to_submitted = contract_id.previous_total_periodicals_reimbursement - contract_id.previous_approved_periodicals_reimbursement
                    else:
                        contract_id.approved_periodicals_reimbursement += line.approved_amount
                        line.reimbusement_to_submitted = contract_id.total_periodicals_reimbursement - contract_id.approved_periodicals_reimbursement
            
            rec.state = 'approved'

            template = self.env.ref('reimbursement_process_ucs.reimbursement_approval_template')
            if template:
                template.send_mail(rec.id, force_send=True)

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'

        return {
            'type': 'ir.actions.act_window',
            'name': 'Reimbursement Wizard',
            'res_model': 'reimbursement.contract_id.approved_fuel_vehicle_reimbursement += line.approved_amountwizard',
            'view_mode': 'form',
            'target': 'new'
        }

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for record in self:
            if record.employee_id:
                record.job_position_id = record.employee_id.job_id.id
                record.work_email = record.employee_id.work_email
                record.department_id = record.employee_id.department_id.id
                record.mobile_phone = record.employee_id.mobile_phone
                record.manager_id = record.employee_id.parent_id.id

                # record.line_ids = [(5, 0, 0)]

                # heads = self.env['reimbursement.head'].search([
                #     ('employee_ids', 'in', record.employee_id.id)
                # ])
                # for head in heads:
                #     record.line_ids = [
                #         (0, 0, {
                #             'head_id': head.id,
                #             'amount': 0.0,
                #         })
                #     ]

    def action_approve_multi(self):
        for rec in self:
            if any(line.approved_amount <= 0 for line in rec.line_ids):
                raise ValidationError(
                    _("Please enter approved amount for all lines before approving record: %s") % rec.name)

            rec.state = 'approved'
            template = self.env.ref('reimbursement_process_ucs.reimbursement_approval_template',
                                    raise_if_not_found=False)
            if template:
                template.send_mail(rec.id, force_send=True)

    def action_reject_multi(self):
        for rec in self:
            rec.state = 'rejected'

            template = self.env.ref('reimbursement_process_ucs.reimbursement_rejection_template',
                                    raise_if_not_found=False)
            if template:
                template.send_mail(rec.id, force_send=True)