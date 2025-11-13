from src.core.base.base_web import BaseWeb

class CartPage(BaseWeb):
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        
        # Thử các selector khác nhau cho cart table
        try:
            self.cart_table = self.get_element('div.table-responsive.cart_info')
            print(f"DEBUG: Cart table found with 'div.table-responsive.cart_info'")
        except:
            try:
                self.cart_table = self.get_element('div.cart_info')
                print(f"DEBUG: Cart table found with 'div.cart_info'")
            except:
                try:
                    self.cart_table = self.get_element('table.cart_info')
                    print(f"DEBUG: Cart table found with 'table.cart_info'")
                except:
                    try:
                        self.cart_table = self.get_element('div.table-responsive')
                        print(f"DEBUG: Cart table found with 'div.table-responsive'")
                    except:
                        print(f"DEBUG: No cart table found with any selector")
                        self.cart_table = None
        
        if self.cart_table:
            print(f"DEBUG: Cart table text: '{self.cart_table.get_text()[:200]}...'")
            
            # Thử các selector khác nhau cho cart rows
            try:
                self.cart_rows = self.cart_table.get_elements('tbody tr')
                print(f"DEBUG: Found {len(self.cart_rows)} rows with 'tbody tr'")
            except:
                try:
                    self.cart_rows = self.cart_table.get_elements('tr')
                    print(f"DEBUG: Found {len(self.cart_rows)} rows with 'tr'")
                except:
                    try:
                        self.cart_rows = self.cart_table.get_elements('div.cart_item')
                        print(f"DEBUG: Found {len(self.cart_rows)} rows with 'div.cart_item'")
                    except:
                        try:
                            self.cart_rows = self.page.get_elements('div.cart_item')
                            print(f"DEBUG: Found {len(self.cart_rows)} rows with page-level 'div.cart_item'")
                        except:
                            print(f"DEBUG: No cart rows found with any selector")
                            self.cart_rows = []
        else:
            self.cart_rows = []
        
        self.proceed_to_checkout_button = self.get_element('a:has-text("Proceed To Checkout")')

    def get_item_by_name(self, itemname):
        for item in self.cart_rows:
            # Tìm trong text của cart row, có thể là product name hoặc description
            item_text = item.get_text().lower()
            if itemname.lower() in item_text:
                return item
        # Debug: in ra tất cả text của cart rows để xem có gì
        print(f"DEBUG: Looking for '{itemname}', found {len(self.cart_rows)} cart rows:")
        for i, item in enumerate(self.cart_rows):
            print(f"  Row {i}: '{item.get_text()}'")
        return None

    def get_cart_item_count(self):
        return len(self.cart_rows)

    def get_quantity_of_item(self, itemname):
        item = self.get_item_by_name(itemname)
        if item is None:
            raise ValueError(f"Item '{itemname}' not found in cart")
        return int(item.get_element('td.cart_quantity').get_text())

    def check_item_visibility(self, itemname):
        item = self.get_item_by_name(itemname)
        if item is None:
            return False
        return item.is_visible()

    def get_price_of_item(self, itemname):
        item = self.get_item_by_name(itemname)
        if item is None:
            raise ValueError(f"Item '{itemname}' not found in cart")
        return int(item.get_element('td.cart_price').get_text().replace('Rs.', '').strip())

    def get_total_price_of_items(self, itemname):
        item = self.get_item_by_name(itemname)
        if item is None:
            raise ValueError(f"Item '{itemname}' not found in cart")
        return int(item.get_element('td.cart_total').get_element('p.cart_total_price').get_text().replace('Rs.', '').strip())

    def remove_item_from_cart(self, itemname):
        item = self.get_item_by_name(itemname)
        if item is None:
            raise ValueError(f"Item '{itemname}' not found in cart")
        item.get_element('td.cart_delete a.cart_quantity_delete').click()

    def navigate_to_item_detail(self, itemname):
        item = self.get_item_by_name(itemname)
        if item is None:
            raise ValueError(f"Item '{itemname}' not found in cart")
        item.get_element('td.cart_description a').click()

    def proceed_to_checkout(self):
        self.proceed_to_checkout_button.click()
    
    def get_title(self):
        """Get page title"""
        return self.page.title()