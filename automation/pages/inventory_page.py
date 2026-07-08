from __future__ import annotations
from typing import Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from .base_page import BasePage

class InventoryPage(BasePage):
    CART_BADGE: Tuple[str, str] = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK: Tuple[str, str] = (By.CLASS_NAME, "shopping_cart_link")
    BURGER_MENU_BTN: Tuple[str, str] = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK: Tuple[str, str] = (By.ID, "logout_sidebar_link")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def add_product_to_cart(self, product_id: str) -> None:
        add_btn: Tuple[str, str] = (By.ID, f"add-to-cart-{product_id}")
        remove_btn: Tuple[str, str] = (By.ID, f"remove-{product_id}")
        self.click_until_present(add_btn, remove_btn, use_js=True)

    def get_cart_badge_count(self) -> int:
        if self.is_visible(self.CART_BADGE):
            return int(self.get_text(self.CART_BADGE))
        return 0

    def go_to_cart(self) -> None:
        self.click_until_url(self.CART_LINK, "cart.html", use_js=True)

    def wait_for_cart_badge_count(self, expected_count: int) -> None:
        if expected_count == 0:
            self.wait_for_invisibility(self.CART_BADGE)
        else:
            self.wait_for_text_in_element(self.CART_BADGE, str(expected_count))

    def logout(self) -> None:
        self.js_click(self.BURGER_MENU_BTN)
        self.js_click(self.LOGOUT_LINK)
        self.wait_for_url("saucedemo.com")
