import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

def pytest_addoption(parser):
    parser.addoption("--browser_name", action="store", default="chrome")
    parser.addoption("--headless", action="store", default="true", help="Run browser in headless mode (true/false)")

@pytest.fixture(scope="class")
def setup(request):
    browser_name = request.config.getoption("browser_name")
    headless = request.config.getoption("headless").lower() == "true"
    
    if browser_name == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)
    elif browser_name == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Firefox(options=options)
    else:
        raise ValueError(f"Browser {browser_name} is not supported.")
        
    driver.maximize_window()
    request.cls.driver = driver
    yield
    driver.quit()
