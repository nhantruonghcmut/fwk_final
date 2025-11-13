from src.core.utils.element_object import ElementObject
from src.core.base.base_web import BaseWeb

class ProductPage(BaseWeb):
    def __init__(self, page, base_url):
        super().__init__(page)
        self.page = page
        self.base_url = base_url
        self.search_input = self.get_element('input#search_product')
        self.brand_section = self.get_element('.brands_products')
        self.search_button = self.get_element('button#submit_search')
        self.category_section = self.get_element('.panel-group.category-products')
        self.product_section = self.get_element('.features_items')

    def get_category_item(self, itemname: str) -> ElementObject:
        id_ = itemname.capitalize()
        return self.category_section.get_element(f'#{id_}')

    def get_brand_item(self, brandname: str) -> ElementObject:
        # Tìm brand item bằng cách lọc các elements có chứa text
        brand_elements = self.brand_section.get_elements('a')
        for element in brand_elements:
            if brandname in element.get_text():
                return element
        raise ValueError(f"Brand '{brandname}' not found")

    def get_product_item(self, product_name: str) -> ElementObject:
        # Tìm product item bằng cách lọc các elements có chứa text
        product_elements = self.product_section.get_elements('div.product-image-wrapper')
        for element in product_elements:
            if product_name in element.get_text():
                return element
        raise ValueError(f"Product '{product_name}' not found")

    def number_item_of_brand(self, brandname: str) -> int:
        brand_item = self.get_brand_item(brandname)
        return int(brand_item.get_element('span').get_text())

    def number_item_of_category(self) -> int:
        return self.category_section.get_element('div.category-products a').count()

    def search_product(self, product_name: str):
        self.search_input.fill(product_name)
        # Sử dụng press để minh hoạ API mới và đảm bảo tương thích
        self.search_input.press("Enter")

    def add_product_to_cart(self, product_name: str):
        product_item = self.get_product_item(product_name)
        product_item.get_element('div.single-products').hover()
        add_to_cart_button = product_item.get_element('div.single-products').get_element('div.product-overlay a')
        add_to_cart_button.click()

    def hover_over_product(self, product_name: str):
        product_item = self.get_product_item(product_name)
        product_item.get_element('div.single-products').hover()

    def view_product(self, product_name: str):
        product_item = self.get_product_item(product_name)
        # Tìm link "View Product" trong product item
        view_links = product_item.get_elements('div.choose a')
        for link in view_links:
            if 'View Product' in link.get_text():
                link.click()
                return
        raise ValueError(f"View Product link not found for '{product_name}'")
