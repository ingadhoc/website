from openerp import api, models, fields

class search_log(models.Model):
    _name= "website.sale.tracker"

    date=fields.Datetime(string="Date & Time")
    user_id=fields.Many2one("res.users",string="User")
    lang_id=fields.Many2one("res.lang",string="Language")
    search_user=fields.Char(setring="Search")
    category_id=fields.Many2one("product.public.category",string="Category")
    product_id=fields.Many2one("product.template",string="Product")

