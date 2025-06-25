import ollama
import json

def analyze_form_with_ai(html_content):
    """Sends the HTML to Ollama to identify form fields and returns their selectors."""
    
    prompt = f"""
    You are an expert HTML parser. Your task is to find the CSS selectors for the **email**, **password**, and **submit button** in the HTML below.

    **Instructions:**
    1.  Focus on `<input>` tags for email and password.
    2.  Look for `id` or `name` attributes. For example: `id="jform_email1"` or `name="jform[password1]"`.
    3.  Find the submit `<button>` or `<input type="submit">`.
    4.  You MUST return a single JSON object with the keys: "email_selector", "password_selector", and "submit_button_selector".

    **HTML Content:**
    ```html
    {html_content}
    ```
    """
    
    print("🤖 Sending HTML to AI for analysis...")
    try:
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}],
            format='json'
        )
        
        print("✅ AI analysis complete.")
        return json.loads(response['message']['content'])
        
    except Exception as e:
        print(f"❌ Error communicating with Ollama: {e}")
        return None

def get_corrected_selectors_from_ai(html_content, failed_selectors, error_message):
    """Sends the HTML, the failed selectors, and the error back to Ollama for a correction."""
    
    prompt = f"""
    You are an expert HTML debugger. Your last attempt failed.

    **Error:** {error_message}
    **Your failed selectors:** {json.dumps(failed_selectors, indent=2)}

    **Instructions:**
    1.  Your previous selectors were WRONG.
    2.  Re-analyze the HTML and find the correct selectors for **name**, **email**, **password**, and the **submit button**.
    3.  Look for `<input>` tags with `id` or `name`.
    4.  You MUST provide a corrected JSON object with the keys "name_selector", "email_selector", "password_selector", and "submit_button_selector".

    **HTML Content:**
    ```html
    {html_content}
    ```
    """

    print("🤖 The previous attempt failed. Sending data back to AI for a more detailed correction...")
    try:
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}],
            format='json'
        )
        
        print("✅ AI has provided a new correction.")
        return json.loads(response['message']['content'])
        
    except Exception as e:
        print(f"❌ Error communicating with Ollama during correction: {e}")
        return None