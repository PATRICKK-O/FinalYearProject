from django import forms
from .models import MaterialType

class MaterialFilterForm(forms.Form):
  SUBJECT_CHOICES = [
    ('maths', 'Mathematics'),
    ('english', 'English'),
    ('physics', 'Physics'),
    ('chemistry', 'Chemistry')
  ]
  
  LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced')
  ]
  
  subject = forms.ChoiceField(choices = SUBJECT_CHOICES, required = True, label = "Subject")
  level = forms.ChoiceField(choices = LEVEL_CHOICES, required = True, label = "Level")
  material_types = forms.ModelMultipleChoiceField(
    queryset = MaterialType.objects.all(),
    widget = forms.CheckboxSelectMultiple,
    required = True,
    label = "Material Type"
  ) 