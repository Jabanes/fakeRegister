import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Import our modular functions
from email_handler import create_mailtm_account, wait_for_verification_email
from form_filler import fill_out_and_submit_form

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
    form_submitted = fill_out_and_submit_form(driver, email, password)
    
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