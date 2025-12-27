from rest_framework import views, generics, status, response
from . import serializers
from . import models
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from helper.utils import delete_session
from workflows.create_debate_agents.flows import debate_agents_creation_graph


class RegisterView(generics.CreateAPIView):
    serializer_class = serializers.RegisterSerializer
    queryset = models.User.objects.all()
    authentication_classes = []
    permission_classes = [AllowAny]
    
    
class LoginView(views.APIView):
    serializer_class = serializers.LoginSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)        
        login_data = serializer.validated_data
        return response.Response(login_data, status=status.HTTP_200_OK)
     

class ChangePasswordView(views.APIView):
    """Allow authenticated user to change password."""
    serializer_class = serializers.ChangePasswordSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return response.Response({'detail': "Password changed successfully"}, status=status.HTTP_200_OK)
     

class ForgotPasswordRequestView(views.APIView):
    """Send a password reset link or OTP to the user's email."""
    serializer_class = serializers.ForgotPasswordRequestSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return response.Response({'detail': "Password reset link sent to your email"}, status=status.HTTP_200_OK)
     

class ResetPasswordView(views.APIView):
    """Reset password using OTP or token."""
    serializer_class = serializers.ResetPasswordSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return response.Response({'detail': "Password Reset successfully"}, status=status.HTTP_200_OK)
    

######################################################### User Self Info ###############################################################

class UserSelfRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's own profile."""
    serializer_class = serializers.UserSelfUpdateSerializer
    queryset = models.User.objects.all()

    def get_object(self):
        return self.request.user
