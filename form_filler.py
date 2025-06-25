import time
import random
import string
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Import the email-handling functions from our other script
from email_handler import create_mailtm_account, wait_for_verification_email

# Import our AI agent's analysis and correction functions
from agent import analyze_form_with_ai, get_corrected_selectors_from_ai

def generate_random_string(length=8):
    """Generates a random string of letters for names."""
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def fill_out_and_submit_form(driver, register_url, email, password):
    """
    Tries to fill the form with known selectors and confirms submission by
    checking for a URL change. If it fails, it asks the AI for a correction.
    """
    selectors = {
        "name_selector": "#jform_name",
        "email_selector": "#jform_email1",
        "password_selector": "#jform_password1",
        "submit_button_selector": "button[type='submit']"
    }

    try:
        with open('register.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("⚠️ Warning: register.html not found. AI correction will not be possible.")
        html_content = ""

    max_retries = 3
    for attempt in range(max_retries):
        print(f"\n--- Filling Form: Attempt {attempt + 1} of {max_retries} ---")
        if attempt > 0:
            print("🔍 Using Corrected Selectors:")
        else:
            print("🔍 Using Initial Selectors:")
        print(json.dumps(selectors, indent=2))
        
        driver.get(register_url)
        time.sleep(3) 
        current_url = driver.current_url
        print(f"\nNavigating to live site: {current_url}")

        try:
            # Fill in all required fields, including the name
            name = generate_random_string()
            if selectors.get("name_selector"):
                driver.find_element(By.CSS_SELECTOR, selectors["name_selector"]).send_keys(name)
            if selectors.get("email_selector"):
                driver.find_element(By.CSS_SELECTOR, selectors["email_selector"]).send_keys(email)
            if selectors.get("password_selector"):
                driver.find_element(By.CSS_SELECTOR, selectors["password_selector"]).send_keys(password)
            
            # Click the submit button
            if selectors.get("submit_button_selector"):
                submit_button = driver.find_element(By.CSS_SELECTOR, selectors["submit_button_selector"])
                driver.execute_script("arguments[0].click();", submit_button)
            else:
                raise Exception("No submit button selector found.")
            
            # *** The new, more intelligent success check ***
            print("✅ Form submitted. Now waiting for URL to change...")
            WebDriverWait(driver, 10).until(lambda driver: driver.current_url != current_url)
            
            print("🎉 URL changed! Submission confirmed.")
            return True, name

        except Exception as e:
            error_message = str(e)
            print(f"❌ An error occurred on attempt {attempt + 1}:\n{error_message.splitlines()[0]}")
            
            if attempt < max_retries - 1:
                print("Asking AI for a correction...")
                corrected_selectors = get_corrected_selectors_from_ai(html_content, selectors, error_message)
                if corrected_selectors:
                    selectors = corrected_selectors
                else:
                    print("AI correction failed. Aborting.")
                    break
            else:
                print("❌ Max retries reached. Could not fill the form.")
    
    return False, None

def main():
    """Main function to orchestrate the bot."""
    
    # 1. Create a new email account
    print("--- Step 1: Creating new email account ---")
    email, password = create_mailtm_account()
    if not email:
        print("Could not create email. Exiting.")
        return
    
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    
    # 2. Set up Selenium and fill out the form
    print("\n--- Step 2: Filling out registration form ---")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    form_submitted, name = fill_out_and_submit_form(driver, "https://www.shippuden.store/%D7%94%D7%A8%D7%A9%D7%9E%D7%94", email, password)
    
    # Give a moment for the submission to process before closing browser
    time.sleep(5)
    driver.quit()
    
    if not form_submitted:
        print("Could not submit the form. Exiting.")
        return
        
    # 3. Wait for and handle the verification email
    print("\n--- Step 3: Waiting for verification email ---")
    wait_for_verification_email(email, password)

if __name__ == "__main__":
    main() 