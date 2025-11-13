from src.core.base.base_web import BaseWeb

class PaymentPage(BaseWeb):
    def __init__(self, page, base_url):
        super().__init__(page)
        self.page = page
        self.base_url = base_url
        self.name_on_card_input = self.get_element('[data-qa="name-on-card"]')
        self.card_number_input = self.get_element('[data-qa="card-number"]')
        self.cvc_input = self.get_element('[data-qa="cvc"]')
        self.expiration_month_input = self.get_element('[data-qa="expiry-month"]')
        self.expiration_year_input = self.get_element('[data-qa="expiry-year"]')

    def fill_payment_details(self, name='', card_number='', cvc='', exp_month='', exp_year=''):
        self.name_on_card_input.fill(name)
        self.card_number_input.fill(card_number)
        self.cvc_input.fill(cvc)
        self.expiration_month_input.fill(exp_month)
        self.expiration_year_input.fill(exp_year)

    def confirm_payment(self):
        self.get_element('[data-qa="pay-button"]').click()
