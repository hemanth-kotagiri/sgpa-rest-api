import time
import os
import requests
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver
import platform

#TODO : Crawler class which consists of all the methods

class Crawler:
    def __init__(self):
        urls = {
            "1,1": "http://results.jntuh.ac.in/jsp/SearchResult.jsp?degree=btech&examCode=1323&etype=r16&type=grade16",
            "1,2": "http://results.jntuh.ac.in/jsp/SearchResult.jsp?degree=btech&examCode=1356&etype=r16&type=grade16",
            "2,1": "http://results.jntuh.ac.in/jsp/SearchResult.jsp?degree=btech&examCode=1391&etype=r17&type=grade17",
            "2,2": "http://results.jntuh.ac.in/jsp/SearchResult.jsp?degree=btech&examCode=1437&etype=r17&type=intgrade",
        }

        driver_file = "geckodriver" if platform.system() == "Linux" else "geckodriver.exe"
    # Starting the driver
    driver = webdriver.Firefox(
        executable_path=os.path.join(os.getcwd(), driver_file))



    def get_result(hallticket, dob, year):
        url = this.urls[year]
        # Returns the json object of results
        this.driver.get(url)

        # Getting the captcha value
        captcha_val = driver.execute_script("return document.getElementById('txtCaptcha').value")
        hall_pass = "document.getElementById('htno').value = '{}'".format(num)
        date_pass = "document.getElementById('datepicker').value = '{}'".format(bday)
        pass_str = "document.getElementById('txtInput').value = '{}'".format(captcha_val)
