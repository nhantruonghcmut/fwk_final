# """
# Test Suite for Automation Exercise Test Cases 12 & 13
# Test Case 12: Add products in Cart
# Test Case 13: Verify Product quantity in Cart
# """
# import pytest
# import allure
# from src.project.page_object.web.automation_exercise import AutomationExercise_HOME
# from src.project.page_object.web.Product_Page import ProductPage
# from src.project.page_object.web.ProductDetailPage import ProductDetailPage
# from src.project.page_object.web.CartPage import CartPage
# from src.project.page_object.web.SigninPage import LoginPage


# class TestCartFeatures:
#     """Test class for cart functionality"""

#     @allure.feature("Checkout")
#     @allure.story("Add Products to Cart")
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.automation_exercise
#     @allure.suite("Test Case 12: Add products in Cart")
#     def test_add_products_to_cart(self, browser, app_urls, cart_test_data, request):
#         """Test Case 12: Add products in Cart"""
#         data = cart_test_data
#         allure.dynamic.title(data.get("test_name", "Add products to cart"))
#         allure.dynamic.description(f"Test ID: {data.get('test_id')}<br>Products: {[p['name'] for p in data['products_to_add']]}")
#         allure.dynamic.label("test_id", data.get("test_id"))
        
#         home_page = AutomationExercise_HOME(browser)
#         product_page = ProductPage(browser, app_urls['automation_excercise'])
#         cart_page = CartPage(browser)
        
#         try:
#             with allure.step("Navigate to home page"):
#                 home_page.navigate()
#                 assert "Automation Exercise" in home_page.get_title(), "Home page should be loaded"
            
#             with allure.step("Add products to cart from home page"):
#                 for product in data['products_to_add']:
#                     product_page.add_product_to_cart(product['name'])
#                     # Wait for modal to appear and click continue shopping
#                     product_page.wait_for_element('div.modal-content', timeout=5000)
#                     continue_shopping_btn = product_page.get_element('div.modal-content button:has-text("Continue Shopping")')
#                     continue_shopping_btn.click()
            
#             with allure.step("Navigate to cart page"):
#                 home_page.navigate_to_cart()
#                 assert "Checkout" in cart_page.get_title(), "Cart page should be loaded"
            
#             with allure.step("Verify products are added to cart"):
#                 cart_count = cart_page.get_cart_item_count()
#                 assert cart_count == data['expected_cart_count'], f"Expected {data['expected_cart_count']} items, got {cart_count}"
                
#                 # Verify each product is in cart
#                 for product in data['products_to_add']:
#                     assert cart_page.check_item_visibility(product['name']), f"Product {product['name']} should be visible in cart"
            
#             with allure.step("Take success screenshot"):
#                 screenshot_path = f"reports/screenshots/{data['test_id']}_success.png"
#                 cart_page.take_screenshot(screenshot_path)
#                 allure.attach.file(screenshot_path, name="Cart Success Screenshot", attachment_type=allure.attachment_type.PNG)
                
#         except Exception as e:
#             screenshot_path = f"reports/screenshots/error_{data['test_id']}_cart.png"
#             cart_page.take_screenshot(screenshot_path)
#             allure.attach.file(screenshot_path, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
#             allure.dynamic.label("error", str(e))
#             raise

#     @allure.feature("Checkout")
#     @allure.story("Verify Product Quantity in Cart")
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.automation_exercise
#     @allure.suite("Test Case 13: Verify Product quantity in Cart")
#     def test_verify_product_quantity_in_cart(self, browser, app_urls, cart_test_data, request):
#         """Test Case 13: Verify Product quantity in Cart"""
#         data = cart_test_data
#         allure.dynamic.title(data.get("test_name", "Verify product quantity in cart"))
#         allure.dynamic.description(f"Test ID: {data.get('test_id')}<br>Products: {[p['name'] for p in data['products_to_add']]}")
#         allure.dynamic.label("test_id", data.get("test_id"))
        
#         home_page = AutomationExercise_HOME(browser)
#         product_page = ProductPage(browser, app_urls['automation_excercise'])
#         cart_page = CartPage(browser)
        
#         try:
#             with allure.step("Navigate to home page"):
#                 home_page.navigate()
#                 assert "Automation Exercise" in home_page.get_title(), "Home page should be loaded"
            
#             with allure.step("Add products to cart"):
#                 for product in data['products_to_add']:
#                     # Navigate to product detail page to set quantity
#                     product_page.view_product(product['name'])
#                     product_detail_page = ProductDetailPage(browser)
                    
#                     # Set quantity if more than 1
#                     if product['quantity'] > 1:
#                         product_detail_page.set_quantity(product['quantity'])
                    
#                     # Add to cart
#                     product_detail_page.add_to_cart()
                    
#                     # Click continue shopping from modal
#                     product_detail_page.wait_for_element('div.modal-content', timeout=5000)
#                     continue_shopping_btn = product_detail_page.get_element('div.modal-content button:has-text("Continue Shopping")')
#                     continue_shopping_btn.click()
                    
#                     # Navigate back to home page for next product
#                     home_page.navigate()
            
#             with allure.step("Navigate to cart page"):
#                 home_page.navigate_to_cart()
#                 assert "Checkout" in cart_page.get_title(), "Cart page should be loaded"
            
#             with allure.step("Verify product quantities in cart"):
#                 for product in data['products_to_add']:
#                     quantity = cart_page.get_quantity_of_item(product['name'])
#                     assert quantity == product['quantity'], f"Expected quantity {product['quantity']} for {product['name']}, got {quantity}"
                
#                 # Verify total cart count
#                 cart_count = cart_page.get_cart_item_count()
#                 assert cart_count == data['expected_cart_count'], f"Expected {data['expected_cart_count']} items, got {cart_count}"
            
#             with allure.step("Take success screenshot"):
#                 screenshot_path = f"reports/screenshots/{data['test_id']}_success.png"
#                 cart_page.take_screenshot(screenshot_path)
#                 allure.attach.file(screenshot_path, name="Quantity Verification Screenshot", attachment_type=allure.attachment_type.PNG)
                
#         except Exception as e:
#             screenshot_path = f"reports/screenshots/error_{data['test_id']}_quantity.png"
#             cart_page.take_screenshot(screenshot_path)
#             allure.attach.file(screenshot_path, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
#             allure.dynamic.label("error", str(e))
#             raise
