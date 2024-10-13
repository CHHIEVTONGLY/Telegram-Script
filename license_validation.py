import csv
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

LICENSE_FILE = "license.csv"

def load_public_key():
    with open('public_key.pem', 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key

def verify_license_data(license_key, expiration_date, signature, public_key):
    data_to_verify = f"{license_key}|{expiration_date}"
    try:
        public_key.verify(
            bytes.fromhex(signature),  # Convert hex signature back to bytes
            data_to_verify.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

def is_license_expired(expiration_date):
    current_date = datetime.now()
    exp_date = datetime.strptime(expiration_date, "%Y-%m-%d")
    return current_date > exp_date  # Returns True if expired

def store_license_key(license_key, expiration_date, signature):
    with open(LICENSE_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['license_key', 'expiration_date', 'signature'])
        writer.writerow([license_key, expiration_date, signature])

def load_license_from_file(file_path="license.csv"):
    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                return row['license_key'], row['expiration_date'], row['signature']
    except FileNotFoundError:
        print("License file not found!")
        return None, None, None
