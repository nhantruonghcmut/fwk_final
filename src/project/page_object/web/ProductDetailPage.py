from src.core.base.base_web import BaseWeb

class ProductDetailPage(BaseWeb):
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        
        # Product information elements
        self.product_name = self.get_element('div.product-information h2')
        self.product_category = self.get_element('div.product-information p:has-text("Category:")')
        self.product_price = self.get_element('div.product-information span span')
        self.product_availability = self.get_element('div.product-information p:has-text("Availability:")')
        self.product_condition = self.get_element('div.product-information p:has-text("Condition:")')
        self.product_brand = self.get_element('div.product-information p:has-text("Brand:")')
        
        # Quantity and add to cart
        self.quantity_input = self.get_element('input#quantity')
        self.add_to_cart_button = self.get_element('button:has-text("Add to cart")')
        
        # Review section
        self.review_name_input = self.get_element('input#name')
        self.review_email_input = self.get_element('input#email')
        self.review_textarea = self.get_element('textarea#review')
        self.review_submit_button = self.get_element('button#button-review')
        self.review_success_message = self.get_element('div.alert-success.alert')
        
        # View cart modal
        self.view_cart_button = self.get_element('div.modal-content a:has-text("View Cart")')
        self.continue_shopping_button = self.get_element('div.modal-content button:has-text("Continue Shopping")')
        
    def get_product_name(self):
        """Get product name"""
        return self.product_name.text_content()
    
    def get_product_price(self):
        """Get product price"""
        return self.product_price.text_content()
    
    def get_product_category(self):
        """Get product category"""
        return self.product_category.text_content()
    
    def set_quantity(self, quantity):
        """Set product quantity"""
        self.quantity_input.fill(str(quantity))
    
    def add_to_cart(self):
        """Add product to cart"""
        self.add_to_cart_button.click()
    
    def submit_review(self, name, email, review_text):
        """Submit product review"""
        self.review_name_input.fill(name)
        self.review_email_input.fill(email)
        self.review_textarea.fill(review_text)
        self.review_submit_button.click()
    
    def get_review_success_message(self):
        """Get review success message"""
        try:
            return self.review_success_message.text_content()
        except:
            return None
    
    def view_cart_from_modal(self):
        """Click View Cart button in modal"""
        self.view_cart_button.click()
    
    def continue_shopping_from_modal(self):
        """Click Continue Shopping button in modal"""
        self.continue_shopping_button.click()
