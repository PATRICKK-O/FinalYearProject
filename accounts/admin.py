from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
  list_display = ('user', 'course_of_interest')

  
admin.site.register(UserProfile, UserProfileAdmin)