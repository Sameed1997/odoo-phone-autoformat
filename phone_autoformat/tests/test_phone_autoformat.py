# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import phonenumbers

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestPhoneAutoFormat(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_pk = cls.env.ref("base.pk")
        cls.icp = cls.env["ir.config_parameter"].sudo()
        cls.Partner = cls.env["res.partner"]

    def _expected(self, number, region, fmt="INTERNATIONAL"):
        parsed = phonenumbers.parse(number, region)
        return phonenumbers.format_number(
            parsed, getattr(phonenumbers.PhoneNumberFormat, fmt)
        )

    def _set_config(self, fmt="INTERNATIONAL", multiple="multiple"):
        self.icp.set_param("phone_autoformat.format", fmt)
        self.icp.set_param("phone_autoformat.multiple", multiple)

    def _create(self, phone):
        return self.Partner.create(
            {"name": "Test", "phone": phone, "country_id": self.country_pk.id}
        )

    def test_create_formats_phone(self):
        self._set_config()
        self.assertEqual(
            self._create("0300 1234567").phone, self._expected("03001234567", "PK")
        )

    def test_write_formats_phone(self):
        self._set_config()
        partner = self._create(False)
        partner.write({"phone": "03001234567"})
        self.assertEqual(partner.phone, self._expected("03001234567", "PK"))

    def test_e164_format(self):
        self._set_config(fmt="E164")
        self.assertEqual(
            self._create("0300 1234567").phone,
            self._expected("03001234567", "PK", "E164"),
        )

    def test_disabled_keeps_value(self):
        self._set_config(fmt="off")
        self.assertEqual(self._create("0300 1234567").phone, "0300 1234567")

    def test_invalid_number_is_kept(self):
        self._set_config()
        self.assertEqual(self._create("abc").phone, "abc")

    def test_multiple_numbers(self):
        self._set_config(multiple="multiple")
        expected = ", ".join(
            [self._expected("03001234567", "PK"), self._expected("03217654321", "PK")]
        )
        self.assertEqual(self._create("03001234567; 03217654321").phone, expected)

    def test_single_number_mode_does_not_split(self):
        self._set_config(multiple="single")
        value = self.Partner._autoformat_value(
            "03001234567, 03217654321", self.country_pk
        )
        self.assertEqual(value, "03001234567, 03217654321")

    def test_phone_fields_detection(self):
        fields_ = self.Partner._autoformat_phone_fields()
        self.assertIn("phone", fields_)
        self.assertNotIn("phone_sanitized", fields_)
        self.assertNotIn("name", fields_)
