import re

from odoo import models
from odoo.addons.phone_validation.tools import phone_validation

VALID_FORMATS = ('INTERNATIONAL', 'E164', 'NATIONAL', 'RFC3966')


class PhoneAutoFormatMixin(models.AbstractModel):
    _name = 'phone.autoformat.mixin'
    _description = 'Phone auto-format helper'

    def _autoformat_phone_fields(self):
        """Every stored, editable text field whose name contains 'phone' or
        'mobile' (includes Studio fields such as x_studio_phone_2)."""
        return [
            name for name, field in self._fields.items()
            if field.type == 'char' and field.store and not field.readonly
            and ('phone' in name or 'mobile' in name)
            and 'sanitized' not in name
        ]

    def _autoformat_country(self, values):
        """Region used to parse numbers typed without a + prefix."""
        country = self.env['res.country']
        if 'country_id' in self._fields:
            cid = values.get('country_id')
            if cid and isinstance(cid, int):
                country = country.browse(cid)
            elif self[:1]:
                country = self[:1].country_id
        return country or self.env.company.country_id

    def _autoformat_config(self):
        """(format, multiple) as chosen in Settings > Phone Auto Format."""
        icp = self.env['ir.config_parameter'].sudo()
        fmt = icp.get_param('phone_autoformat.format') or 'INTERNATIONAL'
        multiple = (icp.get_param('phone_autoformat.multiple') or 'multiple') == 'multiple'
        return fmt, multiple

    def _autoformat_value(self, number, country=None):
        """Format one number, or several when the setting allows it
        (separated by comma, semicolon or newline; joined with ', ')."""
        if not number:
            return number
        fmt, multiple = self._autoformat_config()
        if fmt not in VALID_FORMATS:  # 'off' or unknown value
            return number
        country = country or self.env.company.country_id
        if multiple:
            parts = [p.strip() for p in re.split(r'[,;\n]+', number) if p.strip()]
        else:
            parts = [number.strip()]
        result = []
        for part in parts:
            try:
                part = phone_validation.phone_format(
                    part,
                    country.code if country else None,
                    country.phone_code if country else None,
                    force_format=fmt,
                    raise_exception=True,
                )
            except Exception:
                pass  # invalid number: keep exactly as typed
            result.append(part)
        return ', '.join(result)

    def _autoformat_vals(self, vals):
        country = self._autoformat_country(vals)
        for fname in self._autoformat_phone_fields():
            if vals.get(fname):
                vals[fname] = self._autoformat_value(vals[fname], country)
        return vals

    def onchange(self, values, field_names, fields_spec):
        """Reformat phone fields in the form as soon as the user leaves them."""
        result = super().onchange(values, field_names, fields_spec)
        try:
            if isinstance(field_names, str):
                field_names = [field_names]
            phone_fields = self._autoformat_phone_fields()
            changed = [f for f in (field_names or [])]
            if 'country_id' in changed:
                targets = [f for f in phone_fields if values.get(f)]
            else:
                targets = [f for f in changed if f in phone_fields and values.get(f)]
            if targets:
                country = self._autoformat_country(values)
                for fname in targets:
                    new = self._autoformat_value(values[fname], country)
                    if new != values[fname]:
                        result.setdefault('value', {})[fname] = new
        except Exception:
            pass  # never break the form because of formatting
        return result
