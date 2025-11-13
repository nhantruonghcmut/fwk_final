from src.core.base.base_web import BaseWeb
from src.project.page_object.web.components.headerComponent import Header
from src.project.page_object.web.components.footerComponent import Footer

class BasePage(BaseWeb):
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        self.header = Header(page)
        self.footer = Footer(page)

    def goto_home(self):
        self.header.home.click()

    def navigate_to_product(self):
        self.header.products.click()

    def navigate_to_cart(self):
        self.header.cart.click()

    def navigate_to_login(self):
        self.header.login.click()

    def navigate_to_test_case(self):
        self.header.testcase.click()

    def navigate_to_api_testing(self):
        self.header.apiTesting.click()

    def navigate_to_contact_us(self):
        self.header.contactUs.click()

    def navigate_to_video_tutorials(self):
        self.header.videoTutorial.click()

    def take_subscription(self, email):
        self.footer.subscription_input.fill(email)
        self.footer.subscribe_button.click()