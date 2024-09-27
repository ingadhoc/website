from openupgradelib import openupgrade
import logging
logger = logging.getLogger(__name__)

@openupgrade.migrate()
def migrate(env, version):

    # Desactivamos temporalmente el noupdate para la vista
    env.cr.execute("""
        UPDATE ir_model_data
        SET noupdate = FALSE
        WHERE module = 'website_sale_prod_description' 
        AND model = 'ir.ui.view'
        AND name = 'product_description'
        AND noupdate = TRUE;
    """)

    logger.info('Forzamos la actualización de la vista de product_template_templates en módulo website_sale_prod_description')
    openupgrade.load_data(env.cr, 'website_sale_prod_description', 'views/product_template_templates.xml')
