import requests
import re
import os
from datetime import datetime

# --- आपकी फाइल डिटेल्स ---
THIRD_PARTY_URL = "https://github.com/ProTube/IPTV/raw/refs/heads/main/64bit"
MASTER_M3U_FILENAME = "hstr.m3u"
# PlaceHolder: आपको अपनी hstr.m3u में इस PlaceHolder का उपयोग करना होगा
COOKIE_PLACEHOLDER = "__HDNEA_COOKIE_PLACEHOLDER__"

def get_new_cookie(url):
    """3rd पार्टी M3U से नई __hdnea__ कुकी वैल्यू निकालता है।"""
    print(f"Fetching 3rd party M3U from: {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        m3u_content = response.text
        
        # Regex: हमें वह पूरा string चाहिए जो "__hdnea__=" से शुरू होता है और 
        # अगली '}' या किसी whitespace/नई लाइन से पहले समाप्त होता है।
        # हम इसे #EXTHTTP लाइन से निकालने की कोशिश करेंगे क्योंकि यह अधिक साफ है।
        
        # Regex Pattern: __hdnea__= के बाद से लेकर अगली '}' तक की हर चीज़ को कैप्चर करें
        match = re.search(r'__hdnea__=([^}]+)', m3u_content)
        
        if match:
            # कुकी का पूरा मान (जैसे: st=1762130788~exp=... )
            new_cookie_value = match.group(0) 
            print(f"Successfully extracted new cookie value: {new_cookie_value[:20]}... (showing first 20 chars)")
            return new_cookie_value
        else:
            print("ERROR: '__hdnea__=' cookie value not found in 3rd party M3U.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching 3rd party M3U: {e}")
        return None

def update_master_m3u(new_cookie_value):
    """मास्टर M3U फ़ाइल में कुकी को अपडेट करता है।"""
    # ... (बाकी का कोड वही रहेगा)
    try:
        if not os.path.exists(MASTER_M3U_FILENAME):
            print(f"ERROR: Master M3U file not found: {MASTER_M3U_FILENAME}")
            return False

        with open(MASTER_M3U_FILENAME, 'r') as f:
            master_content = f.read()
            
        # PlaceHolder को नई कुकी वैल्यू से बदलें
        updated_content = master_content.replace(COOKIE_PLACEHOLDER, new_cookie_value)
        
        # चेक करें कि बदलाव हुआ या नहीं
        if updated_content == master_content:
            print("Master M3U content is unchanged (Placeholder not found or cookie is same). Skipping commit.")
            return False

        with open(MASTER_M3U_FILENAME, 'w') as f:
            f.write(updated_content)
            
        print(f"SUCCESS: Master M3U updated and saved to {MASTER_M3U_FILENAME}")
        return True
        
    except Exception as e:
        print(f"Error updating master M3U: {e}")
        return False

if __name__ == "__main__":
    new_cookie = get_new_cookie(THIRD_PARTY_URL)
    
    if new_cookie:
        changes_made = update_master_m3u(new_cookie)
        # GitHub Actions को यह बताने के लिए कि बदलाव हुए हैं, एक आउटपुट सेट करें
        if changes_made:
            print(f"::set-output name=commit_needed::true") 
        else:
             print(f"::set-output name=commit_needed::false") 
    else:
        print("Could not get new cookie. Script terminated.")
        print(f"::set-output name=commit_needed::false")
