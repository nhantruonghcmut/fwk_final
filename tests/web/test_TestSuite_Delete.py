# """
# Test cases for Automation Exercise website
# Includes: Signup, Login, Signout, and Delete Account tests
# """
# import time
# import pytest
# import allure
# from conftest import browser
# from src.project.page_object.web.automation_exercise import AutomationExercise_HOME, AutomationExercise_LOGIN
# from src.project.page_object.web.HomePage import HomePage
# from src.project.page_object.web.SigninPage import LoginPage

# from src.project.page_object.web.BasePage import BasePage


# @allure.parent_suite("Web Automation Excercise Tests")
# class TestSignUpAndSignIn:
#     """Test class for Automation Exercise website functionality"""
#     # ==================== Delete Account TESTS ====================

#     @allure.feature("User Authentication")
#     @allure.story("User Login")
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.automation_exercise
#     @allure.suite("Test delete feature")
#     def test_delete_account(self, browser, app_urls, data_test_delete, request):
#         """Test user account deletion"""
#         data = data_test_delete
#         allure.dynamic.title(data.get("test_name", "User Delete Account"))
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
#             with allure.step("Perform delete account"):
#                 home_page.navigate_to_delete_account()
#                 assert home_page.verifyAccountDeleted()
#                 screenshot_path = home_page.take_screenshot(f"{data['test_id']}_deleted")
#         except Exception as e:
#             screenshot_path = f"reports/screenshots/error_{data['test_id']}_deleteaccount.png"
#             browser.screenshot(path=screenshot_path)
#             allure.attach.file(screenshot_path, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
#             allure.dynamic.label("error", str(e))
#             raise