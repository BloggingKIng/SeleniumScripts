from functions import functions

if __name__ == "__main__":
    driver = functions.login_facebook("email", "password")
    functions.send_reminders(driver, "https://www.facebook.com/groups/1001741534131544/members/invited", 11*60*60, 15, 2*7*24*60*60)