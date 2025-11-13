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


# @allure.feature("User Registration")
# @allure.story("Sign Up Process")
# class TestSignUpV2:
#     @allure.title("User Registration Test")
#     @allure.description("Test user registration functionality with valid data")
#     @allure.severity(allure.severity_level.CRITICAL)
#     @allure.tag("signup", "registration", "smoke")
#     def test_signup(self, browser, app_urls, data_test_signup, request):
#         """
#         Test user signup functionality.
#         Listeners sẽ được gọi tự động thông qua pytest hooks.
#         """
#         data = data_test_signup
#         test_name = data.get("test_name", "User Signup")
        
#         # Set test metadata cho Allure
#         test_listener.set_test_description(f"Test signup for user: {data['signup_name']}")
#         test_listener.set_test_owner("QA Team")
#         test_listener.set_test_severity("critical")
#         test_listener.add_test_tag("signup")
#         test_listener.add_test_tag("registration")
        
#         home_page = HomePage(browser)
        
#         try:
#             # Step 1: Navigate to homepage
#             test_listener.on_step_start("Navigate to homepage")
#             home_page.navigate(app_urls['automation_excercise'])
#             test_listener.on_step_end("Navigate to homepage", "PASSED")
            
#             # Step 2: Navigate to login page
#             test_listener.on_step_start("Navigate to login page")
#             home_page.navigate_to_login()
#             test_listener.on_step_end("Navigate to login page", "PASSED")
            
#             # Step 3: Fill signup form
#             test_listener.on_step_start("Fill signup form")
#             login_page = LoginPage(browser)
#             login_page.configure_signup_form(data['signup_name'], data['signup_email'])
            
#             # Screenshot sẽ được attach vào step "Fill signup form"
#             screenshot_path = home_page.take_screenshot(f"{data['test_id']}_fill_form")
#             test_listener.on_screenshot_taken(screenshot_path, "Filled Signup Form")
            
#             test_listener.on_step_end("Fill signup form", "PASSED")
            
#             # Step 4: Submit signup form
#             test_listener.on_step_start("Submit signup form")
#             login_page.click_signup_button()
#             login_page.fill_signup_form(data['form_data'])
#             login_page.click_continue_button()
#             test_listener.on_step_end("Submit signup form", "PASSED")
            
#             # Step 5: Verify user is logged in
#             test_listener.on_step_start("Verify user login")
#             is_logged_in = home_page.isUserLoggedIn(data['signup_name'])
#             test_listener.on_verification(
#                 "User login verification", 
#                 True, 
#                 is_logged_in, 
#                 is_logged_in
#             )
#             assert is_logged_in, f"User {data['signup_name']} should be logged in"
            
#             # Screenshot sẽ được attach vào step "Verify user login"
#             screenshot_path = home_page.take_screenshot(data["test_id"])
#             test_listener.on_screenshot_taken(screenshot_path, "Signup Success Screenshot")
            
#             test_listener.on_step_end("Verify user login", "PASSED")
            
#             # Add custom metrics
#             test_listener.add_custom_metric("Signup Time", time.time(), "seconds")
#             test_listener.add_custom_metric("User Name", data['signup_name'], "")
            
#         except Exception as e:
#             # Error screenshot sẽ được attach vào step hiện tại hoặc test level
#             screenshot_path = home_page.take_screenshot(f"error_{data['test_id']}_signup")
#             test_listener.on_screenshot_taken(screenshot_path, "Error Screenshot")
            
#             # Log error details
#             test_listener.on_error_occurred(e, "Signup Process")
            
#             # Add error attachment
#             test_listener.add_custom_attachment(
#                 "Error Details", 
#                 str(e), 
#                 "text/plain"
#             )
            
#             raise
    
#     # @allure.title("User Login Test")
#     # @allure.description("Test user login functionality with existing credentials")
#     # @allure.severity(allure.severity_level.CRITICAL)
#     # @allure.tag("login", "authentication", "smoke")
#     # def test_login(self, browser, app_urls, data_test_login, request):
#     #     """
#     #     Test user login functionality.
#     #     Demonstrates advanced listener usage.
#     #     """
#     #     data = data_test_login
#     #     test_name = data.get("test_name", "User Login")
        
#     #     # Set test metadata
#     #     test_listener.set_test_description(f"Test login for user: {data['email']}")
#     #     test_listener.set_test_owner("QA Team")
#     #     test_listener.set_test_severity("high")
#     #     test_listener.add_test_tag("login")
#     #     test_listener.add_test_tag("authentication")
        
#     #     home_page = HomePage(browser)
        
#     #     try:
#     #         # Step 1: Navigate to login page
#     #         test_listener.on_step_start("Navigate to login page")
#     #         home_page.navigate(app_urls['automation_excercise'])
#     #         home_page.navigate_to_login()
#     #         test_listener.on_step_end("Navigate to login page", "PASSED")
            
#     #         # Step 2: Fill login form
#     #         test_listener.on_step_start("Fill login form")
#     #         login_page = LoginPage(browser)
#     #         login_page.fill_login_form(data['email'], data['password'])
            
#     #         # Screenshot sẽ được attach vào step "Fill login form"
#     #         screenshot_path = home_page.take_screenshot(f"{data['test_id']}_login_form")
#     #         test_listener.on_screenshot_taken(screenshot_path, "Login Form Filled")
            
#     #         test_listener.on_step_end("Fill login form", "PASSED")
            
#     #         # Step 3: Submit login
#     #         test_listener.on_step_start("Submit login")
#     #         login_page.click_login_button()
#     #         test_listener.on_step_end("Submit login", "PASSED")
            
#     #         # Step 4: Verify login success
#     #         test_listener.on_step_start("Verify login success")
#     #         is_logged_in = home_page.isUserLoggedIn(data['username'])
#     #         test_listener.on_verification(
#     #             "Login verification", 
#     #             True, 
#     #             is_logged_in, 
#     #             is_logged_in
#     #         )
#     #         assert is_logged_in, f"User should be logged in successfully"
            
#     #         # Screenshot sẽ được attach vào step "Verify login success"
#     #         screenshot_path = home_page.take_screenshot(data["test_id"])
#     #         test_listener.on_screenshot_taken(screenshot_path, "Login Success Screenshot")
            
#     #         test_listener.on_step_end("Verify login success", "PASSED")
            
#     #         # Add test data usage
#     #         test_listener.on_data_used("login_credentials", {
#     #             "email": data['email'],
#     #             "password": "***"  # Masked for security
#     #         })
            
#     #         # Add custom metrics
#     #         test_listener.add_custom_metric("Login Time", time.time(), "seconds")
#     #         test_listener.add_custom_metric("User Email", data['email'], "")
            
#     #     except Exception as e:
#     #         # Error screenshot sẽ được attach vào step hiện tại hoặc test level
#     #         screenshot_path = home_page.take_screenshot(f"error_{data['test_id']}_login")
#     #         test_listener.on_screenshot_taken(screenshot_path, "Login Error Screenshot")
#     #         test_listener.on_error_occurred(e, "Login Process")
#     #         raise
  
    