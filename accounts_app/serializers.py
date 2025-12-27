import requests
from django.db import transaction
from rest_framework import serializers
from accounts_app import models
from orgs_app.models import Organization, OrganizationMember
from helper.exceptions import SmoothException
from helper.utils import decode_token, encode_token, create_session, retrieve_session
from .utils import JWTManager

###################################################################### Authentication ######################################################################


class UserSerializer(serializers.ModelSerializer):
    organization_memberships = serializers.SerializerMethodField(read_only = True)

    def get_organization_memberships(self, obj):
        organization_memberships = OrganizationMember.all_objects.filter(user = obj)
        return [
            {
                "org_id" : membership.org.id,
                "org_name" : membership.org.name,
                "role" : membership.role
            }
            for membership in organization_memberships
        ]


    class Meta:
        model = models.User
        exclude = ['password']



class UserSelfUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating own basic profile details."""
    
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = models.User
        fields = ['id', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        """Create and return a new user."""
        
        request = self.context.get('request')
        invitation_id = request.GET.get('invitation_id')
        
        with transaction.atomic():
            if invitation_id:
                invitation : models.Invitation = models.Invitation.objects.filter(id=invitation_id).first()

                if not invitation:
                    raise SmoothException.error(
                        detail="Invitation does not exist.",
                        dev_message=f"No invitation found with ID: {invitation_id}"
                    )
                if invitation.is_expired:
                    raise SmoothException.warning(
                        detail="Invitation has expired.",
                        dev_message=f"Attempted to use expired invitation ID: {invitation_id}"
                    )
                if invitation.is_accepted:
                    raise SmoothException.warning(
                        detail="Invitation has already been used.",
                        dev_message=f"Attempted to reuse accepted invitation ID: {invitation_id}"
                    )
                if invitation.to_email != validated_data.get('email'):
                    raise SmoothException.error(
                        detail="Email does not match the invitation.",
                        dev_message=f"Attempted to use invitation ID {invitation_id} with mismatched email: {validated_data.get('email')}"
                    )
                
                data = JWTManager._decode(invitation.token)
                role = data.get('role')
                org_id = data.get('org_id')
                user, _ = models.User.objects.get_or_create_user(**validated_data)
                org = Organization.objects.get(id = org_id)
                OrganizationMember.objects.create(
                    org = org,
                    user = user,
                    role = role
                )
                invitation.is_accepted = True
                invitation.save()          
                return user
            
            user = models.User.objects.get_or_create_user(**validated_data)
            return user                
            

    def to_representation(self, instance):
        return {
            "detail" : "Registration completed successfully.",
        }

    class Meta:
        model = models.User
        fields = ['email', 'password', 'first_name', 'last_name']
        

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate the email and password, then authenticate and generate a token."""

        email = data.get('email')
        password = data.get('password')
        login_data = {}

        user : models.User = models.User.objects.filter(email=email).first()
        if not user:
            raise SmoothException.error(
                detail="User with this email does not exist.",
                dev_message=f"Login attempt failed: No user found with email {email}"
            )

        if not user.check_password(password):
            raise SmoothException.error(
                detail="Incorrect password.",
                dev_message=f"Failed login attempt for user {email}: Incorrect password"
            )

        if not user.is_active:
            raise SmoothException.warning(
                detail="This account is deactivated. Contact your administrator to activate it.",
                dev_message=f"Login attempt for deactivated account {email}"
            )

        payload = {"user_id": str(user.id),}
        access_token = JWTManager.create_access_token(payload)
        refresh_token = JWTManager.create_refresh_token(payload)
        user_data = UserSerializer(user).data
        
        login_data['user'] = user_data
        login_data['tokens'] = {
            "access" : access_token,
            "refresh" : refresh_token
        }
        return login_data
    
    
class SocialLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    given_name = serializers.CharField()
    family_name = serializers.CharField()

    def authenticate_google(self, token):
        google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        response = requests.get(google_url)
        if response.status_code == 200:
            return response.json()
        return None        
        
    def authenticate_microsoft(self, token):
        microsoft_url = f"https://graph.microsoft.com/v1.0/me"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(microsoft_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None


    def validate(self, data):
        """Validate the email, given name and family, then authenticate and generate a token."""

        provider = data.get('provider')
        token = data.get('token')
        login_data = {}
        
        if provider == "google":
            user_data = self.authenticate_google(token)
        elif provider == "microsoft":
            user_data = self.authenticate_microsoft(token)
        else:
            raise SmoothException.error(
                detail="Invalid provider!",
                dev_message=f"Unsupported authentication provider: {provider}",
                status_code=401
            )

        if not user_data:
            raise SmoothException.error(
                detail="Invalid token.",
                dev_message=f"Failed authentication attempt with provider {provider} - Invalid token",
                status_code=401
            )
        
        email = user_data.get('email')
        first_name = user_data.get('given_name')
        last_name = user_data.get('family_name')
        
        user, created = models.User.objects.get_or_create(email=email, first_name=first_name, last_name=last_name)
        if created:
                user.set_unusable_password()
                user.save()        
        
        session_data = {
            "user_id": str(user.id),
        }
        session_key = create_session(session_data)
        token = encode_token({
            'session_key' : session_key
        })
        user_data = UserSerializer(user).data
        
        login_data['user'] = user_data
        login_data['token'] = str(token)
        return login_data
    

class ChangePasswordSerializer(serializers.Serializer):
    """Change password for authenticated user."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate old password and update to new password."""
        user = getattr(self.context.get("request"), "user", None)

        if not user:
            raise SmoothException.error("User not found.", "No user on request.")

        if not user.check_password(data.get("old_password")):
            raise SmoothException.error(
                "Incorrect old password.",
                f"Incorrect old password for {user.email}"
            )

        user.set_password(data.get("new_password"))
        user.save()
        return data


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password using session token."""

    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate session token and update password."""
        request = self.context.get("request")
        session_token = request.GET.get("session_token")

        if not session_token:
            raise SmoothException.error("Session Token is required.", "No token provided.")

        payload = decode_token(session_token)
        session_key = payload.get("session_key")

        if not session_key:
            raise SmoothException.error("Session Token is invalid.", "Invalid token data.")

        session_data = retrieve_session(session_key)
        if not session_data:
            raise SmoothException.error("Session has expired.", f"Expired key: {session_key}")

        user = models.User.objects.filter(id=session_data.get("user_id")).first()
        if not user:
            raise SmoothException.error("User not found.", f"No user for session.")

        user.set_password(data.get("new_password"))
        user.save()
        return data

    def to_representation(self, instance):
        return {"detail": "Password changed successfully."}


class ForgotPasswordRequestSerializer(serializers.Serializer):
    """Send password reset link to email."""

    email = serializers.EmailField()

    def validate(self, data):
        """Generate reset token and email it to user."""
        email = data.get('email')
        user = models.User.objects.filter(email=email).first()

        if not user:
            raise SmoothException.error(
                "User with this email does not exist.",
                f"No user found with email {email}"
            )

        session_key = create_session({"user_id": str(user.id)}, expiry_seconds=600)
        token = encode_token({'session_key': session_key})

        user.send_password_reset_email(token)
        return data

    def to_representation(self, instance):
        return {"detail": "Password reset link sent to your email."}
