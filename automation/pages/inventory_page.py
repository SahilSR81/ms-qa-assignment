from selenium.webdriver.common.by import By
from .base_page import BasePage

class InventoryPage(BasePage):
    # Locators
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    BURGER_MENU_BTN = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    def __init__(self, driver):
        super().__init__(driver)

    def add_product_to_cart(self, product_id):
        add_btn = (By.ID, f"add-to-cart-{product_id}")
        self.click(add_btn)
        # Wait for the button to change to "Remove", confirming cart state updated
        remove_btn = (By.ID, f"remove-{product_id}")
        self.find_element(remove_btn)

    def get_cart_badge_count(self):
        if self.is_visible(self.CART_BADGE):
            return int(self.get_text(self.CART_BADGE))
        return 0

    def go_to_cart(self):
        self.click(self.CART_LINK)

    def logout(self):
        self.click(self.BURGER_MENU_BTN)
        self.js_click(self.LOGOUT_LINK)
