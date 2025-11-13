from src.core.base.base_web import BaseWeb

class PaymentDonePage(BaseWeb):
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        
        # Order success elements
        self.order_success_message = self.get_element('div.alert-success.alert')
        self.order_number = self.get_element('div.alert-success.alert p')
        self.download_invoice_button = self.get_element('a:has-text("Download Invoice")')
        self.continue_button = self.get_element('a:has-text("Continue")')
        
    def get_order_success_message(self):
        """Get order success message"""
        try:
            return self.order_success_message.text_content()
        except:
            return None
    
    def get_order_number(self):
        """Get order number from success message"""
        try:
            message = self.order_success_message.text_content()
            # Extract order number from message
            import re
            order_match = re.search(r'Order #(\d+)', message)
            if order_match:
                return order_match.group(1)
            return None
        except:
            return None
    
    def download_invoice(self):
        """Click download invoice button"""
        self.download_invoice_button.click()
    
    def continue_shopping(self):
        """Click continue button"""
        self.continue_button.click()
