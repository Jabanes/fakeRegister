import os
import sys
import time
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Import our modular functions
from email_handler import create_mailtm_account, wait_for_verification_email
from form_filler import fill_out_and_submit_form
from login_filler import login_user

# Load environment variables from .env file
load_dotenv()

def run_registration_flow(register_url, login_url):
    """Handles the full user registration and verification process."""
    # 1. Create a new email account
    print("--- Step 1: Creating new email account ---")
    email, password = create_mailtm_account()
    if not email:
        print("Could not create email. Exiting.")
        return
    
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    
    # 2. Set up Selenium, fill form, and keep browser open
    print("\n--- Step 2: Filling out registration form ---")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    form_submitted, name = fill_out_and_submit_form(driver, register_url, email, password)
    
    if not form_submitted:
        print("Could not submit the form. Exiting.")
        driver.quit()
        return
        
    # 3. Wait for and handle the verification email using the same browser session
    print("\n--- Step 3: Waiting for verification email ---")
    verified = wait_for_verification_email(driver, email, password, name)

    # 4. Clean up
    print("\n--- Step 4: Closing browser ---")
    time.sleep(5)
    driver.quit()

    if verified:
        print("✅ Registration and verification complete!")
    else:
        print("❌ Verification failed.")

def run_login_flow(login_url):
    """Handles logging in with the most recent user."""
    print("--- Starting Login Flow ---")
    try:
        with open("verifiedEmails.json", "r") as f:
            all_users = json.load(f)
            if not all_users:
                raise FileNotFoundError
            
            latest_user = all_users[-1]
            email = latest_user["email"]
            password = latest_user["password"]
            
            print(f"Attempting to log in with user: {email}")
            
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            login_user(driver, login_url, email, password)
            time.sleep(10)
            driver.quit()

    except (FileNotFoundError, json.JSONDecodeError, IndexError):
        print("\n❌ Could not read user data from 'verifiedEmails.json'.")
        print("Please run the registration flow first to create a user.")

def main():
    """Main function to orchestrate the bot."""
    register_url = os.getenv("REGISTER_URL")
    login_url = os.getenv("LOGIN_URL")

    if not register_url or not login_url:
        print("❌ Error: REGISTER_URL and LOGIN_URL must be set in the .env file.")
        return

    if len(sys.argv) < 2 or sys.argv[1] not in ['register', 'login']:
        print("Usage: py main.py [register|login]")
        return

    action = sys.argv[1]

    if action == 'register':
        run_registration_flow(register_url, login_url)
    elif action == 'login':
        run_login_flow(login_url)

if __name__ == "__main__":
    main() 