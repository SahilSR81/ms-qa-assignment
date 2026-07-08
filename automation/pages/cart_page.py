from selenium.webdriver.common.by import By
from .base_page import BasePage

class CartPage(BasePage):
    # Locators
    CART_ITEM = (By.CLASS_NAME, "cart_item")
    CONTINUE_SHOPPING_BTN = (By.ID, "continue-shopping")

    def __init__(self, driver):
        super().__init__(driver)

    def get_cart_items_count(self):
        if self.is_visible(self.CART_ITEM):
            return len(self.find_elements(self.CART_ITEM))
        return 0

    def wait_for_cart_items_count(self, expected_count):
        if expected_count == 0:
            self.wait_for_invisibility(self.CART_ITEM)
        else:
            self.wait.until(lambda driver: len(driver.find_elements(*self.CART_ITEM)) == expected_count)

    def remove_product(self, product_id):
        # e.g., remove-sauce-labs-backpack
        remove_btn = (By.ID, f"remove-{product_id}")
        element = self.find_element(remove_btn)
        self.js_click(remove_btn)
        self.wait_for_staleness(element)

    def continue_shopping(self):
        self.click(self.CONTINUE_SHOPPING_BTN)
        self.wait_for_url("inventory.html")
