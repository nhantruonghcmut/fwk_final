# """
# Test Suite for Automation Exercise Test Case 21
# Test Case 21: Add review on product
# """
# import pytest
# import allure
# from src.project.page_object.web.automation_exercise import AutomationExercise_HOME
# from src.project.page_object.web.Product_Page import ProductPage
# from src.project.page_object.web.ProductDetailPage import ProductDetailPage


# class TestProductReview:
#     """Test class for product review functionality"""

#     @allure.feature("Product Reviews")
#     @allure.story("Add Product Review")
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.automation_exercise
#     @allure.suite("Test Case 21: Add review on product")
#     def test_add_review_on_product(self, browser, app_urls, review_test_data, request):
#         """Test Case 21: Add review on product"""
#         data = review_test_data
#         allure.dynamic.title(data.get("test_name", "Add review on product"))
#         allure.dynamic.description(f"Test ID: {data.get('test_id')}<br>Product: {data.get('product_name')}<br>Reviewer: {data['review_data']['name']}")
#         allure.dynamic.label("test_id", data.get("test_id"))
        
#         home_page = AutomationExercise_HOME(browser)
#         product_page = ProductPage(browser, app_urls['automation_excercise'])
#         product_detail_page = ProductDetailPage(browser)
        
#         try:
#             with allure.step("Navigate to home page"):
#                 home_page.navigate()
#                 assert "AutomationExercise" in browser.title(), "Home page should be loaded"
            
#             with allure.step("Navigate to Products page"):
#                 home_page.navigate_to_products()
#                 assert "All Products" in browser.title() or "Products" in browser.title(), "Products page should be loaded"
            
#             with allure.step("Navigate to product detail page"):
#                 product_page.view_product(data['product_name'])
                
#                 # Verify we're on product detail page
#                 product_name = product_detail_page.get_product_name()
#                 assert data['product_name'] in product_name, f"Expected product '{data['product_name']}', got '{product_name}'"
            
#             with allure.step("Scroll to review section"):
#                 # Scroll to review section
#                 review_section = browser.locator('div#reviews')
#                 review_section.scroll_into_view_if_needed()
#                 browser.wait_for_timeout(1000)
            
#             with allure.step("Fill review form"):
#                 review_data = data['review_data']
#                 product_detail_page.submit_review(
#                     review_data['name'],
#                     review_data['email'],
#                     review_data['review_text']
#                 )
            
#             with allure.step("Verify review submission success"):
#                 # Wait for success message
#                 browser.wait_for_timeout(2000)
                
#                 success_message = product_detail_page.get_review_success_message()
#                 if success_message:
#                     assert "Thank you for your review" in success_message or "success" in success_message.lower(), f"Expected success message, got: {success_message}"
#                 else:
#                     # Check if review appears in the reviews section
#                     reviews_section = browser.locator('div#reviews')
#                     review_text = reviews_section.text_content()
#                     assert data['review_data']['review_text'] in review_text, "Review text should appear in reviews section"
            
#             with allure.step("Take success screenshot"):
#                 screenshot_path = f"reports/screenshots/{data['test_id']}_success.png"
#                 browser.screenshot(path=screenshot_path, full_page=True)
#                 allure.attach.file(screenshot_path, name="Review Success Screenshot", attachment_type=allure.attachment_type.PNG)
                
#         except Exception as e:
#             screenshot_path = f"reports/screenshots/error_{data['test_id']}_review.png"
#             browser.screenshot(path=screenshot_path)
#             allure.attach.file(screenshot_path, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
#             allure.dynamic.label("error", str(e))
#             raise

#     @allure.feature("Product Reviews")
#     @allure.story("Add Review Without Required Fields")
#     @allure.severity(allure.severity_level.NORMAL)
#     @pytest.mark.automation_exercise
#     @allure.suite("Test Case 21: Add review validation")
#     def test_add_review_validation(self, browser, app_urls, request):
#         """Test review form validation"""
#         allure.dynamic.title("Test review form validation")
#         allure.dynamic.description("Test review form with missing required fields")
        
#         home_page = AutomationExercise_HOME(browser)
#         product_page = ProductPage(browser, app_urls['automation_excercise'])
#         product_detail_page = ProductDetailPage(browser)
        
#         try:
#             with allure.step("Navigate to home page"):
#                 home_page.navigate()
#                 assert "AutomationExercise" in browser.title(), "Home page should be loaded"
            
#             with allure.step("Navigate to Products page"):
#                 home_page.navigate_to_products()
#                 assert "All Products" in browser.title() or "Products" in browser.title(), "Products page should be loaded"
            
#             with allure.step("Navigate to product detail page"):
#                 product_page.view_product("Blue Top")
                
#                 # Verify we're on product detail page
#                 product_name = product_detail_page.get_product_name()
#                 assert "Blue Top" in product_name, f"Expected product 'Blue Top', got '{product_name}'"
            
#             with allure.step("Scroll to review section"):
#                 review_section = browser.locator('div#reviews')
#                 review_section.scroll_into_view_if_needed()
#                 browser.wait_for_timeout(1000)
            
#             with allure.step("Submit empty review form"):
#                 # Try to submit without filling any fields
#                 product_detail_page.review_submit_button.click()
#                 browser.wait_for_timeout(1000)
            
#             with allure.step("Verify validation behavior"):
#                 # Check if form shows validation errors or prevents submission
#                 # This test verifies the form behavior with empty fields
#                 success_message = product_detail_page.get_review_success_message()
                
#                 # If no success message, validation is working
#                 if not success_message:
#                     allure.attach("No success message - validation working", name="Validation Result", attachment_type=allure.attachment_type.TEXT)
#                 else:
#                     allure.attach(f"Unexpected success message: {success_message}", name="Validation Result", attachment_type=allure.attachment_type.TEXT)
            
#             with allure.step("Take validation screenshot"):
#                 screenshot_path = f"reports/screenshots/review_validation_test.png"
#                 browser.screenshot(path=screenshot_path, full_page=True)
#                 allure.attach.file(screenshot_path, name="Review Validation Screenshot", attachment_type=allure.attachment_type.PNG)
                
#         except Exception as e:
#             screenshot_path = f"reports/screenshots/error_review_validation.png"
#             browser.screenshot(path=screenshot_path)
#             allure.attach.file(screenshot_path, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
#             allure.dynamic.label("error", str(e))
#             raise
