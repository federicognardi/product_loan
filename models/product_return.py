from odoo import models, fields, api
from odoo import _



class ProductReturn(models.Model):
    _name = 'product.return'
    _description = 'Product Return'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    loan_id = fields.Many2one('product.loan', string='Loan', compute='_compute_loan_id', store=True)
    return_line_ids = fields.One2many('product.return.line', 'return_id', string='Return Lines', required=True)
    return_date = fields.Date(string='Return Date', required=True, default=fields.Date.context_today)


    @api.depends('return_line_ids.loan_line_id')
    def _compute_loan_id(self):
        for record in self:
            loan_ids = record.return_line_ids.mapped('loan_line_id.loan_id')
            if loan_ids:
                record.loan_id = loan_ids[0]
            else:
                record.loan_id = False

    def create_return(self):
        for line in self.return_line_ids:
            line.create_return_line()
        for loan in self.loan_ids:
            if self._check_all_products_returned(loan):
                loan.state = 'returned'
            else:
                loan.state = 'partial_return'
        return {'type': 'ir.actions.act_window_close'}

    def _check_all_products_returned(self, loan):
        all_returned = True
        for line in loan.product_loan_line_ids:
            if line.returned_quantity < line.quantity:
                all_returned = False
                break
        return all_returned
class ProductReturnLine(models.Model):
    _name = 'product.return.line'
    _description = 'Product Return Line'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    loan_line_id = fields.Many2one('product.loan.line', string='Loan Line', required=True)
    return_id = fields.Many2one('product.return', string='Return', required=True)
    loan_line_id = fields.Many2one('product.loan.line', string='Loan Line', required=True)
    loan_id = fields.Many2one(related='loan_line_id.loan_id', string='Loan', readonly=True)


