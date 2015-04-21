from django import forms
from mealmatcher_app.models import UserProfile, Meal 
from django.utils import timezone
from django.contrib.auth.models import User 
import datetime
from django.db import models

class DeleteMealForm(forms.Form):
  idToDelete = forms.CharField(
    widget = forms.TextInput(attrs={'id': "idToDeleteTextbox"}),
    max_length = 3,  
  )

  class Meta:
    fields = ('idToDelete',)
    exclude = ()

class JoinMealForm(forms.Form):
  idToJoin = forms.CharField(
    widget = forms.TextInput(attrs={'id': "idToJoinTextbox"}),
    max_length = 3,  
  )

  class Meta:
    fields = ('idToJoin',)
    exclude = ()


class MealForm(forms.ModelForm):
  # filled in by JS, mm/dd but not necessarily leading 0s
  date_mdy = forms.CharField(
    widget = forms.Select(attrs={'id': 'dateDropdown', 'class': 'form-control'}),
    max_length = 5,
    help_text = "on"
  )

  # filled in by JS, hour:minutes-hour:minutes
  date_time = forms.CharField(
    widget = forms.Select(attrs={'id': 'timeDropdown', 'class': 'form-control'}),
    max_length = 11,    
    help_text = "at",
  ) 
  
  meal_time = forms.ChoiceField(
    widget = forms.Select(attrs={'id': 'mealDropdown', 'name': 'mealDropdown', 'class': 'form-control'}),
    help_text = "I want to get",
    choices = (
      ('B', 'Breakfast'),
      ('L', 'Lunch'),
      ('D', 'Dinner'),
    )
  )

  location = forms.ChoiceField(
    widget = forms.Select(attrs={'class': 'form-control'}),
    help_text = "at",
    choices = (
      ('WH', 'Whitman'),
      ('RM', 'Rocky/Mathey'),
      ('BW', 'Butler/Wilson'),
      ('F', 'Forbes'),
    )
  )

  attire1 = forms.CharField(
     help_text = "and I'll be wearing",
     max_length=100,
   )


  class Meta:
    model = Meal
    fields = ('meal_time', 'date_time', 'date_mdy', 'location', 'attire1',)
    exclude = ('date', 'attire2', 'users',)


