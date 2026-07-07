from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

try:
    driver.get("https://www.saucedemo.com/")
    wait.until(EC.visibility_of_element_located((By.ID, "user-name"))).send_keys("standard_user")
    wait.until(EC.visibility_of_element_located((By.ID, "password"))).send_keys("secret_sauce")
    wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()

    # Add items
    wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart-sauce-labs-backpack"))).click()
    wait.until(EC.presence_of_element_located((By.ID, "remove-sauce-labs-backpack")))
    wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart-sauce-labs-bike-light"))).click()
    wait.until(EC.presence_of_element_located((By.ID, "remove-sauce-labs-bike-light")))

    print("Badge count:", wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "shopping_cart_badge"))).text)

    # Click cart link
    cart_link = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "shopping_cart_link")))
    cart_link.click()

    # Print current URL
    print("URL after click:", driver.current_url)

    # Verify if cart items exist
    items = driver.find_elements(By.CLASS_NAME, "cart_item")
    print("Number of cart items found:", len(items))

except Exception as e:
    print("Error:", e)
finally:
    driver.quit()
