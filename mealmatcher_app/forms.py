from django import forms
from mealmatcher_app.models import UserProfile, Meal 
from django.utils import timezone
from django.contrib.auth.models import User 
import datetime
from django.db import models

class MealForm(forms.ModelForm):
	date_mdy = forms.CharField(max_length=5)   #mm/dd but not necessarily leading 0s
	date_time = forms.CharField(max_length=11) #hour:minutes-hour:minutes
	MEALS = (
		('B', 'Breakfast'),
		('L', 'Lunch'),
		('D', 'Dinner'),
	)
	meal_time = forms.CharField(max_length=1)#, choices=MEALS)
	LOCATIONS = (
		('WH', 'Whitman'),
		('RM', 'Rocky/Mathey'),
		('BW', 'Butler/Wilson'),
		('F', 'Forbes'),
	)
	location = forms.CharField(max_length=2)#, choices=LOCATIONS)

	attire1 = models.CharField(max_length=100)

	class Meta:
		model = Meal
		fields = ('meal_time', 'location', 'attire1',)
		exclude = ('date', 'attire2', 'users',)



















