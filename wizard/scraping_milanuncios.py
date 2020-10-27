#-*- encoding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
import time

import requests
from bs4 import BeautifulSoup

class ScrapingMilanuncios(models.TransientModel):
    _name = 'scraping.milanuncios'

    search_ad = fields.Char('Search ad')  
    
    def get_content_page(self):       
        url = "https://www.milanuncios.com/anuncios/"+self.search_ad+".htm"
        page = ''
        while page == '':
            try:
                page = requests.get(url)
                return page.content
                break
            except:
               
                time.sleep(2)
                
                continue

    def create_products(self):
        products = self.env['product.product']
        if not self.search_ad:
            raise UserError(_('search is required'))

       

        soup = BeautifulSoup(self.get_content_page(), "html.parser")
        ofertas = soup.find_all(class_="aditem-detail")
        for oferta in ofertas:  
            title_class = oferta.find(class_="aditem-detail-title") 
            price_class = oferta.find(class_="aditem-price")    
            title = title_class.text    
          
            lst_price = 0
            try:
                price = price_class.getText()
                price = price.replace('€','')
                price = price.replace('.','')
                lst_price = float(price)
                print('lst_price: ', lst_price)
            except Exception as e:
                pass
            
            product = self.env['product.product'].create({'type' : 'service', 'name' : title, 'lst_price' : lst_price})
            products += product

        return {    "type": "ir.actions.act_window",
                    'name': _("Products"),
                    "res_model": "product.template",
                    "views": [(self.env.ref('product.product_template_tree_view').id, 'tree'), (self.env.ref('product.product_template_only_form_view').id, 'form')],
                    "domain": [('id', 'in', products.ids)]
                    }
    
    
        

    