from src.core.base.base_web import BaseWeb

class CheckOutPage(BaseWeb):
    def __init__(self, page, base_url):
        super().__init__(page)
        self.page = page
        self.base_url = base_url
        self.cart_items_table = self.get_element('div.cart_info#cart_info table')
        self.comment_section = self.get_element('div#ordermsg')
        self.proceed_to_checkout_button = self.get_element('a[href*="payment"]:has-text("Place Order")')

    def get_total_amount(self):
        total_amount_element = self.cart_items_table.get_element('td p.cart_total_price')
        return int(total_amount_element.get_text().replace('Rs.', '').strip())

    def get_comment(self):
        return self.comment_section.get_text()

    def leave_comment(self, comment):
        self.comment_section.fill(comment)

    def place_order(self):
        self.proceed_to_checkout_button.click()
