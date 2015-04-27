from django import forms
from mealmatcher_app.models import UserProfile, Meal 
from django.utils import timezone
from django.contrib.auth.models import User 
import datetime
from django.db import models

# for editing attire for a meal
class EditAttireForm(forms.Form): 
  idToEdit = forms.CharField(
    widget = forms.TextInput(attrs={'id': "idToEditTextbox"}),
    max_length = 3, # will this not work for larger inputs?
  )
  newAttire = forms.CharField(
    widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What will you be wearing?'}),
     help_text = "Enter a new attire for the meal",
     max_length=100,
  )
  class Meta:
    fields = ('idToEdit','newAttire')
    exclude = ()

# for deleting a meal
class DeleteMealForm(forms.Form):
  idToDelete = forms.CharField(
    widget = forms.TextInput(attrs={'id': "idToDeleteTextbox"}),
    max_length = 3,  
  )

  class Meta:
    fields = ('idToDelete',)
    exclude = ()

# for joining a meal, needs new attire too
class JoinMealForm(forms.Form):
  idToJoin = forms.CharField(
    widget = forms.TextInput(attrs={'id': "idToJoinTextbox"}),
    max_length = 3,  
  )
  newAttire = forms.CharField(
    widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What will you be wearing?'}),
     help_text = "Enter an attire for the meal",
     max_length=100,
  )
  class Meta:
    fields = ('idToJoin','newAttire')
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
      ('R', 'Brunch'),
      ('L', 'Lunch'),
      ('D', 'Dinner'),
    )
  )

  location = forms.ChoiceField(
    widget = forms.Select(attrs={'class': 'form-control'}),
    help_text = "at",
    choices = (
      ('WH', 'Whitman'),
      ('RM', 'Rocky'),
      ('MR', 'Mathey'),
      ('BW', 'Butler'),
      ('WB', 'Wilson'),
      ('F', 'Forbes'),
    )
  )


  attire1 = forms.CharField(
    widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What will you be wearing?'}),
     help_text = "and I'll be wearing",
     max_length=100,
   )


  class Meta:
    model = Meal
    fields = ('date_mdy', 'meal_time', 'date_time', 'location', 'attire1',)
    exclude = ('date', 'attire2', 'users',)


