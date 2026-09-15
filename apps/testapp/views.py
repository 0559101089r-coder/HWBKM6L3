from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    UserStatsSerializer,
    GoogleAuthSerializer,
    generate_tokens_for_user
)

from .services import get_google_access_token, get_google_user_info

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Успешный выход из системы."}, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileStatsView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserStatsSerializer

    def get_object(self):
        return self.request.user
    

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']

        google_access_token = get_google_access_token(code)
        user_info = get_google_user_info(google_access_token)
        
        email = user_info['email']
        name = user_info['name']

        
        user, is_new_user = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],  
                'first_name': name,
            }
        )

        if is_new_user:
            user.set_unusable_password()
            user.save()

        
        tokens = generate_tokens_for_user(user)

        
        return Response(
            {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                },
                'is_new_user': is_new_user,
                'tokens': tokens,
            },
            status=status.HTTP_200_OK if not is_new_user else status.HTTP_201_CREATED
        )