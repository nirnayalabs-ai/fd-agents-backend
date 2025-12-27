import jwt
from datetime import datetime, timedelta
from django.conf import settings


class JWTManager:
    SECRET = settings.SECRET_KEY
    ALGORITHM = "HS256"

    # Load custom JWT settings
    ACCESS_LIFETIME = settings.CUSTOM_JWT.get("ACCESS_TOKEN_LIFETIME_MINUTES", 15)
    REFRESH_LIFETIME = settings.CUSTOM_JWT.get("REFRESH_TOKEN_LIFETIME_DAYS", 10)

    # ---------------------------------------------------------
    # Internal decode
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Create Access Token
    # ---------------------------------------------------------
    @staticmethod
    def create_access_token(payload: dict) -> str:
        data = payload.copy()
        data["type"] = "access"
        data["exp"] = datetime.now() + timedelta(
            minutes=JWTManager.ACCESS_LIFETIME
        )
        return jwt.encode(data, JWTManager.SECRET, algorithm=JWTManager.ALGORITHM)

    # ---------------------------------------------------------
    # Create Refresh Token
    # ---------------------------------------------------------
    @staticmethod
    def create_refresh_token(payload: dict) -> str:
        data = payload.copy()
        data["type"] = "refresh"
        data["exp"] = datetime.utcnow() + timedelta(
            days=JWTManager.REFRESH_LIFETIME
        )
        return jwt.encode(data, JWTManager.SECRET, algorithm=JWTManager.ALGORITHM)

    # ---------------------------------------------------------
    # Verify Access Token
    # ---------------------------------------------------------
    @staticmethod
    def verify_access_token(token: str) -> dict:
        payload = JWTManager._decode(token)
        if payload.get("type") != "access":
            raise ValueError("Provided token is not an access token")
        return payload

    # ---------------------------------------------------------
    # Verify Refresh Token
    # ---------------------------------------------------------
    @staticmethod
    def verify_refresh_token(token: str) -> dict:
        payload = JWTManager._decode(token)
        if payload.get("type") != "refresh":
            raise ValueError("Provided token is not a refresh token")
        return payload

    # ---------------------------------------------------------
    # Refresh Access Token from Refresh Token
    # ---------------------------------------------------------
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        payload = JWTManager.verify_refresh_token(refresh_token)

        # Remove internal fields (exp, type)
        new_payload = {
            key: value for key, value in payload.items()
            if key not in ["exp", "type"]
        }

        return JWTManager.create_access_token(new_payload)