import json
import os

from werkzeug.exceptions import NotFound

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

APP_INDEX = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'app', 'index.html')


class KitchenConfiguratorController(http.Controller):

    def _get_design(self, design_id):
        """Design readable by the current user, as sudo for portal users (who have read access only)."""
        design = request.env['kitchen.design'].browse(design_id).exists()
        if not design:
            raise NotFound()
        try:
            design.check_access('read')
        except (AccessError, MissingError):
            raise NotFound()
        portal = request.env.user._is_portal()
        if portal:
            return design.sudo(), 'portal'
        if not request.env.user.has_group('sales_team.group_sale_salesman'):
            raise NotFound()
        return design, 'sales'

    @http.route('/kitchen/configurator/<int:design_id>', type='http', auth='user', methods=['GET'])
    def configurator(self, design_id, **kwargs):
        design, audience = self._get_design(design_id)
        try:
            with open(APP_INDEX, encoding='utf-8') as index:
                html = index.read()
        except FileNotFoundError:
            return request.make_response(
                _("The kitchen configurator is not built. Run “npm run build:odoo” in the configurator repository."),
                headers=[('Content-Type', 'text/plain; charset=utf-8')], status=503,
            )
        config = json.dumps(design._configurator_config(audience), ensure_ascii=False)
        # Neutralise "</script>" and similar sequences inside the JSON.
        config = config.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        script = f'<script>window.__KITCHEN_CONFIG__ = {config};</script>'
        html = html.replace('</head>', f'{script}</head>', 1)
        return request.make_response(html, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Cache-Control', 'no-store'),
        ])

    @http.route('/kitchen/api/project/<int:design_id>/save', type='jsonrpc', auth='user', methods=['POST'])
    def save(self, design_id, data=None, drawing=None, **kwargs):
        design, _audience = self._get_design(design_id)
        design._save_snapshot(data, drawing)
        return True

    @http.route('/kitchen/api/project/<int:design_id>/quote', type='jsonrpc', auth='user', methods=['POST'])
    def quote(self, design_id, lines=None, data=None, drawing=None, **kwargs):
        design, audience = self._get_design(design_id)
        return design._apply_quote(lines, data, portal=audience == 'portal', drawing=drawing)
