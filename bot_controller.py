import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import the email-handling functions from our other script
from app import create_mailtm_account, wait_for_verification_email

def generate_random_string(length=8):
    """Generates a random string of letters for names."""
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def fill_out_and_submit_form(driver, email, password):
    """Navigates to the form, fills it out with random data, and submits it."""
    
    url = "https://www.shippuden.store/%D7%94%D7%A8%D7%A9%D7%9E%D7%94"
    print(f"Navigating to {url}")
    driver.get(url)

    try:
        # Wait for the form to be visible
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "registerForm")))
        print("Form is visible. Starting to fill out fields.")

        # Fill in the form fields using their IDs
        driver.find_element(By.ID, "regFName").send_keys(generate_random_string())
        driver.find_element(By.ID, "regLName").send_keys(generate_random_string())
        driver.find_element(By.ID, "regDisplay").send_keys(generate_random_string(10))
        driver.find_element(By.ID, "regEmail").send_keys(email)
        
        # Passwords
        driver.find_element(By.ID, "regPassword").send_keys(password)
        driver.find_element(By.ID, "regPasswordRe").send_keys(password)
        
        # Shipping info
        driver.find_element(By.ID, "regPhone").send_keys("0523021828")
        driver.find_element(By.ID, "regCity").send_keys("Givatayim") # Example city
        driver.find_element(By.ID, "regAddress").send_keys("Katsenelson St 74") # Example address

        # Agree to terms
        # Use JavaScript click to bypass potential interception
        terms_checkbox = driver.find_element(By.ID, "termsSwitch")
        driver.execute_script("arguments[0].scrollIntoView(true);", terms_checkbox)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", terms_checkbox)
        
        print("All fields filled. Submitting the form.")
        
        # Submit the form using a more robust method
        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginBtn")))
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5) # Wait for any overlays to disappear after scroll
        driver.execute_script("arguments[0].click();", submit_button)
        
        print("✅ Form submitted successfully.")
        return True

    except Exception as e:
        print(f"❌ An error occurred while filling the form: {e}")
        return False

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