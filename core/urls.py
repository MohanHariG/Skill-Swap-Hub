from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.feed, name='feed'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('post/new/', views.post_create_view, name='post_create'),
    path('profile/', views.profile_view, name='profile'),
    path('connect/<int:post_id>/', views.send_match_request, name='connect'),
    path('matches/', views.matches_view, name='matches'),
    path('matches/accept/<int:pk>/', views.accept_match, name='accept_match'),
    path('matches/reject/<int:pk>/', views.reject_match, name='reject_match'),
    path('sessions/', views.sessions_view, name='sessions'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
