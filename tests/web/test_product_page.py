# import pytest

# from src.project.page_object.web.Product_Page import ProductPage



# def test_search_product_press_and_timeout(browser):
#     base_url = "https://automationexercise.com"
#     browser.goto(f"{base_url}/products", wait_until="domcontentloaded", timeout=30000)

#     page = ProductPage(browser, base_url)

#     page.search_product("tshirt")
#     # Minh hoạ override timeout ở call-level
#     assert page.wait_for_element(page.product_section, timeout=15000, state="visible")