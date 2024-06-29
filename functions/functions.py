from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import os
import json 
def login_facebook(email, password):
    cookies_exist = os.path.exists(f"cookies\\{email}.json")
    service = Service(executable_path="chromedriver.exe")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized") 
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    chrome_options.add_experimental_option("useAutomationExtension", False) 
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.facebook.com/")
    time.sleep(3)
    if cookies_exist:
        with open(f"cookies\\{email}.json") as f:
            cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.get("https://www.facebook.com/")
    else:
        email_input = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.ID, "email")))
        email_input.send_keys(email)
        password_input = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.ID, "pass")))
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(30) # for approving 2 factor auth :)
        with open(f"cookies\\{email}.json", "w") as f:
            json.dump(driver.get_cookies(), f)
    return driver 

def string_to_time(time_string):
    time_units = {
        'second': 1,
        'minute': 60,
        'hour': 60*60,
        'day': 24*60*60,
        'week': 7*24*60*60,
        'month': 30*24*60*60,  
        'year': 365*24*60*60  
    }
    match = re.search(r'(\d+)\s+(\w+)\s+ago', time_string)
    if not match:
        print("Invalid time string")
        return
    value, unit = match.groups()
    value = int(value)
    unit = unit.rstrip('s')  
    if unit not in time_units:
        print("Invalid time unit")
        return
    
    return value * time_units[unit]

def send_reminders(driver,invites_page_url, remind_after_seconds,members_to_remind, remove_after_seconds):
    driver.get(invites_page_url)
    time.sleep(3)
    members_list = driver.find_element(By.XPATH, '//div[@role="list"]')
    members = members_list.find_elements(By.XPATH, "//div[@role='listitem']")
    reminded = 0
    already_checked_people = []
    prev_len = len(already_checked_people)
    tries = 0
    while reminded < members_to_remind and tries <= 2:
        for member in members:
            try:
                #Moving this to the top so it checks if a modal is blocking the screen beforing starting
                try:
                    close_btn = driver.find_element(By.XPATH, '//div[contains(translate(@aria-label,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"), "close")]')
                    close_btn.click()
                    time.sleep(1)
                except Exception as e:
                    pass
                if reminded >= members_to_remind:
                    break
                txt = member.text
                member_name = txt.split('\n')[0] if txt.split('\n')[0].lower().strip() != "active" else txt.split('\n')[1]
                if member_name not in already_checked_people:
                    member.location_once_scrolled_into_view
                    driver.execute_script("window.scrollBy(0, -300);")
                    time.sleep(1)
                    already_checked_people.append(member_name)
                    for line in txt.split('\n'):
                        if 'ago' in line:
                            st_time = string_to_time(line)
                            print(f"Member Name: {member_name} -> Line: {line} -> Time: {st_time}s")
                            if st_time > remind_after_seconds:
                                print(f"Sending reminder to {member_name}")
                                more_btn = driver.find_element(By.XPATH, f'//div[contains(@aria-label, "Actions for {member_name}")]')
                                more_btn.click()
                                try:
                                    time.sleep(2)
                                    reminder = driver.find_element(By.XPATH, '//span[contains(translate(text(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"), "reminder")]')
                                    ActionChains(driver).move_to_element(reminder).click().perform()
                                    time.sleep(1)
                                    confirm_btns = driver.find_elements(By.XPATH, '//span[contains(translate(text(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"), "confirm")]')
                                    for btn in confirm_btns:    
                                        try:
                                            btn.click()
                                            time.sleep(1)
                                            print("Successfully reminded the person!")
                                            print()
                                            reminded += 1
                                        except Exception as e:
                                            pass
                                except Exception as e:
                                    print("Seems like we have already reminded the person!")
                                    print("Let's see if its long enough we can remove this invite so we won't have to deal with it again")
                                    time.sleep(1)
                                    if st_time >= remove_after_seconds:
                                        remove_invitation = driver.find_elements(By.XPATH, f'//span[contains(translate(text(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"), "remove")]')
                                        for btn in remove_invitation:
                                            try:
                                                btn.click()
                                            except Exception as e:
                                                pass
                                    time.sleep(2)
                                    confirm_btns = driver.find_elements(By.XPATH, '//span[contains(translate(text(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"), "confirm")]')
                                    for btn in confirm_btns:    
                                        try:
                                            btn.click()
                                            time.sleep(1)
                                            print(f"Successfully removed invite to {member_name}")
                                            print()
                                            reminded += 1
                                        except Exception as e:
                                            pass
                                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            except:
                continue
        if len(already_checked_people) == prev_len:
            tries += 1
        prev_len = len(already_checked_people)
        members = members_list.find_elements(By.XPATH, "//div[@role='listitem']")

