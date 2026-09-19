from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import get_user_model

from apps.testapp.models import Post

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'username': self.user.username,
            'role': getattr(self.user, 'role', None), # Подтянет поле role из CustomUser (если его нет — вернет None)
        }
        return data
    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    
    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            self.fail('bad_token')


class UserStatsSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='get_role_display')

    class Meta:
        model = User
        fields = ['email', 'role', 'is_staff', 'date_joined']

class GoogleAuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, allow_blank=False)


def generate_tokens_for_user(user) -> dict:
    refresh = RefreshToken.for_user(user)
    
    refresh['email'] = user.email
    refresh['role'] = getattr(user, 'role', 'user')  # Берем роль из модели или дефолт 'user'
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class PostSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author_email', 'created_at']