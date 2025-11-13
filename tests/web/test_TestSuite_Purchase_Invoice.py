# """
# Test Suite for Automation Exercise Test Case 24
# Test Case 24: Download Invoice after purchase order
# """
# import pytest
# import allure
# import os
# from pathlib import Path
# from src.project.page_object.web.automation_exercise import AutomationExercise_HOME
# from src.project.page_object.web.Product_Page import ProductPage
# from src.project.page_object.web.CartPage import CartPage
# from src.project.page_object.web.checkout_page import CheckOutPage
# from src.project.page_object.web.payment_page import PaymentPage
# from src.project.page_object.web.PaymentDonePage import PaymentDonePage
# from src.project.page_object.web.SigninPage import LoginPage


# class TestPurchaseAndDownloadInvoice:
#     """Test class for purchase flow and invoice download"""

#     @allure.feature("E-commerce Flow")
#     @allure.story("Complete Purchase and Download Invoice")
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.automation_exercise
#     @allure.suite("Test Case 24: Download Invoice after purchase order")
#     def test_complete_purchase_and_download_invoice(self, browser, app_urls, purchase_test_data, data_test_signup, request):
#         """Test Case 24: Download Invoice after purchase order"""
#         purchase_data = purchase_test_data
#         signup_data = data_test_signup
#         allure.dynamic.title(purchase_data.get("test_name", "Complete purchase and download invoice"))
#         allure.dynamic.description(f"Test ID: {purchase_data.get('test_id')}<br>Products: {[p['name'] for p in purchase_data['products_to_purchase']]}")
#         allure.dynamic.label("test_id", purchase_data.get("test_id"))
        
#         home_page = AutomationExercise_HOME(browser)
#         product_page = ProductPage(browser, app_urls['automation_excercise'])
#         cart_page = CartPage(browser)
#         checkout_page = CheckOutPage(browser, app_urls['automation_excercise'])
#         payment_page = PaymentPage(browser, app_urls['automation_excercise'])
#         payment_done_page = PaymentDonePage(browser)
#         login_page = LoginPage(browser)
        
#         try:
#             with allure.step("Navigate to home page"):
#                 home_page.navigate()
#                 assert "AutomationExercise" in browser.title(), "Home page should be loaded"
            
#             with allure.step("Add products to cart"):
#                 for product in purchase_data['products_to_purchase']:
#                     product_page.add_product_to_cart(product['name'])
#                     # Wait for modal and click continue shopping
#                     browser.wait_for_selector('div.modal-content', timeout=5000)
#                     continue_shopping_btn = browser.locator('div.modal-content button:has-text("Continue Shopping")')
#                     continue_shopping_btn.click()
            
#             with allure.step("Navigate to cart"):
#                 home_page.navigate_to_cart()
#                 assert "Shopping Cart" in browser.title() or "Cart" in browser.title(), "Cart page should be loaded"
            
#             with allure.step("Proceed to checkout"):
#                 cart_page.proceed_to_checkout()
#                 assert "Checkout" in browser.title(), "Checkout page should be loaded"
            
#             with allure.step("Register/Login for checkout"):
#                 # Click register/login button on checkout page
#                 register_login_btn = browser.locator('a:has-text("Register / Login")')
#                 register_login_btn.click()
                
#                 # Fill signup form
#                 login_page.configure_signup_form(signup_data['signup_name'], signup_data['signup_email'])
#                 login_page.click_signup_button()
#                 login_page.fill_signup_form(signup_data['form_data'])
#                 login_page.click_continue_button()
                
#                 # Verify user is logged in
#                 assert home_page.isUserLoggedIn(signup_data['signup_name']), f"User {signup_data['signup_name']} should be logged in"
            
#             with allure.step("Navigate back to cart and proceed to checkout"):
#                 home_page.navigate_to_cart()
#                 cart_page.proceed_to_checkout()
                
#                 # Verify address details
#                 address_section = browser.locator('div#address_delivery')
#                 assert address_section.is_visible(), "Delivery address should be visible"
                
#                 billing_section = browser.locator('div#address_invoice')
#                 assert billing_section.is_visible(), "Billing address should be visible"
            
#             with allure.step("Add comment and place order"):
#                 checkout_page.leave_comment(purchase_data['comment'])
#                 checkout_page.place_order()
#                 assert "Payment" in browser.title(), "Payment page should be loaded"
            
#             with allure.step("Fill payment details"):
#                 payment_data = purchase_data['payment_data']
#                 payment_page.fill_payment_details(
#                     payment_data['name_on_card'],
#                     payment_data['card_number'],
#                     payment_data['cvc'],
#                     payment_data['expiry_month'],
#                     payment_data['expiry_year']
#                 )
#                 payment_page.confirm_payment()
            
#             with allure.step("Verify order success"):
#                 # Wait for payment success page
#                 browser.wait_for_timeout(3000)
                
#                 success_message = payment_done_page.get_order_success_message()
#                 assert success_message and "successfully" in success_message.lower(), f"Expected success message, got: {success_message}"
                
#                 order_number = payment_done_page.get_order_number()
#                 assert order_number, "Order number should be generated"
                
#                 allure.attach(order_number, name="Order Number", attachment_type=allure.attachment_type.TEXT)
            
#             with allure.step("Download invoice"):
#                 # Set up download path
#                 download_path = Path("reports/downloads")
#                 download_path.mkdir(parents=True, exist_ok=True)
                
#                 # Start download
#                 with browser.expect_download() as download_info:
#                     payment_done_page.download_invoice()
                
#                 download = download_info.value
                
#                 # Save download
#                 invoice_path = download_path / f"invoice_{purchase_data['test_id']}.pdf"
#                 download.save_as(invoice_path)
                
#                 # Verify file was downloaded
#                 assert invoice_path.exists(), f"Invoice file should be downloaded at {invoice_path}"
#                 assert invoice_path.stat().st_size > 0, "Downloaded invoice file should not be empty"
                
#                 allure.attach.file(str(invoice_path), name="Downloaded Invoice", attachment_type=allure.attachment_type.PDF)
            
#             with allure.step("Continue and delete account"):
#                 payment_done_page.continue_shopping()
                
#                 # Delete account for cleanup
#                 home_page.navigate_to_delete_account()
#                 assert payment_done_page.accountDeletedMessage.is_visible(), "Account deleted message should be visible"
#                 payment_done_page.continue_button.click()
            
#             with allure.step("Take success screenshot"):
#                 screenshot_path = f"reports/screenshots/{purchase_data['test_id']}_success.png"
#                 browser.screenshot(path=screenshot_path, full_page=True)
#                 allure.attach.file(screenshot_path, name="Purchase Success Screenshot", attachment_type=allure.attachment_type.PNG)
                
#         except Exception as e:
#             screenshot_path = f"reports/screenshots/error_{purchase_data['test_id']}_purchase.png"
#             browser.screenshot(path=screenshot_path)
#             allure.attach.file(screenshot_path, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
#             allure.dynamic.label("error", str(e))
#             raise

#     @allure.feature("E-commerce Flow")
#     @allure.story("Purchase Flow Validation")
#     @allure.severity(allure.severity_level.NORMAL)
#     @pytest.mark.automation_exercise
#     @allure.suite("Test Case 24: Purchase flow validation")
#     def test_purchase_flow_validation(self, browser, app_urls, request):
#         """Test purchase flow validation"""
#         allure.dynamic.title("Test purchase flow validation")
#         allure.dynamic.description("Test purchase flow with invalid payment details")
        
#         home_page = AutomationExercise_HOME(browser)
#         product_page = ProductPage(browser, app_urls['automation_excercise'])
#         cart_page = CartPage(browser)
#         checkout_page = CheckOutPage(browser, app_urls['automation_excercise'])
#         payment_page = PaymentPage(browser, app_urls['automation_excercise'])
        
#         try:
#             with allure.step("Navigate to home page"):
#                 home_page.navigate()
#                 assert "AutomationExercise" in browser.title(), "Home page should be loaded"
            
#             with allure.step("Add product to cart"):
#                 product_page.add_product_to_cart("Blue Top")
#                 browser.wait_for_selector('div.modal-content', timeout=5000)
#                 continue_shopping_btn = browser.locator('div.modal-content button:has-text("Continue Shopping")')
#                 continue_shopping_btn.click()
            
#             with allure.step("Navigate to cart and proceed to checkout"):
#                 home_page.navigate_to_cart()
#                 cart_page.proceed_to_checkout()
            
#             with allure.step("Register/Login for checkout"):
#                 register_login_btn = browser.locator('a:has-text("Register / Login")')
#                 register_login_btn.click()
                
#                 # Use existing test data for quick signup
#                 login_page.configure_signup_form("Test User", "testuser@example.com")
#                 login_page.click_signup_button()
                
#                 # Fill minimal signup form
#                 signup_data = {
#                     "Title": "Mr.",
#                     "Name": "Test User",
#                     "Password": "Test@123456",
#                     "DOB": ["15", "5", "1990"],
#                     "FirstName": "Test",
#                     "LastName": "User",
#                     "Company": "Test Company",
#                     "Address": {
#                         "Add1": "123 Test Street",
#                         "Add2": "",
#                         "Country": "United States",
#                         "State": "California",
#                         "City": "Los Angeles",
#                         "Code": "90001"
#                     },
#                     "Phone": "+1234567890"
#                 }
                
#                 login_page.fill_signup_form(signup_data)
#                 login_page.click_continue_button()
            
#             with allure.step("Navigate back to cart and proceed to checkout"):
#                 home_page.navigate_to_cart()
#                 cart_page.proceed_to_checkout()
#                 checkout_page.leave_comment("Test order")
#                 checkout_page.place_order()
            
#             with allure.step("Test invalid payment details"):
#                 # Fill invalid payment details
#                 payment_page.fill_payment_details(
#                     "Invalid Name",
#                     "0000000000000000",  # Invalid card number
#                     "000",  # Invalid CVC
#                     "13",  # Invalid month
#                     "2020"  # Past year
#                 )
                
#                 # Try to submit payment
#                 payment_page.confirm_payment()
#                 browser.wait_for_timeout(2000)
                
#                 # Check if error message appears or payment fails
#                 error_elements = browser.locator('div.alert-danger, div.error, .error-message')
#                 if error_elements.count() > 0:
#                     error_message = error_elements.first.text_content()
#                     allure.attach(error_message, name="Payment Error Message", attachment_type=allure.attachment_type.TEXT)
#                 else:
#                     allure.attach("No error message detected", name="Payment Validation", attachment_type=allure.attachment_type.TEXT)
            
#             with allure.step("Take validation screenshot"):
#                 screenshot_path = f"reports/screenshots/purchase_validation_test.png"
#                 browser.screenshot(path=screenshot_path, full_page=True)
#                 allure.attach.file(screenshot_path, name="Purchase Validation Screenshot", attachment_type=allure.attachment_type.PNG)
                
#         except Exception as e:
#             screenshot_path = f"reports/screenshots/error_purchase_validation.png"
#             browser.screenshot(path=screenshot_path)
#             allure.attach.file(screenshot_path, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
#             allure.dynamic.label("error", str(e))
#             raise
