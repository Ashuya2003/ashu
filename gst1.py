import requests
import json
import base64
import hashlib
import hmac
from Crypto.Cipher import AES




# Replace with actual values
client_id = "your_client_id"
client_secret = "your_client_secret"
username = "your_username"
auth_token = "your_auth_token"
ip_usr = "your_ip_address"
txn_id = "unique_txn_id"

# Encryption key (from authentication, replace with actual)
ek = b'your_shared_key'  # Example shared key from the API

# Function to encrypt data using AES 256
def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    padded_data = data + (16 - len(data) % 16) * chr(16 - len(data) % 16)
    encrypted_data = cipher.encrypt(padded_data.encode('utf-8'))
    return base64.b64encode(encrypted_data).decode('utf-8')

# Function to generate HMAC-SHA256
def generate_hmac(data, key):
    return base64.b64encode(hmac.new(key, data.encode('utf-8'), hashlib.sha256).digest()).decode('utf-8')

# GST API endpoint for taxpayer data
url = "https://domain-name/v0.1/taxpayerapi/returns"

# Define request headers
headers = {
    "clientid": client_id,
    "client-secret": client_secret,
    "username": username,
    "auth-token": auth_token,
    "state-cd": "99",  # Example state code, replace with actual
    "ip-usr": ip_usr,
    "txn": txn_id,
    "Content-Type": "application/json"
}

# Define the request payload (encrypt the payload)
request_payload = {
    "action": "getTaxpayerData",
    "data": encrypt_data(json.dumps({
        "gstin": "GSTIN_of_Taxpayer",  # Replace with the actual GSTIN
        "ret_period": "2023-09"  # Return period example
    }), ek),
    "hmac": generate_hmac("data_to_hmac", ek),
    "hdr": json.dumps({
        "clientid": client_id,
        "username": username,
        "state_cd": "99",
        "ip_usr": ip_usr,
        "txn": txn_id,
        "Api version": "v0.1",
        "User Role": "taxpayer"
    })
}

# Make the API request
response = requests.get(url, headers=headers, params=request_payload)

# Process the API response
if response.status_code == 200:
    # Decrypt the response (if required) and process the data
    response_data = response.json()
    print("Taxpayer Data:", json.dumps(response_data, indent=4))
else:
    print(f"Error: {response.status_code} - {response.text}")
