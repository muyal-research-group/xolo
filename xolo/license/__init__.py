import time
import hmac
import hashlib
import base64
from option import Result,Err,Ok

class LicenceManager:
    def __init__(self,secret_key:bytes):
        self.secret_key = secret_key
    @staticmethod
    def base32_encode(data: bytes) -> str:
        """Encodes the data in Base32 and ensures it's uppercase."""
        return base64.b32encode(data).decode('utf-8').rstrip('=').upper()
    @staticmethod
    def base32_decode(data: str) -> bytes:
        """Decodes a Base32-encoded string."""
        # Add padding for Base32 (it needs to be multiple of 8 characters)
        padding_needed = 8 - (len(data) % 8)
        padded_data = data + "=" * padding_needed
        return base64.b32decode(padded_data)
    def generate(self,user_id: str, app_id: str, expires_in_days: int) -> Result[str,Exception]:
        """Generates a license key that expires after a certain number of days."""
        try:
            # Calculate expiration timestamp (in seconds)
            expiration_timestamp = int(time.time()) + expires_in_days * 86400
            
            # Create the message for HMAC (user_id, product_id, expiration)
            message = f"{user_id}:{app_id}:{expiration_timestamp}".encode()
            
            # Create an HMAC using the secret key and the message
            hmac_obj = hmac.new(self.secret_key, message, hashlib.sha256)
            
            # Encode the HMAC output in Base32 and ensure uppercase without padding
            license_key = LicenceManager.base32_encode(hmac_obj.digest())
            
            # Combine the license key and expiration timestamp (converted to Base32 as well)
            encoded_expiration = LicenceManager.base32_encode(expiration_timestamp.to_bytes(6, 'big'))  # 6 bytes can store expiration for long periods
            
            return Ok(f"{license_key}{encoded_expiration}")
        except Exception as e:
            return Err(e)
    
    def verify(self,user_id: str, app_id: str, license_key: str) -> Result[bool, Exception]:
        """Validates the license key and checks if it has expired."""
        try:
            # Extract the last part (expiration timestamp) from the license
            encoded_expiration = license_key[-10:]  # Last 10 characters are expiration
            actual_license_key = license_key[:-10]  # The rest is the HMAC

            # Decode the expiration timestamp from Base32
            expiration_timestamp = int.from_bytes(LicenceManager.base32_decode(encoded_expiration), 'big')
            # Check if the license has expired
            if int(time.time()) > expiration_timestamp:
                print("License has expired!")
                return Err(Exception("License has expired."))
            
            # Generate the expected license key using the user_id, product_id, and expiration
            expected_license = self.generate(user_id, app_id, (expiration_timestamp - int(time.time())) // 86400 )
            
            # Compare only the HMAC part of the license (ignoring expiration part in this comparison)
            return Ok(hmac.compare_digest(expected_license[:-10], actual_license_key))
        
        except Exception as e:
            return Err(e)

if __name__ =="__main__":
    lm = LicenceManager(secret_key=b"secret")
    lkey = lm.generate(user_id="user", app_id="oca", expires_in_days=1)
    print(lkey)
    result = lm.verify(user_id="user", app_id="oca",license_key=lkey)
    print(result)