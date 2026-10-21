from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, new_test_user, tagged

SNAPSHOT = {'version': 1, 'savedAt': '2026-01-01T00:00:00Z', 'room': {}, 'kitchen': {'name': 'Test'}}


@tagged('post_install', '-at_install')
class TestKitchenDesign(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.salesman = new_test_user(cls.env, 'kitchen_salesman', groups='sales_team.group_sale_salesman')
        cls.partner = cls.env['res.partner'].create({'name': 'Kitchen customer'})
        cls.portal_user = new_test_user(cls.env, 'kitchen_portal', groups='base.group_portal')
        cls.lines = [
            {'ref': 'test-base-600', 'productName': 'Base 600', 'name': 'Base 600 — 600 × 720 × 560 mm',
             'quantity': 1, 'unit': 'u', 'priceUnit': 250.0},
            {'ref': 'test-worktop', 'productName': 'Worktop', 'name': 'Worktop A', 'quantity': 1.5, 'unit': 'm²', 'priceUnit': 120.0},
        ]

    def test_sales_quote_creates_products_and_keeps_manual_lines(self):
        order = self.env['sale.order'].with_user(self.salesman).create({'partner_id': self.partner.id})
        order.action_open_kitchen_configurator()
        design = order.kitchen_design_id
        self.assertTrue(design)
        manual = self.env['sale.order.line'].create({
            'order_id': order.id, 'product_id': self.env.ref('kitchen_configurator.product_kitchen_item').id,
            'name': 'Manual line', 'price_unit': 10,
        })
        result = design.with_user(self.salesman)._apply_quote(self.lines, SNAPSHOT)
        self.assertEqual(result['name'], order.name)
        generated = order.order_line.filtered(lambda l: l.kitchen_generated and not l.display_type)
        self.assertEqual(len(generated), 2)
        self.assertEqual(generated.product_id.mapped('kitchen_ref'), ['test-base-600', 'test-worktop'])
        self.assertEqual(generated[0].price_unit, 250.0)
        # Second send replaces generated lines only and reuses the products.
        design.with_user(self.salesman)._apply_quote(self.lines[:1], SNAPSHOT)
        self.assertIn(manual, order.order_line)
        self.assertEqual(len(order.order_line.filtered(lambda l: l.kitchen_generated and not l.display_type)), 1)
        self.assertEqual(self.env['product.product'].search_count([('kitchen_ref', '=', 'test-base-600')]), 1)
        self.assertEqual(design.data, SNAPSHOT)

    def test_confirmed_order_is_not_modified(self):
        design = self.env['kitchen.design'].create({'partner_id': self.partner.id})
        design._apply_quote(self.lines, SNAPSHOT)
        first = design.sale_order_id
        first.action_confirm()
        design._apply_quote(self.lines, SNAPSHOT)
        self.assertNotEqual(design.sale_order_id, first)
        self.assertEqual(design.sale_order_count, 2)

    def test_portal_request_uses_fallback_product(self):
        design = self.env['kitchen.design'].with_user(self.portal_user)._create_portal_design('My kitchen')
        self.assertEqual(design.partner_id, self.portal_user.partner_id)
        design.with_user(self.portal_user).check_access('read')
        design.with_user(self.portal_user).sudo()._apply_quote(self.lines, SNAPSHOT, portal=True)
        fallback = self.env.ref('kitchen_configurator.product_kitchen_item')
        products = design.sale_order_id.order_line.filtered(lambda l: not l.display_type).product_id
        self.assertEqual(products, fallback)
        self.assertEqual(design.state, 'requested')

    def test_invalid_payloads(self):
        design = self.env['kitchen.design'].create({'partner_id': self.partner.id})
        with self.assertRaises(ValidationError):
            design._save_snapshot({'version': 99})
        with self.assertRaises(ValidationError):
            design._apply_quote([{'ref': 'x', 'name': 'x', 'quantity': -1, 'priceUnit': 1}], SNAPSHOT)

    def test_drawing_is_stored_and_printed(self):
        design = self.env['kitchen.design'].create({'partner_id': self.partner.id})
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10"/></svg>'
        drawing = {
            'plan': svg,
            'elevations': [{'title': 'Vue de face — Mur A', 'svg': svg}],
            'rows': [{'mark': 1, 'name': 'Base 600', 'wall': 'Mur A', 'offset': 0, 'elevation': 0, 'width': 600, 'height': 870, 'depth': 560}],
            'worktops': [],
            'labels': {'topView': 'Vue de dessus', 'schedule': 'Répartition des caissons'},
        }
        design._save_snapshot(SNAPSHOT, drawing)
        self.assertTrue(design.has_drawing)
        self.assertEqual(len(design._drawing_report_values()['views']), 2)
        html = self.env['ir.actions.report']._render_qweb_html('kitchen_configurator.report_kitchen_drawing', design.ids)[0]
        self.assertIn(b'Base 600', html)
        self.assertIn(b'data:image/svg+xml;base64,', html)
        # A malformed drawing is dropped, the project is still saved.
        design._save_snapshot(SNAPSHOT, {'plan': '<script>alert(1)</script>', 'elevations': [], 'rows': [], 'labels': {}})
        self.assertFalse(design.has_drawing)

    def test_wardrobe_project_type_and_detail(self):
        design = self.env['kitchen.design'].create({'partner_id': self.partner.id})
        snapshot = dict(SNAPSHOT, kitchen={'name': 'Dressing', 'projectType': 'wardrobe'})
        svg = '<svg xmlns="http://www.w3.org/2000/svg"/>'
        drawing = {
            'plan': svg, 'elevations': [], 'worktops': [], 'labels': {'detail': 'Détail'},
            'rows': [{'mark': 1, 'name': 'Armoire coulissante', 'wall': 'Mur A', 'offset': 0, 'elevation': 0,
                      'width': 2400, 'height': 2400, 'depth': 650, 'detail': 'coulissante, 3 vantaux · portes : Miroir'}],
        }
        design._apply_quote(self.lines[:1], snapshot, drawing=drawing)
        self.assertEqual(design.project_type, 'wardrobe')
        self.assertTrue(design.sale_order_id.order_line.filtered(lambda l: l.display_type == 'line_section').name.startswith('Wardrobe'))
        self.assertEqual(design._configurator_config('sales')['projectType'], 'wardrobe')
        html = self.env['ir.actions.report']._render_qweb_html('kitchen_configurator.report_kitchen_drawing', design.ids)[0]
        self.assertIn('3 vantaux'.encode(), html)
