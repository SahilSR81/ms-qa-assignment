from __future__ import annotations
from typing import Self
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from .base_page import BasePage

class LoginPage(BasePage):
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)
        self.url = "https://www.saucedemo.com/"

    def open(self) -> Self:
        self.driver.get(self.url)
        return self

    def login(self, username: str, password: str, expect_success: bool = True) -> None:
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        if expect_success:
            self.click_until_url(self.LOGIN_BUTTON, "inventory.html")
        else:
            self.click_until_visible(self.LOGIN_BUTTON, self.ERROR_MESSAGE)

    def get_error_message(self) -> str:
        if self.is_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""
