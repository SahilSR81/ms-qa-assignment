from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

driver.get("https://www.saucedemo.com/")
wait.until(EC.visibility_of_element_located((By.ID, "user-name"))).send_keys("standard_user")
wait.until(EC.visibility_of_element_located((By.ID, "password"))).send_keys("secret_sauce")
wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()

# Click backpack add button
add_btn = wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart-sauce-labs-backpack")))
print("Add button text:", add_btn.text)
add_btn.click()

# Wait and print page source around the button or find the button
try:
    remove_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'remove-')]")))
    print("Found button ID:", remove_btn.get_attribute("id"))
    print("Found button text:", remove_btn.text)
except Exception as e:
    print("Failed to find remove button:", e)

driver.quit()
