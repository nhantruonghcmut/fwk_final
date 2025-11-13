# """
# Test cases for Automation Exercise website
# Includes: Signup, Login, Signout, and Delete Account tests
# """
# import time
# import pytest
# import allure
# from conftest import test_listener
# from src.project.page_object.web.automation_exercise import AutomationExercise_HOME, AutomationExercise_LOGIN
# from src.project.page_object.web.HomePage import HomePage
# from src.project.page_object.web.SigninPage import LoginPage

# from src.project.page_object.web.BasePage import BasePage



# class TestSignUpAndSignIn:
#     """Test class for Automation Exercise website functionality"""
    
#     @allure.feature("User Registration")
#     @allure.story("User Signup")
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.automation_exercise
#     @allure.suite("Test signup feature")
#     def test_signup(self, browser, app_urls, data_test_signup, request):
#         """Test user signup with valid data"""
#         data = data_test_signup
#         allure.dynamic.title(data.get("test_name", "User Signup"))
#         allure.dynamic.description(f"Test ID: {data.get('test_id')}<br>Email: {data.get('signup_email')}<br>Name: {data.get('signup_name')}")
#         allure.dynamic.label("test_id", data.get("test_id"))
#         home_page = HomePage(browser)
#         try:
#             with allure.step("Navigate to home page"):
#                 home_page.navigate(app_urls['automation_excercise'])
#             with allure.step("Go to signup/login page"):
#                 home_page.navigate_to_login()
#                 login_page = LoginPage(browser)
#             with allure.step("Fill signup form"):
#                 login_page.configure_signup_form(data['signup_name'], data['signup_email'])
#                 if hasattr(home_page, "take_screenshot"):
#                     screenshot_path = home_page.take_screenshot(f"{data['test_id']}_fill_form")
#                     if screenshot_path:
#                         allure.attach.file(screenshot_path, name="Filled Signup Form", attachment_type=allure.attachment_type.PNG)
#                 login_page.click_signup_button()
#             with allure.step("Complete registration"):
#                 login_page.fill_signup_form(data['form_data'])
#                 login_page.click_continue_button()
#             with allure.step("Verify signup success"):
#                 assert home_page.isUserLoggedIn(data['signup_name']), f"User {data['signup_name']} should be logged in"
#             if hasattr(home_page, "take_screenshot"):
#                 screenshot_path = home_page.take_screenshot(data["test_id"])
#                 if screenshot_path:
#                     allure.attach.file(screenshot_path, name="Signup Screenshot", attachment_type=allure.attachment_type.PNG)
#         except Exception as e:
#             screenshot_path = f"reports/screenshots/error_{data['test_id']}_signup.png"
#             browser.screenshot(path=screenshot_path)
#             allure.attach.file(screenshot_path, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
#             allure.dynamic.label("error", str(e))
#             raise
#     # # ==================== LOGIN TESTS ====================
    
#     @allure.feature("User Authentication")
#     @allure.story("User Login")
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.automation_exercise
#     @allure.suite("Test login - logout feature")
#     def test_login_and_logout(self, browser, app_urls, data_test_login, request):
#         """Test user login with various scenarios"""
#         data = data_test_login
#         allure.dynamic.title(data.get("test_name", "User Login"))
#         allure.dynamic.description(f"Test ID: {data.get('test_id')}<br>Email: {data.get('email')}<br>Username: {data.get('username')}")
#         allure.dynamic.label("test_id", data.get("test_id"))
#         home_page = HomePage(browser)
#         login_page = LoginPage(browser)
#         try:
#             with allure.step("Navigate to home page"):
#                 home_page.navigate(app_urls['automation_excercise'])
#             with allure.step("Go to login page"):
#                 home_page.navigate_to_login()
#             with allure.step("Perform login"):
#                 login_page.perform_login(data['email'], data['password'])
#             with allure.step("Verify login result"):
#                 if data['expected_result'] == 'success':
#                     assert home_page.isUserLoggedIn(data['username']), f"User {data['username']} should be logged in"
#                     with allure.step("Perform logout"):
#                         home_page.navigate_to_logout()
#                         assert not home_page.isUserLoggedIn(data['username']), f"User {data['username']} should be logged out"
#                         screenshot_path = home_page.take_screenshot(f"{data['test_id']}_logout")
#                 else:
#                     error_message = login_page.get_login_error_message()
#                     assert data['expected_result'] in error_message, f"Expected error message: {data['error_message']}"
#             if hasattr(home_page, "take_screenshot"):
#                 screenshot_path = home_page.take_screenshot(data["test_id"])
#                 if screenshot_path:
#                     allure.attach.file(screenshot_path, name="Login Screenshot", attachment_type=allure.attachment_type.PNG)

#         except Exception as e:
#             screenshot_path = f"reports/screenshots/error_{data['test_id']}_login_logout.png"
#             browser.screenshot(path=screenshot_path)
#             allure.attach.file(screenshot_path, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
#             allure.dynamic.label("error", str(e))
#             raise
    