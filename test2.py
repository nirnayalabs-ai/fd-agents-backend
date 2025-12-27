import jwt
from datetime import datetime, timedelta
import time

# ---------------------------------------------------------
# 1. MOCK SETTINGS (To run without Django)
# ---------------------------------------------------------
class MockSettings:
    SECRET_KEY = "my_super_secret_testing_key_12345"
    CUSTOM_JWT = {
        "ACCESS_TOKEN_LIFETIME_MINUTES": 15,
        "REFRESH_TOKEN_LIFETIME_DAYS": 7
    }

# Assign mock to a variable named 'settings' so the class works as is
settings = MockSettings()

# ---------------------------------------------------------
# 2. YOUR JWT CLASS
# ---------------------------------------------------------
class JWTManager:
    SECRET = settings.SECRET_KEY
    ALGORITHM = "HS256"

    # Load custom JWT settings
    ACCESS_LIFETIME = settings.CUSTOM_JWT.get("ACCESS_TOKEN_LIFETIME_MINUTES", 15)
    REFRESH_LIFETIME = settings.CUSTOM_JWT.get("REFRESH_TOKEN_LIFETIME_DAYS", 10)

    # Internal decode
    @staticmethod
    def _decode(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                JWTManager.SECRET,
                algorithms=[JWTManager.ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    # Create Access Token
    @staticmethod
    def create_access_token(payload: dict) -> str:
        data = payload.copy()
        data["type"] = "access"
        data["exp"] = datetime.utcnow() + timedelta(
            minutes=JWTManager.ACCESS_LIFETIME
        )
        return jwt.encode(data, JWTManager.SECRET, algorithm=JWTManager.ALGORITHM)

    # Create Refresh Token
    @staticmethod
    def create_refresh_token(payload: dict) -> str:
        data = payload.copy()
        data["type"] = "refresh"
        data["exp"] = datetime.utcnow() + timedelta(
            days=JWTManager.REFRESH_LIFETIME
        )
        return jwt.encode(data, JWTManager.SECRET, algorithm=JWTManager.ALGORITHM)

    # Verify Access Token
    @staticmethod
    def verify_access_token(token: str) -> dict:
        payload = JWTManager._decode(token)
        if payload.get("type") != "access":
            raise ValueError("Provided token is not an access token")
        return payload

    # Verify Refresh Token
    @staticmethod
    def verify_refresh_token(token: str) -> dict:
        payload = JWTManager._decode(token)
        if payload.get("type") != "refresh":
            raise ValueError("Provided token is not a refresh token")
        return payload

    # Refresh Access Token from Refresh Token
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        payload = JWTManager.verify_refresh_token(refresh_token)

        # Remove internal fields (exp, type)
        new_payload = {
            key: value for key, value in payload.items()
            if key not in ["exp", "type"]
        }

        return JWTManager.create_access_token(new_payload)

# ---------------------------------------------------------
# 3. TEST EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    print("--- STARTING JWT TESTS ---\n")

    # Test Data
    user_data = {"user_id": 1, "email": "test@example.com", "role": "admin"}
    print(f"Original Data: {user_data}")

    # TEST A: Create and Verify Access Token
    print("\n[TEST A] Access Token Cycle")
    access_token = JWTManager.create_access_token(user_data)
    print(f"Generated Access Token: {access_token}")
    
    try:
        decoded_access = JWTManager.verify_access_token(access_token)
        print(f"Decoded Successfully: {decoded_access}")
    except ValueError as e:
        print(f"FAILED: {e}")

    # TEST B: Create and Verify Refresh Token
    print("\n[TEST B] Refresh Token Cycle")
    refresh_token = JWTManager.create_refresh_token(user_data)
    print(f"Generated Refresh Token: {refresh_token}")

    try:
        decoded_refresh = JWTManager.verify_refresh_token(refresh_token)
        print(f"Decoded Successfully: {decoded_refresh}")
    except ValueError as e:
        print(f"FAILED: {e}")

    # TEST C: Rotation (Get new Access Token using Refresh Token)
    print("\n[TEST C] Refreshing Access Token")
    try:
        new_access_token = JWTManager.refresh_access_token(refresh_token)
        print(f"New Access Token: {new_access_token}")
        # Verify the new one works
        verify_new = JWTManager.verify_access_token(new_access_token)
        print("New token verified successfully.")
    except ValueError as e:
        print(f"FAILED: {e}")

    # TEST D: Negative Test (Wrong Type)
    print("\n[TEST D] Negative Test: Sending Access Token to Refresh Verifier")
    try:
        JWTManager.verify_refresh_token(access_token)
        print("FAILED: Should have raised an error but didn't.")
    except ValueError as e:
        print(f"SUCCESS: Caught expected error: '{e}'")

    # TEST E: Tampered Token
    print("\n[TEST E] Negative Test: Tampered Token")
    tampered_token = access_token[:-1] + "a" # Change last char
    try:
        JWTManager.verify_access_token(tampered_token)
        print("FAILED: Should have raised an error.")
    except ValueError as e:
         print(f"SUCCESS: Caught expected error: '{e}'")

    print("\n--- TESTS FINISHED ---")











number = int(input("Enter a number: "))

if number % 5 == 0:
    print("The number is divisible by 5.")
else:
    print("The number is not divisible by 5.")