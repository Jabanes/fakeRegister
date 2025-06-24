import requests
import random
import string
import time
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup

def save_verified_email(email, password, url):
    data = []
    try:
        # Try to read existing data
        with open("verifiedEmails.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is invalid, start a new list
        pass

    # Append the new verified email with a timestamp
    data.append({
        "email": email,
        "password": password,
        "website_url": url,
        "timestamp": datetime.now().isoformat()
    })

    # Write the updated list back to the file
    with open("verifiedEmails.json", "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"💾 Saved verified email to verifiedEmails.json")

def get_mailtm_domains():
    try:
        response = requests.get("https://api.mail.tm/domains?page=1")
        response.raise_for_status()
        return [domain["domain"] for domain in response.json()["hydra:member"]]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching domains: {e}")
        return None

def generate_random_email(domain):
    # Generate random username (e.g., "abc123")
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{username}@{domain}"

def create_mailtm_account():
    # Step 1: Get an available domain
    domains = get_mailtm_domains()
    if not domains:
        print("❌ Could not get any domains from mail.tm.")
        return None, None

    domain = random.choice(domains)
    print(f"ℹ️ Using domain: {domain}")

    # Step 2: Generate a random email
    email = generate_random_email(domain)
    password = "yy123456"  # Can be anything
    
    # Step 3: Create the account
    response = requests.post(
        "https://api.mail.tm/accounts",
        json={"address": email, "password": password}
    )
    
    if response.status_code == 201:
        print(f"✅ Success! Email: {email}")
        return email, password
    else:
        print(f"❌ Error creating account: {response.text}")
        return None, None

def get_auth_token(email, password):
    try:
        response = requests.post(
            "https://api.mail.tm/token",
            json={"address": email, "password": password}
        )
        response.raise_for_status()
        return response.json()["token"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting auth token: {e}")
        return None

def get_messages(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://api.mail.tm/messages", headers=headers)
        response.raise_for_status()
        return response.json()["hydra:member"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting messages: {e}")
        return []

def find_verification_link(html_content):
    """Parses HTML content to find the specific verification link."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Find the 'a' tag with the specific Hebrew text
        link_tag = soup.find('a', string='לחצו כאן לאמת')
        if link_tag and link_tag.has_attr('href'):
            return link_tag['href']
    except Exception as e:
        print(f"Error parsing email HTML: {e}")
    
    # Fallback if the specific text is not found
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', html_content)
    for url in urls:
        if "אימות-משתמש" in url: # "user-verification" in Hebrew
            return url

    return None

def wait_for_verification_email(email, password):
    print("\n⏳ Waiting for a verification email...")
    token = get_auth_token(email, password)
    if not token:
        return

    start_time = time.time()
    while time.time() - start_time < 300:  # Wait for 5 minutes
        messages = get_messages(token)
        if messages:
            latest_message = messages[0]
            print(f"✅ New message received: '{latest_message['subject']}' from '{latest_message['from']['address']}'")

            headers = {"Authorization": f"Bearer {token}"}
            msg_id = latest_message['id']
            
            try:
                msg_response = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers)
                msg_response.raise_for_status()
                msg_data = msg_response.json()
                
                print("\n--- Full Email Content ---")
                if msg_data.get('text'):
                    print("--- Plain Text Version ---")
                    print(msg_data['text'])
                if msg_data.get('html'):
                    print("\n--- HTML Version ---")
                    print("".join(msg_data['html']))
                print("--- End of Email Content ---\n")

                html_content = "".join(msg_data.get('html', []))
                verification_link = find_verification_link(html_content)

                if verification_link:
                    print(f"🔗 Found verification link: {verification_link}")
                    print("🚀 Attempting to verify...")
                    try:
                        verify_response = requests.get(verification_link, allow_redirects=True, timeout=15)
                        verify_response.raise_for_status()
                        print("✅ Verification successful!")
                        print(f"    Final URL: {verify_response.url}")
                        print(f"    Status code: {verify_response.status_code}")
                        save_verified_email(email, password, "https://www.shippuden.store/")
                    except requests.exceptions.RequestException as e:
                        print(f"❌ Verification failed: {e}")
                    return # Exit after processing the first email
                else:
                    print("❌ No verification link found in the email.")
                    return
            except requests.exceptions.RequestException as e:
                print(f"❌ Error getting message content: {e}")

        time.sleep(10)

    print("🤷 No email received within 5 minutes.")


# Run it
if __name__ == "__main__":
    new_email, password = create_mailtm_account()
    if new_email:
        print(f"📧 Use this email: {new_email}")
        wait_for_verification_email(new_email, password)