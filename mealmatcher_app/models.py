import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# UserProfile is a helper class. Has a 1-1 relation with the Django User class
# Used only to link the meals with the users -- perhaps unneeded, and we could 
# directly link meals with Django builin Users, but too late to change
class UserProfile(models.Model):
	# required to link UserProfile to User
	user = models.OneToOneField(User)
	def __unicode__(self):
		return self.user.username

# Meal is the meal class. Has a Many-to-One relation with 2 users,
# which is modeled here with a Many to Many relation

# Other fields include date (date AND time of meal), meal_time (which meal
# is it), location (dining hall of the menu, 1 of 6 res colleges),
# attire1 (the user1 attire for the meal), attire2 (user2 attire)
class Meal(models.Model):

	date = models.DateTimeField('Date of meal') # date and time

	MEALS = (
		('B', 'Breakfast'),
		('L', 'Lunch'),
		('D', 'Dinner'),
		('R', 'Brunch'),
	)
	meal_time = models.CharField(max_length=1, choices=MEALS)

	LOCATIONS = (
		('WH', 'Whitman'),
		('RM', 'Rocky'),
		('BW', 'Butler'),
		('MR', 'Mathey'),
		('WB', 'Wilson'),
		('F', 'Forbes'),
	)
	location = models.CharField(max_length=2, choices=LOCATIONS)

	attire1 = models.CharField('Person 1 Attire', max_length=100, blank=True)
	attire2 = models.CharField('Person 2 Attire', max_length=100, blank=True) # can be blank

	users = models.ManyToManyField(UserProfile)

	# True if there are two users associated with the meal
	def is_matched(self):
		if (self.users == None):
			return False
		else:
			return (self.users.count() == 2)
	is_matched.boolean = True
	is_matched.short_description = 'Are there are two users associated with the meal?'

	# True if the time is within 1 hour of the mealtime in either direction, and if it is matched
	def is_ongoing(self):
		now = timezone.now()
		return self.is_matched() and ((now + datetime.timedelta(hours=1)) > self.date) and now < ((self.date + datetime.timedelta(hours=1)))
	is_ongoing.boolean = True
	is_ongoing.short_description = 'Is the meal upcoming or ongoing?'


	# True if the meal should no longer be matched with, which occurs 1 hour before mealtime
	def is_expired(self):
		now = timezone.now()
		return ((now + datetime.timedelta(hours=1)) > self.date )
	is_expired.boolean = True
	is_expired.short_description = 'Should the meal no longer be considered?'

	# True is it has been over 2 weeks since a meal occurred. Will be removed from db
	def to_be_removed(self):
		now = timezone.now()
		return ((now - datetime.timedelta(days=14)) > self.date )
	to_be_removed.boolean = True
	to_be_removed.short_description = 'Should the meal be removed (occurred over a week ago)?'

	# prints out meal date, location, and which meal_time it is. This is what is viewed in print
	# statements and shell interaction 
	def __unicode__(self):
		return self.date.strftime("%Y-%m-%d") + " " + self.location + " " + self.meal_time + " "

