from odoo import api, models


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'phone.autoformat.mixin']

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([self._autoformat_vals(dict(v)) for v in vals_list])

    def write(self, vals):
        return super().write(self._autoformat_vals(dict(vals)))
