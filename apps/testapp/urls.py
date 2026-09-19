from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import GoogleAuthView, PostListCreateAPIView  
from apps.testapp import views

urlpatterns = [
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/stats/', views.ProfileStatsView.as_view(), name='profile_stats'),
    path('auth/google/', GoogleAuthView.as_view(), name='google_auth'),  # Добавляем путь для Google OAuth
    path('posts/', PostListCreateAPIView.as_view(), name='post_list_create'),
]