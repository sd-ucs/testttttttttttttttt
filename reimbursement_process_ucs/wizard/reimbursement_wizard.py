from odoo import fields,models,api,_

class ReimbursementWizard(models.TransientModel):
    _name = "reimbursement.wizard"

    reason = fields.Text(string="Reason for Rejection",required="True")

    def action_save_domain(self):
        main_model = self.env['reimbursement.request'].browse(self._context.get('active_id'))
        if main_model:
            main_model.write({
                'reason': self.reason
            })

            template = self.env.ref('reimbursement_process_ucs.reimbursement_rejection_template')
            if template:
                template.send_mail(main_model.id, force_send=True)

        return {'type': 'ir.actions.act_window_close'}