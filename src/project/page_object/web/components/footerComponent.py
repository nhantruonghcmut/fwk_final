from src.core.base.base_web import BaseWeb
import src.core.utils.element_object as ElementObject
class Footer(BaseWeb):
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        self.root = self.get_element('footer')
        self.subscription_input = self.root.get_element('input[type="email"]')
        self.subscribe_button = self.root.get_element('button[type="submit"]')

    def subscribe(self, email):
        self.subscription_input.fill(email)
        self.subscribe_button.click()