from functions import functions
import time
if __name__ == "__main__":
    driver = functions.login_facebook("email", "password")
    time.sleep(30)
    # The 30 second delay is for completing 2 factor authentication :)
    functions.invite_people(driver, "https://www.facebook.com/groups/1001741534131544/", 15)