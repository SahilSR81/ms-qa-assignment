from __future__ import annotations
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from typing import Generator, Any

from _pytest.config.argparsing import Parser
from _pytest.fixtures import SubRequest

def pytest_addoption(parser: Parser) -> None:
    parser.addoption("--browser_name", action="store", default="chrome")
    parser.addoption(
        "--headless",
        action="store",
        default="true",
        help="Run browser in headless mode (true/false)",
    )

@pytest.fixture(scope="function")
def setup(request: SubRequest) -> Generator[None, None, None]:
    browser_name: str = request.config.getoption("browser_name")
    headless: bool = request.config.getoption("headless").lower() == "true"

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

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Any, call: Any) -> Generator[None, Any, None]:
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        try:
            if hasattr(item.cls, "driver"):
                driver = item.cls.driver
                os.makedirs("screenshots", exist_ok=True)
                screenshot_path: str = os.path.join("screenshots", f"{item.name}.png")
                driver.save_screenshot(screenshot_path)
                print(f"\nSaved failure screenshot to: {screenshot_path}")
                print(f"[DEBUG FAILURE] Current URL: {driver.current_url}")
                print(f"[DEBUG FAILURE] Page source snippet:\n{driver.page_source[:1500]}")
        except Exception as e:
            print(f"\nFailed to capture screenshot/details: {e}")
