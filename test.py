from bs4 import BeautifulSoup
from selenium import webdriver
import os
import platform

driver_file = "drivers/geckodriver" if platform.system() == "Linux" else "drivers/geckodriver.exe"
firefox_options = webdriver.FirefoxOptions()

firefox_options.add_argument("--headless")
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument("--disable-dev-shm-usage")
firefox_options.add_argument("--disable-javascript")

driver = webdriver.Firefox(
    executable_path=os.path.join(os.getcwd(), driver_file), firefox_options=firefox_options)

driver.get("http://results.jntuh.ac.in/")

print("DOING...")
print(driver.execute_script("return document.documentElement.outerHTML"))
