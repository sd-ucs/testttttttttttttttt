from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class ReimbursementLine(models.Model):
    _name = 'reimbursement.line'
    _description = 'Reimbursement Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request_id = fields.Many2one('reimbursement.request', string='Reimbursement Request', ondelete='cascade', tracking=True)
    # head_id = fields.Many2one('reimbursement.head', string='Head', tracking=True)
    employee_id = fields.Many2one('hr.employee', related='request_id.employee_id', store=True)
    reimbursement_type = fields.Selection([('fule', 'Fuel/Vehicle'),('uniform', 'Uniform'),('medical','Medical'),('helper','Helper'),('books_periodicals','Books and Periodicals')], string="Reimbursement Type")
    reimbursement_ytd = fields.Monetary(string='Reimbursement YTD', tracking=True, currency_field='currency_id',store=True,compute='_compute_reimbursement_type')
    amount = fields.Monetary(string='Proof Submitted Amount', required=True, tracking=True, currency_field='currency_id')
    exceed_reason = fields.Text(string="Reason for Less Approval", tracking=True, copy=False)
    date = fields.Date(string='Date', related='request_id.date', store=True)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'res_id',
        string='Attachments',
        domain=[('res_model', '=', 'reimbursement.line')],
        help='You can attach multiple documents like receipts, invoices, etc.',
        tracking=True
    )
    approved_amount = fields.Monetary(string='Approved Amount', tracking=True, currency_field='currency_id')
    reimbusement_to_submitted = fields.Monetary(string='Reibursement To Submitted', currency_field='currency_id')
    is_admin = fields.Boolean(compute='_compute_is_admin', default=False,  copy=False)
    is_exceed = fields.Boolean(string='Is Less Approval', default=False,  copy=False)
    description = fields.Char(string="Description",  copy=False, tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='request_id.currency_id',
        store=True,
        readonly=False
    )
    month = fields.Char(related='request_id.month',store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ],related='request_id.state',store=True)

    def _compute_is_admin(self):
        for grp in self:
            if self.env.user.has_group('reimbursement_process_ucs.group_reimbursement_admin') and grp.request_id.state == 'submitted' :
                grp.is_admin = True
            else:
                grp.is_admin = False

    # @api.onchange('amount'
    # def _onchange_amount(self):
    #     for rec in self:
    #         rec.approved_amount = rec.amount

    @api.onchange('approved_amount')
    def _onchange_approved_amount(self):
        for rec in self: rec.is_exceed = rec.approved_amount < rec.amount

    @api.depends('reimbursement_type')
    def _compute_reimbursement_type(self):
        
        current_month = date.today().month
        current_year = date.today().year

        for rec in self:
            contract_id = rec.request_id.employee_id.contract_id
            reimbursement_month = rec.date.month
            reimbursement_year = rec.date.year
        
            is_prev = False
            if reimbursement_month > 4 and reimbursement_year == (current_year - 1):
                is_prev = True
            
            if reimbursement_month < 4 and reimbursement_year == current_year :
                is_prev = True
                
            if reimbursement_month >= 4 and reimbursement_year == current_year:
                is_prev = False
                
            if reimbursement_month < 4 and reimbursement_year == (current_year + 1):
                is_prev = False
            
            if rec.reimbursement_type:
                
                if rec.reimbursement_type == 'fule':
                    reimbursement_ytd = contract_id.previous_total_fuel_vehicle_reimbursement if is_prev else contract_id.total_fuel_vehicle_reimbursement
                if rec.reimbursement_type == 'uniform':
                    reimbursement_ytd = contract_id.previous_total_uniform_reimbursement if is_prev else contract_id.total_uniform_reimbursement
                if rec.reimbursement_type == 'medical':
                    reimbursement_ytd = contract_id.previous_total_medical_reimbursement if is_prev else contract_id.total_medical_reimbursement
                if rec.reimbursement_type == 'helper':
                    reimbursement_ytd = contract_id.previous_total_helper_reimbursement if is_prev else contract_id.total_helper_reimbursement
                if rec.reimbursement_type == 'books_periodicals':
                    reimbursement_ytd = contract_id.previous_total_periodicals_reimbursement if is_prev else contract_id.total_periodicals_reimbursement
                
                rec.reimbursement_ytd = reimbursement_ytd

    @api.constrains('reimbursement_type', 'attachment_ids','approved_amount','amount')
    def _check_required_fields(self):
        for line in self:
            if not line.reimbursement_type:
                raise ValidationError("Reimbursement Type is required for each reimbursement line.")
            if not line.attachment_ids:
                raise ValidationError("At least one attachment is required for each reimbursement line.")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._assign_attachment_res_id()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._assign_attachment_res_id()
        return res

    def _assign_attachment_res_id(self):
        for line in self:
            for attachment in line.attachment_ids:
                if not attachment.res_id:
                    attachment.write({
                        'res_model': 'reimbursement.line',
                        'res_id': line.id,
                    })
