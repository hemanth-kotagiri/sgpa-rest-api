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


iframe_path = "/html/frameset/frameset/frame[1]"

driver.get("http://results.jntuh.ac.in/")
iframe = driver.find_element_by_xpath(iframe_path)
driver.switch_to.frame(iframe)

body_xpath = "/html/body"
body = driver.find_element_by_xpath(body_xpath)
body = body.get_attribute('innerHTML')
soup = BeautifulSoup(body, 'html.parser')
for each in soup.findAll("h3"):
    current = each.getText()
    date, description = current.split(" ", 1)
    date = date.lstrip("*(").rstrip(")")
    description = description.strip()
    print(date, description)
