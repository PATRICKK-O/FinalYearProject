from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
  course_of_interest = models.CharField(max_length = 100)
  profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
  
  def __str__(self):
    return self.user.username  