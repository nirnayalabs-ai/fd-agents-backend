import jwt
from .models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .utils import JWTManager

class CustomJWTAuthentication(BaseAuthentication):
    """
    Custom authentication class that uses a JWT token from the 'Authorization' header
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            raise AuthenticationFailed('Authorization header is required for authentication.')

        try:
            token = auth_header.split()[1]
        except IndexError:
            raise AuthenticationFailed('Invalid token header. No token provided.')

        try:
            decoded_payload = JWTManager.verify_access_token(token=token)
        except Exception as e:
            raise AuthenticationFailed(str(e))

        user_id = decoded_payload.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')
        
        if not user.is_active:
            raise AuthenticationFailed('User is inactive.')

        from config import context_storage
        context_storage.set_current_user(user)
        return (user, decoded_payload)

    def authenticate_header(self, request):
        """
        Return a string to be used in the 'WWW-Authenticate' header.
        This is used when the authentication fails.
        """
        return 'Bearer'