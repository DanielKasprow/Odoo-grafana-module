from odoo import http
from odoo.http import request


class Grafana(http.Controller):

    @http.route('/statistics/', type='http', auth='user', csrf=False, website=True)
    def get_all_sales(self):
        """
        Funcja sprawdzająca czy użytkownik ma dostęp do jakichkolwiek statystyk, jeśli tak generuje stronę internetowa

        Parameters:
        -----
        access: boolean
            Wartośc logiczna czy użytkownik uzyskał dostęp do strony internetowej

        sales_rec: list of dict
            lista słowników zawierająca wszystkie dane z zamówień  użytkownika

        rec: dict
            słównik zawierająca wszystkie dane z zamówienia  użytkownika

        product_id: int
            zmienna zawierająca id produktu

        Return
        ------
        http.request.render():xml
            Zwraca zapytanie do strony internetowej
        """
        access = False
        sales_rec = request.env['sale.order'].search([])

        for rec in sales_rec:
            if rec.partner_shipping_id.id and rec.state == "sale":
                for product_id in rec.order_line.product_id:
                    if product_id.id == 1 or product_id.id == 2:
                        access = True

        if access:
            #wyświetlanie podstrony z statystykami
            return http.request.render('grafana.grafana_statistics',)
        else:
            #wyświetlanie koszyka
            return http.request.render('website_sale.cart',)