from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_reward_line(self, program):
        for rec in self.order_line:
            rec.write({
                'discount':program.discount_percentage
                })

class SaleCouponApplyCode(models.TransientModel):
    _inherit = 'sale.coupon.apply.code'

    def apply_coupon(self, order, coupon_code):
        res=super(SaleCouponApplyCode, self).apply_coupon(order, coupon_code)
        order.applied_coupon_ids=None
        return res
