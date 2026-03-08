from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import track_activity

urlpatterns = [
  path('', views.index),
  path('home/', views.home, name='home'),
  path('recommended/', views.recommended, name='recommended'),
  path('search/', views.search, name='search'),
  path('search_suggestions/', views.search_suggestions, name='search_suggestions'),
  path('trending/', views.trending_materials, name='trending'),
  path('load_recommendations/', views.load_recommendations, name='load_recommendations'),
  path('track/<int:material_id>/<str:type>/', track_activity, name='track_activity'),
  path('save/<int:material_id>/', views.save_material, name='save_material'),
  path('remove/<int:material_id>/', views.remove_saved_material, name='remove_saved_material'),
  path('saved/', views.saved_materials, name='saved_materials')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)