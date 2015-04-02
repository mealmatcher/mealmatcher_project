import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# UserProfile is our user class. Has a 1-1 relation with the Django User class
class UserProfile(models.Model):
	# required to link UserProfile to User
	user = models.OneToOneField(User)

	# no additional attributes for now

	def __unicode__(self):
		return self.user.username

# Meal is the meal class. Has a Many-to-One relation with 2 users
class Meal(models.Model):

	date = models.DateTimeField('Date of meal')

	TIMES = (
		('B', 'Breakfast'),
		('L', 'Lunch'),
		('D', 'Dinner'),
	)
	time = models.CharField(max_length=1, choices=TIMES)

	LOCATIONS = (
		('WH', 'Whitman'),
		('RM', 'Rocky/Mathey'),
		('BW', 'Butler/Wilson'),
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

	# True if the meal has already occured
	def is_expired(self):
		now = timezone.now()
		return (now >= self.date + datetime.timedelta(days=1))
	is_expired.boolean = True
	is_expired.short_description = 'Has the meal expired?'

	def __unicode__(self):
		return self.date.strftime("%Y-%m-%d") + " " + self.location + " " + self.time

