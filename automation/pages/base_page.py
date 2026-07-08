from __future__ import annotations
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

class BasePage:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def find_element(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, locator: tuple[str, str]) -> list[WebElement]:
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator: tuple[str, str]) -> None:
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def js_click(self, locator: tuple[str, str]) -> None:
        element = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].click();", element)

    def type_text(self, locator: tuple[str, str], text: str) -> None:
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple[str, str]) -> str:
        element = self.wait.until(EC.visibility_of_element_located(locator))
        return element.text

    def is_visible(self, locator: tuple[str, str]) -> bool:
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def wait_for_url(self, url_part: str) -> None:
        self.wait.until(EC.url_contains(url_part))

    def click_until_present(self, click_locator: tuple[str, str], target_locator: tuple[str, str], max_retries: int = 3, use_js: bool = False) -> None:
        for i in range(max_retries):
            try:
                if use_js:
                    self.js_click(click_locator)
                else:
                    self.click(click_locator)
                WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(target_locator))
                return
            except Exception:
                if i == max_retries - 1:
                    if use_js:
                        self.js_click(click_locator)
                    else:
                        self.click(click_locator)
                    self.wait.until(EC.presence_of_element_located(target_locator))

    def click_until_visible(self, click_locator: tuple[str, str], target_locator: tuple[str, str], max_retries: int = 3, use_js: bool = False) -> None:
        for i in range(max_retries):
            try:
                if use_js:
                    self.js_click(click_locator)
                else:
                    self.click(click_locator)
                WebDriverWait(self.driver, 2).until(EC.visibility_of_element_located(target_locator))
                return
            except Exception:
                if i == max_retries - 1:
                    if use_js:
                        self.js_click(click_locator)
                    else:
                        self.click(click_locator)
                    self.wait.until(EC.visibility_of_element_located(target_locator))

    def wait_for_staleness(self, element: WebElement) -> None:
        self.wait.until(EC.staleness_of(element))

    def wait_for_text_in_element(self, locator: tuple[str, str], text: str) -> None:
        self.wait.until(EC.text_to_be_present_in_element(locator, text))

    def wait_for_invisibility(self, locator: tuple[str, str]) -> None:
        self.wait.until(EC.invisibility_of_element_located(locator))

    def click_until_url(self, click_locator: tuple[str, str], url_part: str, max_retries: int = 3, use_js: bool = False) -> None:
        for i in range(max_retries):
            try:
                if use_js:
                    self.js_click(click_locator)
                else:
                    self.click(click_locator)
                WebDriverWait(self.driver, 2).until(EC.url_contains(url_part))
                return
            except Exception:
                if i == max_retries - 1:
                    if use_js:
                        self.js_click(click_locator)
                    else:
                        self.click(click_locator)
                    self.wait_for_url(url_part)
