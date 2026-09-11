from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView  # <--- Импортируем отсюда
from apps.testapp import views

urlpatterns = [
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # <--- Убрали views.
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/stats/', views.ProfileStatsView.as_view(), name='profile_stats'),
]