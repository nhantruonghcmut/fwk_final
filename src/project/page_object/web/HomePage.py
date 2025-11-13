from src.project.page_object.web.BasePage import BasePage
from src.project.page_object.web.components.footerComponent import Footer
from src.project.page_object.web.components.headerComponent import Header
from src.project.page_object.web.components.productSection import ProductSection
from src.core.utils.web_action import WebActions 
import time
class HomePage(BasePage):

    def __init__(self, page):
        super().__init__(page) 
        self.footer = Footer(page)
        self.header = Header(page)
        self.product_section = ProductSection(page)
        self.web_actions = WebActions(page)
        self.sign_up_login_button = "a[href='/login']"
        self.homeLink = self.get_element('a >> text="Home"')
        self.productsLink = self.get_element('a >> text="Products"')
        self.cartLink = self.get_element('a >> text="Cart"')
        
        self.testCasesLink = self.get_element('a >> text="Test Cases"')
        self.apiTestingLink = self.get_element('a >> text="API Testing"')
        self.videoTutorialsLink = self.get_element('a >> text="Video Tutorials"')
        self.contactUsLink = self.get_element('a >> text="Contact us"')
        self.loggedInAsText = self.get_element('a >> text="Logged in as "')
        self.logoutLink = self.get_element('a >> text="Logout"')
        self.deleteAccountLink = self.get_element('a >> text="Delete Account"')
        self.accountDeletedMessage = self.get_element('h2.title >> text="Account Deleted!"')
        self.continueButton = self.get_element('[data-qa="continue-button"]')
        self.loginLink = self.get_element('a >> text="Signup / Login"')
    
    def navigate(self, url):
        """Navigate with comprehensive error handling"""
        retries = 3
        retry_delay = 2000  # ms
        
        for attempt in range(retries):
            try:
                # Set longer timeout for slow connections
                self.navigate_to(
                    url, 
                    wait_until="domcontentloaded",
                    timeout=30000 
                )
                
                # Wait for critical element to ensure page is ready
                # self.page.wait_for_load_state("networkidle", timeout=30000)
                self.wait_for_element(self.sign_up_login_button, timeout=15000)
                
                print(f"✓ Successfully loaded {self.url}")
                
            except Exception as e:
                print(f"✗ Attempt {attempt + 1}/{retries} failed: {str(e)}")
                time.sleep(retry_delay / 1000)  # Convert ms to seconds

    def navigate_to_home(self):
        self.header.home.click()
    def navigate_to_login(self):
        self.header.login.click()
    def navigate_to_cart(self):
        self.header.cart.click()
    def navigate_to_logout(self):
        self.header.logout.click()
    def navigate_to_delete_account(self):
        self.header.deleteAccount.click()
    def isUserLoggedIn(self,username):
        """Check if user is logged in with given username"""
        try:
            return self.verify_text_present(f'Logged in as {username}')
        except Exception:
            return False
    def verifyAccountDeleted(self):
        """Verify if the account deletion was successful"""
        return self.accountDeletedMessage.is_visible()

    # def navigate_to_test_cases(self):
    #     self.testCasesLink.click()
    # def navigate_to_api_testing(self):
    #     self.apiTestingLink.click()
    # def navigate_to_video_tutorials(self):
    #     self.videoTutorialsLink.click()
    # def navigate_to_contact_us(self):
    #     self.contactUsLink.click()
