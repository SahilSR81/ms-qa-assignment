
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def find_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, locator):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def js_click(self, locator):
        element = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].click();", element)

    def type_text(self, locator, text):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        return element.text

    def is_visible(self, locator):
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def wait_for_url(self, url_part):
        self.wait.until(EC.url_contains(url_part))

    def click_until_present(self, click_locator, target_locator, max_retries=3, use_js=False):
        for i in range(max_retries):
            try:
                if use_js:
                    self.js_click(click_locator)
                else:
                    self.click(click_locator)
                # Wait a short duration for the target element to appear
                WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(target_locator))
                return
            except Exception:
                if i == max_retries - 1:
                    # Final attempt will raise the actual timeout exception if it fails
                    if use_js:
                        self.js_click(click_locator)
                    else:
                        self.click(click_locator)
                    self.wait.until(EC.presence_of_element_located(target_locator))

    def click_until_visible(self, click_locator, target_locator, max_retries=3, use_js=False):
        for i in range(max_retries):
            try:
                if use_js:
                    self.js_click(click_locator)
                else:
                    self.click(click_locator)
                # Wait a short duration for the target element to become visible
                WebDriverWait(self.driver, 2).until(EC.visibility_of_element_located(target_locator))
                return
            except Exception:
                if i == max_retries - 1:
                    if use_js:
                        self.js_click(click_locator)
                    else:
                        self.click(click_locator)
                    self.wait.until(EC.visibility_of_element_located(target_locator))

    def wait_for_staleness(self, element):
        self.wait.until(EC.staleness_of(element))

    def wait_for_text_in_element(self, locator, text):
        self.wait.until(EC.text_to_be_present_in_element(locator, text))

    def wait_for_invisibility(self, locator):
        self.wait.until(EC.invisibility_of_element_located(locator))

    def click_until_url(self, click_locator, url_part, max_retries=3, use_js=False):
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
