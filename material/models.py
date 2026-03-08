from django.db import models
from django.contrib.auth.models import User

class MaterialType(models.Model):
  type_name = models.CharField(max_length = 50, choices=[
    ('pdf', 'PDF'),
    ('video', 'Video')
  ], unique = True)
  
  def __str__(self):
    return self.type_name

class Material(models.Model):
  name = models.CharField(max_length = 255)
  subject = models.CharField(max_length = 50, choices = [
    ('maths', 'Mathematics'),
    ('english', 'English'),
    ('physics', 'Physics'),
    ('chemistry', 'Chemistry')
  ])
  level = models.CharField(max_length = 50, choices = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced')
  ])
  material_types = models.ManyToManyField(MaterialType) # Checkbox for type selection
  pdf_file = models.FileField(upload_to='pdf_files/', blank=True, null=True) # stores pdf
  video_link = models.URLField(blank=True, null=True) # stores YouTube links
  description = models.TextField()
  keywords = models.TextField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.name   
  
class UserActivity(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  subject = models.CharField(max_length = 50)
  level = models.CharField(max_length = 50)
  timestamp = models.DateTimeField(auto_now_add=True)  
  
  def __str__(self):
    return f"{self.user.username} - {self.subject} ({self.level})" 
  
class SearchHistory(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  query = models.CharField(max_length=255)
  timestamp = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return f"{self.user.username} - {self.query}" 
  
class SavedMaterial(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  material = models.ForeignKey(Material, on_delete=models.CASCADE)   
  saved_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return f"{self.user.username} saved {self.material.name}"