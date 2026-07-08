import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)
driver.get("https://www.saucedemo.com/")
driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
driver.get("about:blank")
driver.get("https://www.saucedemo.com/")
print("Fields visible:", driver.execute_script("return document.getElementById('user-name') !== null"))
driver.find_element("id", "user-name").send_keys("standard_user")
driver.find_element("id", "password").send_keys("secret_sauce")
driver.find_element("id", "login-button").click()
import time
time.sleep(2)
print("URL:", driver.current_url)
print("Error:", driver.execute_script("return document.querySelector('[data-test=\"error\"]') ? document.querySelector('[data-test=\"error\"]').innerText : 'No error'"))
driver.quit()
