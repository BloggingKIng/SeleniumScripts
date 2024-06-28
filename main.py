from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def login_facebook(email, password):
    service = Service(executable_path="chromedriver.exe")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized") 
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    chrome_options.add_experimental_option("useAutomationExtension", False) 
    driver = webdriver.Chrome(service=service, options=chrome_options)
    time.sleep(3)
    email_input = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.ID, "email")))
    email_input.send_keys(email)
    password_input = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.ID, "pass")))
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)