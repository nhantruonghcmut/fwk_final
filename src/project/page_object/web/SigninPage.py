from src.project.page_object.web.BasePage import BasePage
from src.project.page_object.web.components.footerComponent import Footer
from src.project.page_object.web.components.headerComponent import Header
class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)       
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
   
    def perform_login(self, email, password):
        """Perform login with email and password"""
        self.login_email.fill(email)
        self.login_password.fill(password)
        self.login_button.click()
    
    def get_login_error_message(self):
        """Get login error message if present"""
        try:
            return self.login_error_message.get_text()
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




