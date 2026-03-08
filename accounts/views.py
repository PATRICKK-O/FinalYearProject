from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from .forms import UserRegistrationForm
from .models import UserProfile
from django.contrib import messages, auth
from django.http import JsonResponse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
# from django.contrib.auth.decorators import login_required


def register(request):
  if request.method == "POST":
    form = UserRegistrationForm(request.POST, request.FILES)
    if form.is_valid():
      user = form.save()
      
      # After saving the user, we create a profile for them
      UserProfile.objects.create(
        user = user,
        course_of_interest = form.cleaned_data.get('course_of_interest'),
        profile_picture = form.cleaned_data.get('profile_picture')
      )
      # Automatic login after registration
      auth_login(request, user)
      return redirect('/home/')
    else:
      return render(request, 'register.html', {'form': form})
    
  else: 
    form = UserRegistrationForm()
      
  return render(request, 'register.html', {'form': form})


def login_view(request):
  if request.method == "POST":
    user_name = request.POST['user_name']
    password = request.POST['password']
    
    user = auth.authenticate(username=user_name, password=password)
    
    if user is None:
      messages.info(request, "Invalid Credentials")
      return redirect('/accounts/login')
    else:
      auth.login(request, user)
      return redirect('/home/')
  
  return render(request, 'login.html')  


def logout(request):
  # We clear the cached recommendations here
  request.session.pop('cached_recommendations', None)
  request.session.pop('cold_start', None)
  
  # Then we log out
  auth.logout(request)
  return redirect('/')



@csrf_exempt
@require_http_methods(["POST"])
def validate_password_ajax(request):
  """
  AJAX endpoint to validate password using Django's built-in validators
  """
  try:
    data = json.loads(request.body)
    password = data.get('password', '')
    username = data.get('username', '')
    email = data.get('email', '')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    
    # Create a temporary user object for validation context
    user = User(
      username=username,
      email=email,
      first_name=first_name,
      last_name=last_name
    )
      
    validation_errors = []
    
    try:
      # Use Django's built-in password validation
      validate_password(password, user=user)
      is_valid = True
    except ValidationError as e:
      validation_errors = e.messages
      is_valid = False
  
    # Return structured response
    return JsonResponse({
      'is_valid': is_valid,
      'errors': validation_errors,
      'requirements': {
        'length': len(password) >= 8,
        'not_common': 'This password is too common.' not in validation_errors,
        'not_numeric': 'This password is entirely numeric.' not in validation_errors,
        'not_similar': not any('similar' in error.lower() for error in validation_errors)
      }
    })
      
  except Exception as e:
    return JsonResponse({
      'is_valid': False,
      'errors': ['An error occurred during validation.'],
      'requirements': {}
    })  