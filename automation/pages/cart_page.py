from __future__ import annotations
from typing import Tuple, List
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from .base_page import BasePage

class CartPage(BasePage):
    CART_ITEM: Tuple[str, str] = (By.CLASS_NAME, "cart_item")
    INVENTORY_ITEM_NAME: Tuple[str, str] = (By.CLASS_NAME, "inventory_item_name")
    CONTINUE_SHOPPING_BTN: Tuple[str, str] = (By.ID, "continue-shopping")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def get_cart_items_count(self) -> int:
        if self.is_visible(self.CART_ITEM):
            return len(self.find_elements(self.CART_ITEM))
        return 0

    def get_cart_item_names(self) -> List[str]:
        if not self.is_visible(self.CART_ITEM):
            return []
        elements = self.find_elements(self.INVENTORY_ITEM_NAME)
        return [elem.text for elem in elements]

    def wait_for_cart_items_count(self, expected_count: int) -> None:
        if expected_count == 0:
            self.wait_for_invisibility(self.CART_ITEM)
        else:
            self.wait.until(lambda driver: len(driver.find_elements(*self.CART_ITEM)) == expected_count)

    def remove_product(self, product_id: str) -> None:
        remove_btn: Tuple[str, str] = (By.ID, f"remove-{product_id}")
        element = self.find_element(remove_btn)
        self.js_click(remove_btn)
        self.wait_for_staleness(element)

    def continue_shopping(self) -> None:
        self.click_until_url(self.CONTINUE_SHOPPING_BTN, "inventory.html", use_js=True)
