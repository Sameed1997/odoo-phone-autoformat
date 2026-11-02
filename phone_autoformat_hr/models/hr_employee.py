from odoo import api, models


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'phone.autoformat.mixin']

    def _autoformat_country(self, values):
        # hr.employee.country_id is the employee's nationality, so it must not
        # decide how numbers are parsed. Use the company's country instead.
        company = self[:1].company_id or self.env.company
        return company.country_id or self.env.company.country_id

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([self._autoformat_vals(dict(v)) for v in vals_list])

    def write(self, vals):
        return super().write(self._autoformat_vals(dict(vals)))
