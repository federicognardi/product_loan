from odoo import models, fields, api
from odoo import _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_loan_line_ids = fields.One2many('product.loan.line', 'product_id', string='Product Loan Lines')
    is_loaned = fields.Boolean(string='Is Loaned', compute='_compute_is_loaned', store=True)

    @api.depends('product_loan_line_ids.loan_id.state')
    def _compute_is_loaned(self):
        for product in self:
            loan_lines = self.env['product.loan.line'].search([('product_id', '=', product.id), ('loan_id.state', '=', 'loaned')])
            product.is_loaned = bool(loan_lines)

class ProductLoan(models.Model):
    _name = 'product.loan'
    _description = 'Product Loan'

    name = fields.Char(string='Loan Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    loan_date = fields.Date(string='Loan Date', required=True, default=fields.Date.context_today)
    location = fields.Many2one('stock.location', string='Location', required=True, help='Location where the products will be used')
    expected_return_date = fields.Date(string='Expected Return Date', required=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('loaned', 'Loaned'),
            ('partial_return', 'Partial Return'),
            ('returned', 'Returned'),
            ('cancelled', 'Cancelled')
        ], default='draft', string='Status')
    product_loan_line_ids = fields.One2many('product.loan.line', 'loan_id', string='Loan Lines')

    def action_confirm_loan(self):
        for loan in self:
            # Create an inventory move for each loan line
            for line in loan.product_loan_line_ids:
                self.env['stock.move'].create({
                    'name': f'Product Loan: {loan.partner_id.name}',
                    'product_id': line.product_id.id,
                    'product_uom': line.uom_id.id,
                    'product_uom_qty': line.quantity,
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': loan.location.id,
                    'state': 'done',
                })
            # Change the loan's state to "Loaned"
            loan.write({'state': 'loaned'})

    @api.model
    def action_return_products(self):
        # Obtenga el ID del registro actual
        #loan_id = self.id

        self.ensure_one()
        view_id = self.env.ref('product_loan.product_return_form_view').id
        return {
            'name': _('Return Products'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.return',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_product_loan_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_location': self.location,
            },
        }

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('product.loan') or _('New')
        result = super(ProductLoan, self).create(vals)
        return result

class ProductLoanLine(models.Model):
    _name = 'product.loan.line'
    _description = 'Product Loan Line'

    loan_id = fields.Many2one('product.loan', string='Loan', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    returned_quantity = fields.Float(string='Returned Quantity', default=0.0)  # Agrega esta línea
    uom_id = fields.Many2one(related='product_id.uom_id', string='Unit of Measure', readonly=True)

