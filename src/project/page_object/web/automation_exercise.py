from src.core.base.base_web import BaseWeb
from src.core.utils.web_action import WebActions

class AutomationExercise_HOME(BaseWeb):
    def __init__(self, page):
        super().__init__(page)
        self.url = "https://automationexercise.com"
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
    
    def navigate(self):
        """Navigate with comprehensive error handling"""
        retries = 3
        retry_delay = 2000  # ms
        
        for attempt in range(retries):
            try:
                # Set longer timeout for slow connections
                self.page.goto(
                    self.url, 
                    wait_until="domcontentloaded",
                    timeout=30000  # Increased timeout
                )
                
                # Wait for critical element to ensure page is ready
                # self.page.wait_for_load_state("networkidle", timeout=30000)
                self.page.wait_for_selector(self.sign_up_login_button, timeout=15000)
                
                print(f"[OK] Successfully loaded {self.url}")

                
            except Exception as e:
                print(f"[ERROR] Attempt {attempt + 1}/{retries} failed: {str(e)}")

        


    def navigate_to_home(self):
        self.homeLink.click()
    def navigate_to_login(self):
        self.loginLink.click()
    def navigate_to_cart(self):
        self.cartLink.click()
    def navigate_to_test_cases(self):
        self.testCasesLink.click()
    def navigate_to_api_testing(self):
        self.apiTestingLink.click()
    def navigate_to_video_tutorials(self):
        self.videoTutorialsLink.click()
    def navigate_to_contact_us(self):
        self.contactUsLink.click()
    def navigate_to_logout(self):
        self.logoutLink.click()
    def navigate_to_delete_account(self):
        self.deleteAccountLink.click()
    def isUserLoggedIn(self,username):
        """Check if user is logged in with given username"""
        try:
            return self.verify_text_present(f'Logged in as {username}')
        except Exception:
            return False

class AutomationExercise_LOGIN(BaseWeb):
    def __init__(self, page):
        super().__init__(page)
        self.url = "https://automationexercise.com/login"
        
        # Login form elements
        self.login_header = self.get_element('div.login-form h2')
        self.login_email = self.get_element('div.login-form input[data-qa="login-email"]')
        self.login_password = self.get_element('div.login-form input[data-qa="login-password"]')
        self.login_button = self.get_element('div.login-form button[data-qa="login-button"]')
        self.login_error_message = self.get_element('div.login-form p')
        
        # Signup form elements
        self.new_user_signup_header = self.get_element('div.signup-form>h2')
        self.new_user_signup_name = self.get_element('div.signup-form input[data-qa="signup-name"]')
        self.new_user_signup_email = self.get_element('div.signup-form input[data-qa="signup-email"]')
        self.new_user_signup_button = self.get_element('div.signup-form button[type="submit"]')

        """
        New Signup Page 2
        """
        ##Top Section
        self.signup_header = self.get_element('div.login-form h2:nth-child(1)')
        self.signup_title_mr = self.get_element('div.radio-inline input[value="Mr"]')
        self.signup_title_mrs = self.get_element('div.radio-inline input[value="Mrs"]')
        self.signup_name = self.get_element('input#name')
        self.signup_email = self.get_element('input#email')
        self.signup_password = self.get_element('input#password')
        self.dob_day = self.get_element('select#days')
        self.dob_month = self.get_element('select#months')
        self.dob_year = self.get_element('select#years')
        self.signup_newsletter = self.get_element('input[type="checkbox"]#newsletter')
        self.signup_offers = self.get_element('input[type="checkbox"]#optin')

        ##Address Section
        self.first_name = self.get_element('input#first_name')
        self.last_namme = self.get_element('input#last_name')
        self.company = self.get_element('input#company')
        self.add1 = self.get_element('input#address1')
        self.add2 = self.get_element('input#address2')
        self.country = self.get_element('select#country')
        self.state = self.get_element('input#state')
        self.city = self.get_element('input#city')
        self.zip = self.get_element('input#zipcode')
        self.phone = self.get_element('input#mobile_number')
        self.create_button = self.get_element('button:has-text("Create Account")')
        self.continue_button = self.get_element('[data-qa="continue-button"]')

    def get_header(self):
        return self.get_page_title()

    def navigate_to(self):
        self.page.goto(self.url, wait_until="domcontentloaded")
    
    def perform_login(self, email, password):
        """Perform login with email and password"""
        self.login_email.fill(email)
        self.login_password.fill(password)
        self.login_button.click()
    
    def get_login_error_message(self):
        """Get login error message if present"""
        try:
            return self.login_error_message.text_content()
        except:
            return None

    def configure_signup_form(self, username, email):
        self.new_user_signup_name.fill(username)
        self.new_user_signup_email.fill(email)
    
    def click_signup_button(self):
        """Click the signup button"""
        self.new_user_signup_button.click()

    def click_continue_button(self):
        """Click the continue button"""
        self.continue_button.click()

    def fill_signup_form(self, signup_form_data):
        #Fill in the data sequentially
        if (signup_form_data["Title"]) == "Mr.":
            self.signup_title_mr.click()
        elif (signup_form_data["Title"] == "Mrs."):
            self.signup_title_mrs.click()

        self.signup_name.fill(signup_form_data["Name"])
        self.signup_password.fill(signup_form_data["Password"])

        self.dob_day.select_option(value=f'{signup_form_data["DOB"][0]}')
        self.dob_month.select_option(value=f'{signup_form_data["DOB"][1]}')
        self.dob_year.select_option(value=f'{signup_form_data["DOB"][2]}')

        self.signup_newsletter.click()
        self.signup_offers.click()

        #Address section of the form
        self.first_name.fill(signup_form_data["FirstName"])
        self.last_namme.fill(signup_form_data["LastName"])
        self.company.fill(signup_form_data["Company"])
        self.add1.fill(signup_form_data["Address"]["Add1"])
        self.add2.fill(signup_form_data["Address"]["Add2"])
        self.country.select_option(value=f'{signup_form_data["Address"]["Country"]}')
        self.state.fill(signup_form_data["Address"]["State"])
        self.city.fill(signup_form_data["Address"]["City"])
        self.zip.fill(signup_form_data["Address"]["Code"])
        self.phone.fill(signup_form_data["Phone"])

        self.create_button.click()




