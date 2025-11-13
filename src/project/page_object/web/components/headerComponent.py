from src.core.base.base_web import BaseWeb
class Header(BaseWeb):
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        self.root = self.get_element('header#header')
        self.logo = self.get_element('div.logo.pull-left')
        self.cart = self.get_element('a[href*="cart"]')
        self.login = self.get_element('a[href*="login"]')
        self.testcase = self.get_element('a[href*="testcase"]')
        self.apiTesting = self.get_element('a[href*="apitesting"]')
        self.contactUs = self.get_element('a[href*="contact us"]')
        self.home = self.get_element('a:has-text("Home")')
        self.videoTutorial = self.get_element('a:has-text(" Video Tutorials")')
        self.products = self.get_element('a:has-text("Products")')
        self.logout = self.get_element('a[href*="logout"]')
        self.deleteAccount = self.get_element('a[href*="delete_account"]')