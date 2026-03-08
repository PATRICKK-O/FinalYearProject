from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
  path('register/', views.register, name='register'),
  path('login/', views.login_view, name='login'),
  path('logout/', views.logout, name='logout'),
  path('validate-password/', views.validate_password_ajax, name='validate_password_ajax')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)