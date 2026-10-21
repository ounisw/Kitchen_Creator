from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class KitchenPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'kitchen_design_count' in counters:
            Design = request.env['kitchen.design']
            values['kitchen_design_count'] = Design.search_count([]) if Design.has_access('read') else 0
        return values

    @http.route('/my/kitchen', type='http', auth='user', website=True)
    def portal_my_kitchen(self, **kwargs):
        Design = request.env['kitchen.design']
        designs = Design.search([]) if Design.has_access('read') else Design
        values = self._prepare_portal_layout_values()
        values.update({
            'designs': designs,
            'page_name': 'kitchen_design',
            'can_create': request.env.user._is_portal(),
        })
        return request.render('kitchen_configurator.portal_my_kitchen', values)

    @http.route('/my/kitchen/new', type='http', auth='user', methods=['POST'], website=True)
    def portal_kitchen_new(self, name=None, project_type='kitchen', **kwargs):
        if not request.env.user._is_portal():
            return request.redirect('/my/kitchen')
        design = request.env['kitchen.design']._create_portal_design(name, project_type)
        return request.redirect(f'/kitchen/configurator/{design.id}')
