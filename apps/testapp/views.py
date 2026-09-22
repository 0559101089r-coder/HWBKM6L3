from django.contrib.auth import get_user_model
from django.core.cache import cache
from .tasks import send_welcome_email_task
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Post
from .serializers import (
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    UserStatsSerializer,
    GoogleAuthSerializer,
    generate_tokens_for_user,
    PostSerializer
)
from .services import get_google_access_token, get_google_user_info

User = get_user_model()

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
         
        if is_new_user:
           user.set_unusable_password()
           user.save()

           send_welcome_email_task.delay(user.email)
        
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
    

class PostListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        cache_key = "posts_list"

        # 1. Проверяем Redis
        cached_posts = cache.get(cache_key)
        if cached_posts is not None:
            return Response(cached_posts, status=status.HTTP_200_OK)

        # 2. Если нет в кэше — делаем запрос к БД
        posts = Post.objects.select_related('author').all()
        serializer = PostSerializer(posts, many=True)
        data = serializer.data

        # 3. Записываем в Redis на 60 секунд
        cache.set(cache_key, data, timeout=60)

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)

            # 4. Очищаем кэш при добавлении записи
            cache.delete("posts_list")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)