from django import forms
from mealmatcher_app.models import UserProfile, Meal 
from django.utils import timezone
from django.contrib.auth.models import User 
import datetime
from django.db import models

class MealForm(forms.ModelForm):
  # filled in by JS, mm/dd but not necessarily leading 0s
  date_mdy = forms.CharField(
    max_length = 5,
    widget = forms.Select(attrs={'id': 'dateDropdown'}),
    help_text = "on"
    # choices = ( # HACK(drew): this tuple must include all options filled in dynamically in findmeal.html
    #   ("4/1", "4/1"),
    #   ("4/2", "4/2"),
    #   ("4/3", "4/3"),
    #   ("4/4", "4/4"),
    #   ("4/5", "4/5"),
    #   ("4/6", "4/6"),
    #   ("4/7", "4/7"),
    #   ("4/8", "4/8"),
    #   ("4/9", "4/9"),
    #   ("4/10", "4/10"),
    #   ("4/11", "4/11"),
    #   ("4/12", "4/12"),
    #   ("4/13", "4/13"),
    #   ("4/14", "4/14"),
    #   ("4/15", "4/15"),
    #   ("4/16", "4/16"),
    #   ("4/17", "4/17"),
    #   ("4/18", "4/18"),
    #   ("4/19", "4/19"),
    #   ("4/20", "4/20"),
    #   ("4/21", "4/21"),
    # )
  )

  # filled in by JS, hour:minutes-hour:minutes
  date_time = forms.ChoiceField(
    widget = forms.Select(attrs={'id': 'timeDropdown'}),
    help_text = "at",
    choices = ( # HACK(drew): this tuple must include all options filled in dynamically in findmeal.html
      ("7:30-8:00", "7:30 - 8:00"),
      ("8:00-8:30", "8:00 - 8:30"),
      ("8:30-9:00", "8:30 - 9:00"),
      ("9:00-9:30", "9:00 - 9:30"),
      ("9:30-10:00", "9:30 - 10:00"),
      ("10:00-10:30", "10:00 - 10:30"),
      ("10:30-11:00", "10:30 - 11:00"),
      ("11:00-11:45", "11:00 - 11:45"),
      ("11:45-12:30", "11:45 - 12:30"),
      ("12:30-1:15", "12:30 - 1:15"),
      ("1:15-2:00", "1:15 - 2:00"),
      ("5:00-5:45", "5:00 - 5:45"),
      ("5:45-6:30", "5:45 - 6:30"),
      ("6:30-7:15", "6:30 - 7:15"),
      ("7:15-8:00", "7:15 - 8:00"),
    )
  ) 
  
  meal_time = forms.ChoiceField(
    widget = forms.Select(attrs={'id': 'mealDropdown', 'name': 'mealDropdown'}),
    help_text = "I want to get",
    choices = (
      ('B', 'Breakfast'),
      ('L', 'Lunch'),
      ('D', 'Dinner'),
    )
  )

  location = forms.ChoiceField(
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


