# """
# Test Suite for Automation Exercise Test Cases 19 & 20
# Test Case 19: View & Search Products
# Test Case 20: Search Products and verify cart after login
# """
# import pytest
# import allure
# from src.project.page_object.web.automation_exercise import AutomationExercise_HOME
# from src.project.page_object.web.Product_Page import ProductPage
# from src.project.page_object.web.SigninPage import LoginPage


# class TestViewSearchProducts:
#     """Test class for viewing and searching products"""

#     @allure.feature("Product Management")
#     @allure.story("View All Products")
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.automation_exercise
#     @allure.suite("Test Case 19: View & Search Products")
#     def test_view_all_products(self, browser, app_urls, view_search_test_data, request):
#         """Test Case 19: View & Search Products"""
#         data = view_search_test_data
#         allure.dynamic.title(data.get("test_name", "View all products"))
#         allure.dynamic.description(f"Test ID: {data.get('test_id')}<br>Search term: {data.get('search_term')}")
#         allure.dynamic.label("test_id", data.get("test_id"))
        
#         home_page = AutomationExercise_HOME(browser)
#         product_page = ProductPage(browser, app_urls['automation_excercise'])
        
#         try:
#             with allure.step("Navigate to home page"):
#                 home_page.navigate()
#                 assert "AutomationExercise" in browser.title(), "Home page should be loaded"
            
#             with allure.step("Navigate to Products page"):
#                 home_page.navigate_to_products()
#                 assert "All Products" in browser.title() or "Products" in browser.title(), "Products page should be loaded"
            
#             with allure.step("Verify all products are visible"):
#                 # Check if product section is visible
#                 assert product_page.product_section.is_visible(), "Product section should be visible"
                
#                 # Get number of products displayed
#                 products = browser.locator('div.product-image-wrapper').count()
#                 assert products > 0, "At least one product should be visible"
                
#                 allure.attach(str(products), name="Number of Products", attachment_type=allure.attachment_type.TEXT)
            
#             with allure.step("Search for specific product"):
#                 product_page.search_product(data['search_term'])
                
#                 # Wait for search results
#                 browser.wait_for_timeout(2000)
                
#                 # Verify search results
#                 if data['expected_search_results'] > 0:
#                     search_results = browser.locator('div.product-image-wrapper').count()
#                     assert search_results > 0, f"Expected search results for '{data['search_term']}', but found none"
                    
#                     # Verify search term appears in product names
#                     product_names = browser.locator('div.product-image-wrapper p').all_text_contents()
#                     matching_products = [name for name in product_names if data['search_term'].lower() in name.lower()]
#                     assert len(matching_products) > 0, f"No products found matching '{data['search_term']}'"
#                 else:
#                     # Verify no results message or empty results
#                     no_results_message = browser.locator('div:has-text("No results found")')
#                     if no_results_message.count() == 0:
#                         # Check if no products are displayed
#                         search_results = browser.locator('div.product-image-wrapper').count()
#                         assert search_results == 0, f"Expected no results for '{data['search_term']}', but found {search_results}"
            
#             with allure.step("Take success screenshot"):
#                 screenshot_path = f"reports/screenshots/{data['test_id']}_success.png"
#                 browser.screenshot(path=screenshot_path, full_page=True)
#                 allure.attach.file(screenshot_path, name="Search Results Screenshot", attachment_type=allure.attachment_type.PNG)
                
#         except Exception as e:
#             screenshot_path = f"reports/screenshots/error_{data['test_id']}_search.png"
#             browser.screenshot(path=screenshot_path)
#             allure.attach.file(screenshot_path, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
#             allure.dynamic.label("error", str(e))
#             raise

#     @allure.feature("Product Management")
#     @allure.story("Search Products and Verify Cart After Login")
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.automation_exercise
#     @allure.suite("Test Case 20: Search Products and verify cart after login")
#     def test_search_products_and_verify_cart_after_login(self, browser, app_urls, view_search_test_data, data_test_login, request):
#         """Test Case 20: Search Products and verify cart after login"""
#         search_data = view_search_test_data
#         login_data = data_test_login
#         allure.dynamic.title("Search products and verify cart after login")
#         allure.dynamic.description(f"Search term: {search_data.get('search_term')}<br>Login email: {login_data.get('email')}")
#         allure.dynamic.label("test_id", f"search_login_{search_data.get('test_id')}")
        
#         home_page = AutomationExercise_HOME(browser)
#         product_page = ProductPage(browser, app_urls['automation_excercise'])
#         login_page = LoginPage(browser)
        
#         try:
#             with allure.step("Navigate to home page"):
#                 home_page.navigate()
#                 assert "AutomationExercise" in browser.title(), "Home page should be loaded"
            
#             with allure.step("Navigate to Products page"):
#                 home_page.navigate_to_products()
#                 assert "All Products" in browser.title() or "Products" in browser.title(), "Products page should be loaded"
            
#             with allure.step("Search for products"):
#                 product_page.search_product(search_data['search_term'])
#                 browser.wait_for_timeout(2000)
            
#             with allure.step("Add products to cart"):
#                 if search_data['expected_search_results'] > 0:
#                     # Add first available product to cart
#                     products = browser.locator('div.product-image-wrapper')
#                     if products.count() > 0:
#                         # Hover over first product and add to cart
#                         first_product = products.first
#                         first_product.hover()
#                         add_to_cart_btn = first_product.locator('div.product-overlay a')
#                         add_to_cart_btn.click()
                        
#                         # Click continue shopping from modal
#                         browser.wait_for_selector('div.modal-content', timeout=5000)
#                         continue_shopping_btn = browser.locator('div.modal-content button:has-text("Continue Shopping")')
#                         continue_shopping_btn.click()
            
#             with allure.step("Navigate to login page"):
#                 home_page.navigate_to_login()
#                 assert "Login" in browser.title(), "Login page should be loaded"
            
#             with allure.step("Perform login"):
#                 login_page.perform_login(login_data['email'], login_data['password'])
                
#                 # Verify login success
#                 assert home_page.isUserLoggedIn(login_data['username']), f"User {login_data['username']} should be logged in"
            
#             with allure.step("Navigate to cart and verify products"):
#                 home_page.navigate_to_cart()
#                 assert "Shopping Cart" in browser.title() or "Cart" in browser.title(), "Cart page should be loaded"
                
#                 # Verify cart is not empty (if products were added)
#                 cart_items = browser.locator('tbody tr').count()
#                 if search_data['expected_search_results'] > 0:
#                     assert cart_items > 0, "Cart should contain products after login"
#                 else:
#                     # If no products were found, cart might be empty
#                     allure.attach(str(cart_items), name="Cart Items Count", attachment_type=allure.attachment_type.TEXT)
            
#             with allure.step("Take success screenshot"):
#                 screenshot_path = f"reports/screenshots/search_login_{search_data['test_id']}_success.png"
#                 browser.screenshot(path=screenshot_path, full_page=True)
#                 allure.attach.file(screenshot_path, name="Search and Login Success Screenshot", attachment_type=allure.attachment_type.PNG)
                
#         except Exception as e:
#             screenshot_path = f"reports/screenshots/error_search_login_{search_data['test_id']}.png"
#             browser.screenshot(path=screenshot_path)
#             allure.attach.file(screenshot_path, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
#             allure.dynamic.label("error", str(e))
#             raise
