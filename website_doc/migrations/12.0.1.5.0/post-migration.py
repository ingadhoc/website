

def migrate(cr, version):
    cr.execute("""
        UPDATE website_doc_toc SET title_view_type = 'kanban' WHERE dont_show_childs = TRUE
    """)
