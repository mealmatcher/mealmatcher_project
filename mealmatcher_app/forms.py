from django import forms
from mealmatcher_app.models import UserProfile, Meal 
from django.utils import timezone
from django.contrib.auth.models import User 
import datetime
from django.db import models

class MealForm(forms.ModelForm):
  # filled in by JS, mm/dd but not necessarily leading 0s
  date_mdy = forms.ChoiceField(
    widget = forms.Select(attrs={'id': 'dateDropdown'}),
    help_text = "on",
    choices = ()
  ) 

  # filled in by JS, hour:minutes-hour:minutes
  date_time = forms.ChoiceField(
    widget = forms.Select(attrs={'id': 'timeDropdown'}),
    help_text = "at",
    choices = ()
  ) 
  
  meal_time = forms.ChoiceField(
    widget = forms.Select(attrs={'id': 'mealDropdown', 'name': 'mealDropdown'}),
    help_text = "I want to get ",
    choices = (
      ('B', 'Breakfast'),
      ('L', 'Lunch'),
      ('D', 'Dinner'),
    )
  )

  location = forms.ChoiceField(
    help_text = "at ",
    choices = (
      ('WH', 'Whitman'),
      ('RM', 'Rocky/Mathey'),
      ('BW', 'Butler/Wilson'),
      ('F', 'Forbes'),
    )
  )

  attire1 = models.CharField(
     help_text = "and I'll be wearing...",
     max_length=100,  
   )


  class Meta:
    model = Meal
    fields = ('meal_time', 'location', 'date_mdy', 'date_time', 'attire1',)
    exclude = ('date', 'attire2', 'users',)


