import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import our AI agent's analysis and correction functions
from agent import analyze_form_with_ai, get_corrected_selectors_from_ai

def login_user(driver, login_url, email, password):
    """
    Reads a local login.html, has an AI analyze it, then navigates to the
    live URL and dynamically fills the form. Retries on failure.
    """
    try:
        print("Reading local login.html for analysis...")
        with open('login.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("❌ Error: login.html not found. Please create it in the project root.")
        return False
        
    # Initial analysis
    selectors = analyze_form_with_ai(html_content)
    if not selectors:
        print("❌ Initial AI analysis for login failed. Cannot proceed.")
        return False

    max_retries = 3
    for attempt in range(max_retries):
        print(f"\n--- Logging In: Attempt {attempt + 1} of {max_retries} ---")
        if attempt > 0:
            print("🔍 Using Corrected Selectors:")
        else:
            print("🔍 Using Initial Selectors:")
        print(json.dumps(selectors, indent=2))
        
        print(f"\nNavigating to live login page: {login_url}")
        driver.get(login_url)
        time.sleep(2)

        try:
            driver.find_element(By.CSS_SELECTOR, selectors["email_selector"]).send_keys(email)
            driver.find_element(By.CSS_SELECTOR, selectors["password_selector"]).send_keys(password)
            
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors["submit_button_selector"]))
            )
            driver.execute_script("arguments[0].click();", submit_button)
            
            print(f"✅ Login submitted for user {email}.")
            return True

        except Exception as e:
            error_message = str(e)
            print(f"❌ An error occurred on login attempt {attempt + 1}:\n{error_message.splitlines()[0]}")
            
            if attempt < max_retries - 1:
                print("Asking AI for a correction...")
                corrected_selectors = get_corrected_selectors_from_ai(html_content, selectors, error_message)
                if corrected_selectors:
                    selectors = corrected_selectors
                else:
                    print("AI correction failed. Aborting login.")
                    break
            else:
                print("❌ Max retries reached. Could not log in.")
                
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
            login_user(driver, "https://www.shippuden.store/%D7%94%D7%AA%D7%97%D7%91%D7%A8%D7%95%D7%AA", email, password)
            time.sleep(10) # Keep browser open for 10 seconds to observe result
            driver.quit()

    except (FileNotFoundError, json.JSONDecodeError, IndexError):
        print("\n❌ Could not read user data from 'verifiedEmails.json'.")
        print("Please run main.py first to register and verify at least one user.")
    
    print("\n--- Login Script Finished ---") 