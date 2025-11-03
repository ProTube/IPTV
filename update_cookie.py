import requests
import re
import os
from datetime import datetime

# --- आपकी फाइल डिटेल्स ---
# 3rd पार्टी M3U का URL जहाँ से कुकी मिलेगी
THIRD_PARTY_URL = "https://raw.githubusercontent.com/alex8875/m3u/refs/heads/main/jstar.m3u"
# आपकी मास्टर M3U फ़ाइल का नाम (जो GitHub पर है)
MASTER_M3U_FILENAME = "hstr.m3u"
# PlaceHolder जिसे स्क्रिप्ट आपकी मास्टर फ़ाइल में ढूंढेगी और बदलेगी
COOKIE_PLACEHOLDER = "__COOKIE_PLACEHOLDER__"

def get_new_cookie(url):
    """3rd पार्टी M3U से नई कुकी निकालता है।"""
    print(f"Fetching 3rd party M3U from: {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        m3u_content = response.text
        
        # 'cookie=' के बाद की कुकी वैल्यू को Regex से ढूंढें 
        # (यह मानकर कि कुकी '&' से पहले समाप्त होती है)
        match = re.search(r'cookie=([^&\s\)]+)', m3u_content)
        
        if match:
            new_cookie = match.group(1) 
            print(f"Successfully extracted new cookie: {new_cookie[:5]}... (showing first 5 chars)")
            return new_cookie
        else:
            print("ERROR: Cookie parameter not found in 3rd party M3U stream URLs.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching 3rd party M3U: {e}")
        return None

def update_master_m3u(new_cookie):
    """मास्टर M3U फ़ाइल में कुकी को अपडेट करता है और बदलावों को चेक करता है।"""
    try:
        # 1. मास्टर फ़ाइल को पढ़ें
        if not os.path.exists(MASTER_M3U_FILENAME):
            print(f"ERROR: Master M3U file not found: {MASTER_M3U_FILENAME}")
            return False

        with open(MASTER_M3U_FILENAME, 'r') as f:
            master_content = f.read()
            
        # 2. PlaceHolder को नई कुकी से बदलें
        updated_content = master_content.replace(COOKIE_PLACEHOLDER, new_cookie)
        
        # 3. चेक करें कि कोई बदलाव हुआ है या नहीं
        if updated_content == master_content:
            print("Master M3U content is unchanged (Placeholder not found or cookie is same). Skipping commit.")
            return False

        # 4. अपडेटेड कंटेंट को वापस फ़ाइल में लिखें
        with open(MASTER_M3U_FILENAME, 'w') as f:
            f.write(updated_content)
            
        print(f"SUCCESS: Master M3U updated and saved to {MASTER_M3U_FILENAME}")
        return True
        
    except Exception as e:
        print(f"Error updating master M3U: {e}")
        return False

if __name__ == "__main__":
    new_cookie_value = get_new_cookie(THIRD_PARTY_URL)
    
    if new_cookie_value:
        # GitHub Actions को यह बताने के लिए कि बदलाव हुए हैं, एक आउटपुट सेट करें
        changes_made = update_master_m3u(new_cookie_value)
        if changes_made:
            # Action को पता चलता है कि कमिट करना है
            print(f"::set-output name=commit_needed::true") 
        else:
             print(f"::set-output name=commit_needed::false") 
    else:
        print("Could not get new cookie. Script terminated.")
        print(f"::set-output name=commit_needed::false")
