from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
  email = forms.EmailField(required=True)
  course_of_interest = forms.CharField(max_length = 100, required=True)
  profile_picture = forms.ImageField(required=False)
  
  class Meta:
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'course_of_interest', 'password1', 'password2']