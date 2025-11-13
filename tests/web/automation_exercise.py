# """
# Test cases for Automation Exercise website
# Includes: Signup, Login, Signout, and Delete Account tests
# """
# import time
# import pytest
# import allure
# from src.project.page_object.web.automation_exercise import AutomationExercise_HOME, AutomationExercise_LOGIN
# from src.project.page_object.web.BasePage import BasePage



# class AutomationExercise:
#     """Test class for Automation Exercise website functionality"""
    
#     @allure.feature("User Registration")
#     @allure.story("User Signup")
#     @allure.severity(allure.severity_level.CRITICAL)

#     @pytest.mark.automation_exercise
#     def test_signup(self, browser, base_urls, data_test_signup):
#         """Test user signup with valid data"""
#         # Get test data
#         data = data_test_signup
#         print(f"Using signup test data: {data}")

       
#         # Initialize page objects
#         home_page = AutomationExercise_HOME(browser)
        
#         try:
#             home_page.navigate()
            
#             # Navigate to signup page
#             home_page.navigate_to_login()
#             login_page = AutomationExercise_LOGIN(browser)
#             # Fill signup form
#             login_page.configure_signup_form(data['signup_name'], data['signup_email'])
        
#             login_page.click_signup_button()
            
#             # Complete registration
#             # assert login_page.verify_text_present("Account Created!")
#             login_page.fill_signup_form(data['form_data'])
#             login_page.click_continue_button()            
#             # Verify signup success
#             home_page = AutomationExercise_HOME(browser)
#             assert home_page.isUserLoggedIn(data['signup_name'])
#             home_page.take_screenshot({data["test_id"]})
#             home_page.navigate_to_delete_account()
#             time.sleep(2)  # Wait for 2 seconds before taking the screenshot
#         except Exception as e:
#             # Take screenshot manually on exception
#             browser.screenshot(path=f"reports/screenshots/error_{data['test_id']}.png")
#             raise e  # Re-raise the exception after taking screenshot
#     # ==================== LOGIN TESTS ====================
    
#     # @allure.feature("User Authentication")
#     # @allure.story("User Login")
#     # @allure.severity(allure.severity_level.CRITICAL)

#     # @pytest.mark.automation_exercise
#     # @pytest.mark.parametrize("test_data_item", [
#     #     "login_001",
#     #     "login_002",
#     #     "login_003",
#     #     "login_004",
#     #     "login_005",
#     # ])
#     # def test_login(self, browser, test_data_item):
#     #     """Test user login with various scenarios"""
#     #     # Get test data
#     #     test_data = self.test_data['automation_exercise_testdata']['login_test_data']
#     #     data = next((item for item in test_data if item['test_id'] == test_data_item), None)
        
#     #     # Initialize page objects
#     #     home_page = AutomationExercise_HOME(browser)
#     #     login_page = AutomationExercise_LOGIN(browser)
        
#     #     # Navigate to login page
#     #     home_page.navigate_to_login()
        
#     #     # Perform login
#     #     login_page.perform_login(data['email'], data['password'])
        
#     #     # Verify result
#     #     if data['expected_result'] == 'success':
#     #         assert home_page.isUserLoggedIn(data['username'])
#     #     else:
#     #         error_message = login_page.get_login_error_message()
#     #         assert data['error_message'] in error_message
    
#     # # ==================== SIGNOUT TESTS ====================
    
#     # @allure.feature("User Authentication")
#     # @allure.story("User Signout")
#     # @allure.severity(allure.severity_level.NORMAL)

#     # # @pytest.mark.regression
#     # @pytest.mark.parametrize("test_data_item", [
#     #     "signout_001",
#     #     "signout_002",
#     #     "signout_003",
#     #     "signout_004",
#     #     "signout_005",
#     # ])
#     # def test_signout(self, browser, test_data_item):
#     #     """Test user signout functionality"""
#     #     # Get test data
#     #     test_data = self.test_data['automation_exercise_testdata']['signout_test_data']
#     #     data = next((item for item in test_data if item['test_id'] == test_data_item), None)
        
#     #     # Initialize page objects
#     #     home_page = AutomationExercise_HOME(browser)
#     #     login_page = AutomationExercise_LOGIN(browser)
        
#     #     # Login first
#     #     home_page.navigate_to_login()
#     #     login_page.perform_login(data['email'], data['password'])
#     #     assert home_page.isUserLoggedIn(data['username'])
        
#     #     # Perform logout
#     #     home_page.navigate_to_logout()
        
#     #     # Verify logout
#     #     assert "/login" in browser.url
    
#     # # ==================== DELETE ACCOUNT TESTS ====================
    
#     # @allure.feature("User Management")
#     # @allure.story("Delete Account")
#     # @allure.severity(allure.severity_level.CRITICAL)

#     # # @pytest.mark.regression
#     # @pytest.mark.parametrize("test_data_item", [
#     #     "delete_001",
#     #     "delete_002",
#     #     "delete_003",
#     #     "delete_004",
#     #     "delete_005",
#     # ])
#     # def test_delete_account(self, browser, test_data_item):
#     #     """Test account deletion functionality"""
#     #     # Get test data
#     #     test_data = self.test_data['automation_exercise_testdata']['delete_test_data']
#     #     data = next((item for item in test_data if item['test_id'] == test_data_item), None)
        
#     #     # Initialize page objects
#     #     home_page = AutomationExercise_HOME(browser)
#     #     login_page = AutomationExercise_LOGIN(browser)
        
#     #     # Create account
#     #     home_page.navigate_to_login()
#     #     login_page.configure_signup_form(
#     #         data['signup_data']['signup_name'],
#     #         data['signup_data']['signup_email']
#     #     )
#     #     login_page.click_signup_button()
#     #     login_page.fill_signup_form(data['signup_data']['form_data'])
        
#     #     # Delete account
#     #     home_page.navigate_to_delete_account()
        
#     #     # Verify deletion
#     #     assert "account_deleted" in browser.url or "ACCOUNT DELETED" in browser.content()
