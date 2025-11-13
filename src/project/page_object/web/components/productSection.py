from src.project.page_object.web.BasePage import BasePage
from src.core.utils.web_action import WebActions 

class ProductSection(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.brandSection = self.get_element('.brands_products')
        self.categorySection = self.get_element('.panel-group.category-products')
    def verifyCategoryVisible(self):
        return self.categorySection.is_visible()
    def countItemProduct(self):
        listProduct = self.get_element('div.features_items')
        return listProduct.count()
    def verifyBrandSectionVisible(self):
        return self.brandSection.is_visible()
    def verifyBrandVisible(self, name):
        brand = self.brandSection.get_element(f'a[href*="{name}"]')
        return brand.is_visible()
    def clickBrand(self, name):
        brand = self.brandSection.get_element(f'a[href*="{name}"]')
        brand.click()
    def clickCategory(self, namecate):
        category = self.categorySection.get_element(f'a[href*="{namecate}"]')
        category.click()
    def scrollUp(self):
        scroll = self.get_element('a#scrollUp')
        scroll.click()
    def scrollDown(self):
        scroll = self.get_element('a#scrollDown')
        scroll.click()