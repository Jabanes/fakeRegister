import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login_user(driver, email, password):
    """Navigates to the login page and logs the user in."""
    
    url = "https://www.shippuden.store/%D7%94%D7%AA%D7%97%D7%91%D7%A8%D7%95%D7%AA"
    print(f"Navigating to login page: {url}")
    driver.get(url)

    try:
        # Wait for the login form to be visible
        login_form = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "loginForm"))
        )
        print("Login form is visible. Filling out credentials.")

        # Fill in email and password
        login_form.find_element(By.ID, "loginEmail").send_keys(email)
        login_form.find_element(By.ID, "loginPassword").send_keys(password)
        
        # Find the submit button within the form and click it
        submit_button = login_form.find_element(By.ID, "loginBtn")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_button)
        
        print(f"✅ Login submitted for user {email}.")
        return True

    except Exception as e:
        print(f"❌ An error occurred during login: {e}")
        return False

# Example of how to use this script
if __name__ == '__main__':
    print("--- Starting Login Script ---")
    
    try:
        with open("verifiedEmails.json", "r") as f:
            all_users = json.load(f)
            if not all_users:
                raise FileNotFoundError # Treat empty list as if file not found
            
            # Get the most recently created user
            latest_user = all_users[-1]
            email = latest_user["email"]
            password = latest_user["password"]
            
            print(f"Attempting to log in with the most recent user: {email}")
            
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            login_user(driver, email, password)
            time.sleep(10) # Keep browser open for 10 seconds to observe result
            driver.quit()

    except (FileNotFoundError, json.JSONDecodeError, IndexError):
        print("\n❌ Could not read user data from 'verifiedEmails.json'.")
        print("Please run main.py first to register and verify at least one user.")
    
    print("\n--- Login Script Finished ---") 