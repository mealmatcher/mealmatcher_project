from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
# from django.db.models import Q
from django.contrib.auth import login as django_login
from mealmatcher_app.models import UserProfile, Meal
from mealmatcher_app.forms import MealForm, DeleteMealForm, JoinMealForm, EditAttireForm
import datetime, random
import pytz
from django.utils import timezone as django_timezone
import urllib2, re
# mailer lib
from post_office.models import EmailTemplate
from post_office import mail
from django.template.loader import render_to_string
from django.utils import timezone
from django import template
from django.template.loader import get_template

# index is the app homepage
@login_required
def index(request):
	context_dict = {'user': request.user, 'first_name': request.user.first_name, 
					'last_name': request.user.last_name, 'username': request.user.username}
	return render(request, 'mealmatcher_app/index_new_replaced.html', context_dict)

# used to contain logic for editing attire of a meal in my-meals 
# redirects to my-meals if success, error page if failure in saving, and my-meals if 
# the URL is attempted to be accessed without a POST
@login_required
def edit_attire(request): # TODO: add email support by Andreas
	if request.method == "POST":
		form = EditAttireForm(request.POST)

		# verify form data, and attire size. #TODO: form security check by kevin 
		if form.is_valid():
			data = form.cleaned_data
			newAttire = data['newAttire']
			if len(newAttire) > 100: newAttire = newAttire[0:100] 
			matchingMeals = Meal.objects.filter(id=data['idToEdit']) 

			# got a meal, see whether user is user1 or user2 by order
			if len(matchingMeals) >= 1:
				mealToEdit = matchingMeals[0]
				my_user_profile = UserProfile.objects.filter(user=request.user)[0]


				user1 = mealToEdit.users.all()[0].user.first_name
				user1net = mealToEdit.users.all()[0].user.username

				if mealToEdit.is_matched():
					user2 = mealToEdit.users.all()[1].user.first_name
					user2net = mealToEdit.users.all()[1].user.username

				send_meal = mealToEdit.meal_time
				send_location = mealToEdit.location

				#mailer
				if (send_meal == "B"):
					send_meal = "Breakfast"
				elif (send_meal == "L"):
					send_meal = "Lunch"
				elif (send_meal == "D"):
					send_meal = "Dinner"
				else:
					send_meal = "Brunch"

				if (send_location == "BW"):
					send_location = "Butler"
				elif (send_location == "WB"):
					send_location = "Wilson"
				elif (send_location == "RM"):
					send_location = "Rocky"
				elif (send_location == "MR"):
					send_location = "Mathey"
				elif (send_location == "WH"):
					send_location = "Whitman"
				else:
					send_location = "Forbes"

				if mealToEdit.users.all()[0] == my_user_profile: # change user1 attire
					mealToEdit.attire1 = newAttire
					mealToEdit.save()

					#mailer
					if mealToEdit.is_matched():
						mail.send(
							[user2net + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							subject='Notification About Your Partner\'s Attire',
							html_message=render_to_string('mealmatcher_app/attire_alert_email.html', {'name': user2, 'datetime': mealToEdit.date, 'meal': send_meal, 'location': send_location, 'attire': mealToEdit.attire1}),
							priority='now',
						)

				elif mealToEdit.is_matched() and mealToEdit.users.all()[1] == my_user_profile: # change user2 attire
					mealToEdit.attire2 = newAttire
					mealToEdit.save()

					#mailer
					mail.send(
						[user1net + '@princeton.edu'],
						'princeton.meal.matcher@gmail.com',
						subject='Notification About Your Partner\'s Attire',
						html_message=render_to_string('mealmatcher_app/attire_alert_email.html', {'name': user1, 'datetime': mealToEdit.date, 'meal': send_meal, 'location': send_location, 'attire': mealToEdit.attire2}),
						priority='now',
					)


				return HttpResponseRedirect('/my-meals/')
			else:
				print 'edit_attire error: no meal found with that id'
				return error(request)

		else: # form data is invalid. print errors, give error page
			print 'edit_attire error: edit meal form was invalid '
			print form.errors
			return error(request)

	else: # not a POST -- this url should not have been reached, redirect to mymeals page
		print 'edit_attire error: edit page attemped access without a GET'
		# return render(request, 'mealmatcher_app/error.html')
		return HttpResponseRedirect('/my-meals/')

# helper function, used by join meals to add a second user to the meal
def match_meal(attire1, my_user_profile, matched_meal):
	matched_meal.attire2 = attire1
	matched_meal.save()
	matched_meal.users.add(my_user_profile) # add my_user_profile as the second user
	matched_meal.save()

	# TODO below: Email support -- notifications for both
	#mailer user 
	# matchedUsers = matched_meal.users.all()
	# TODO error if not found
	# if len(matchedUsers) > 0:
	# user2 = matchedUsers[0].user.username

	# print(type(matched_meal.users))
	# print(type(my_user_profile))

	# HACK(drew): match with dummy user for debug
	# dummyProfile = None
	# dummyUser = None
	# dummyUsers = User.objects.filter(username="nobody")
	# if len(dummyUsers) == 0:
	# 	username = "nobody"
	# 	password = "nobody"
	# 	dummyUser = User(username=username, password=password, email= ("nobody" + '@princeton.edu'))
	# 	dummyUser.save()
	# 	dummyUser.set_password(dummyUser.password)
	# 	dummyUser.save()
	# 	dummyProfile = UserProfile(user = dummyUser)
	# 	dummyProfile.save()
	# else:
	# 	dummyUser = dummyUsers[0]
	# 	dummyProfile = UserProfile.objects.filter(user=dummyUser)[0]

	# matched_meal.users.add(dummyProfile)

	#mailer users
	user1 = matched_meal.users.all()[1].user.first_name
	user2 = matched_meal.users.all()[0].user.first_name	
	user1net = matched_meal.users.all()[1].user.username
	user2net = matched_meal.users.all()[0].user.username	

	#mailer

	meal = matched_meal.meal_time
	location = matched_meal.location

	if (meal == "B"):
		meal = "Breakfast"
	elif (meal == "L"):
		meal = "Lunch"
	elif (meal == "D"):
		meal = "Dinner"
	else:
		meal = "Brunch"

	if (location == "BW"):
		location = "Butler"
	elif (location == "WB"):
		location = "Wilson"
	elif (location == "RM"):
		location = "Rocky"
	elif (location == "MR"):
		location = "Mathey"
	elif (location == "WH"):
		location = "Whitman"
	else:
		location = "Forbes"

	#mailer view
	mail.send(
		[user1net + '@princeton.edu'],
		'princeton.meal.matcher@gmail.com',
		subject='Your Meal Has Matched!',
		html_message=render_to_string('mealmatcher_app/match_email.html', {'name': user1, 'datetime': matched_meal.date, 'meal': meal, 'location': location, 'attire': matched_meal.attire1}),
		priority='now',
	)
	mail.send(
		[user2net + '@princeton.edu'],
		'princeton.meal.matcher@gmail.com',
		subject='Your Meal Has Matched!',
		html_message=render_to_string('mealmatcher_app/match_email.html', {'name': user2, 'datetime': matched_meal.date, 'meal': meal, 'location': location, 'attire': matched_meal.attire2}),
		priority='now',
	)

	if (datetime_obj.hour == 1):
		mail.send(
			[user1net + '@princeton.edu'],
			'princeton.meal.matcher@gmail.com',
			html_message=render_to_string('mealmatcher_app/warn_email.html', {'name': user1, 'datetime': datetime_obj, 'meal': meal, 'location': location, 'attire': matched_meal.attire1}),
			scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, 12),
		)
		mail.send(
			[user2net + '@princeton.edu'],
			'princeton.meal.matcher@gmail.com',
			html_message=render_to_string('mealmatcher_app/warn_email.html', {'name': user2, 'datetime': datetime_obj, 'meal': meal, 'location': location, 'attire': matched_meal.attire2}),
			scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, 12),
		)
	else:
		hour = datetime_obj.hour - 1
		mail.send(
			[user1net + '@princeton.edu'],
			'princeton.meal.matcher@gmail.com',
			subject='Your Meal Is Approaching!',
			html_message=render_to_string('mealmatcher_app/warn_email.html', {'name': user1, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire1}),
			scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, hour),
		)
		mail.send(
			[user2net + '@princeton.edu'],
			'princeton.meal.matcher@gmail.com',
			subject='Your Meal Is Approaching!',
			html_message=render_to_string('mealmatcher_app/warn_email.html', {'name': user2, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire2}),
			scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, hour),
		)


	print matched_meal.attire2
	matched_meal.users.add(my_user_profile)
	matched_meal.save()


# join_meal contains the majority of logic of joining a meal with the open meals interface
# redirects to my-meals if success, error page if there are errors
@login_required
def join_meal(request):
	if request.method == 'POST':
		form = JoinMealForm(request.POST)

		# validate the form data. TODO -- security checks by Kevin
		if form.is_valid():
			data = form.cleaned_data
			join_attire = data['newAttire'] # attire of the person signing up
			matchingMeals = Meal.objects.filter(id=data['idToJoin'])
					
			if len(matchingMeals) >= 1:
				mealToJoin = matchingMeals[0]

				# make sure that the User is not joining a meal_time for which the user already has a meal
				badTime = False
				same_time = list(Meal.objects.filter(meal_time=mealToJoin.meal_time, users__user=User.objects.filter(username=request.user.username)))
				for meal in same_time:
					if (meal.date.month == mealToJoin.date.month and meal.date.day == mealToJoin.date.day):
						badTime = True

				# cannot join this meal, rerender the page
				if badTime:
					form = MealForm()
					today = django_timezone.now()

					# grab the open meals to be displayed
					meals = list(Meal.objects.exclude(users__user=request.user).order_by('date'))
					mealsCopy = list(meals)
					for meal in mealsCopy:
						if meal.is_expired():
							meals.remove(meal)
					context_dict = {
						# for find meal form:
						'form':form, 'dateObj': today, 'date': {'month':today.month, 'day':today.day}, 'badTime': badTime, 'expiredTime': False, 
						# for open meals:
						'username':request.user.username, 'meals':meals, 'user_profile': UserProfile.objects.filter(user=request.user)[0],
						}
					return render(request, 'mealmatcher_app/findmeal.html', context_dict)

				# can join the meal, use match_meal to add user to the meal and send emails, and redirect to my-meals page
				else:
					my_user_profile = UserProfile.objects.filter(user=request.user)[0]
					match_meal(join_attire, my_user_profile, mealToJoin)
					return view_meals(request, new_meal=mealToJoin)

			else: # did not get a meal to join, redirect to error
				print 'join_meal error: no meal found with idToJoin'
				return error(request)

		else: # form is not valid, redirect to error 
			print 'join_meal error: '
			print form.errors
			return error(request)

	else: # not a GET, redirect to find-a-meal
		return HttpResponseRedirect('/find-a-meal/')

# error page view
@login_required
def error(request):
	return render(request, 'mealmatcher_app/error.html')


@login_required
def about(request):
	return render(request, 'mealmatcher_app/about.html')

# find-meals page, used to find meals and view/join open meals
# redirects to mymeals with the latest meal upon success
@login_required
def find_meals(request):
	username = request.user.username
	myUserProfiles = UserProfile.objects.filter(user=request.user)
	my_user_profile = myUserProfiles[0]

	badTime = False
	expiredTime = False
	if request.method == 'POST': 
		form = MealForm(request.POST)

		# validate form data, parse it for the appropriate information
		if form.is_valid():
			data = form.cleaned_data
			year = django_timezone.now().year
			location = data['location']
			meal_time = data['meal_time']
			attire1 = data['attire1'] # TODO - validate the attire1 security by Kevin
			date_md = data['date_mdy'].split('/')
			month = int(date_md[0])
			day = int(date_md[1])

			# parsing time information (hh:mm-hh:mm). only save the start time
			date_time = data['date_time'].split('-')[0].split(':')
			hour = int(date_time[0])
			# reformat hours for 24hour day 
			if meal_time == 'L' and hour <= 3:
				hour += 12
			elif meal_time == 'D':
				hour += 12
			elif meal_time == 'R' and hour <= 3:
				hour += 12
			minute = int(date_time[1])
			
			# set the timezone to Eastern 
			datetime_obj = datetime.datetime(year, month, day, hour, minute)
			datetime_obj = pytz.timezone(timezone.get_default_timezone_name()).localize(datetime_obj)

			# check for multiple meals at the same mealtime -- prevent signup 
			same_time = list(Meal.objects.filter(meal_time=meal_time, users__user=User.objects.filter(username=username)))
			for meal in same_time:
				if (meal.date.month == month and meal.date.day == day):
					badTime = True

			# check if meal is going to be at an expired time -- prevent signup
			check_exp = Meal(date = datetime_obj, location=location, meal_time=meal_time, attire1=attire1)
			if check_exp.is_expired():
				expiredTime = True

			# can join this meal 
			if not badTime and not expiredTime:
				possible_matches = Meal.objects.filter(date=datetime_obj, location=location, 
									meal_time=meal_time).exclude(users__user=User.objects.filter(username=username))
				filtered_matches = []

				# there are potential matches, remove already matched ones
				if possible_matches:                        
					for match in possible_matches:
						if not (match.is_matched()):  # this meal is not matched
							filtered_matches.append(match)
				possible_matches = filtered_matches

				# if there are still possible_matches, make the match, 				
				if possible_matches:
					matched_meal = random.choice(possible_matches) # perhaps never needed
					matched_meal.attire2 = attire1
					matched_meal.save()
					matched_meal.users.add(my_user_profile)
					matched_meal.save()
					new_meal = matched_meal

					# BELOW: all MAIL stuff in this if block section

					#mailer users
					user1 = matched_meal.users.all()[1].user.first_name
					user2 = matched_meal.users.all()[0].user.first_name		
					user2net = matched_meal.users.all()[0].user.username	

					meal = meal_time
					meal_location = location

					#mailer
					if (meal == "B"):
						meal = "Breakfast"
					elif (meal == "L"):
						meal = "Lunch"
					elif (meal == "D"):
						meal = "Dinner"
					else:
						meal = "Brunch"

					if (meal_location == "BW"):
						meal_location = "Butler"
					elif (meal_location == "WB"):
						meal_location = "Wilson"
					elif (meal_location == "RM"):
						meal_location = "Rocky"
					elif (meal_location == "MR"):
						meal_location = "Mathey"
					elif (meal_location == "WH"):
						meal_location = "Whitman"
					else:
						meal_location = "Forbes"

					#mailer view
					mail.send(
						[username + '@princeton.edu'],
						'princeton.meal.matcher@gmail.com',
						subject='Your Meal Has Matched!',
						html_message=render_to_string('mealmatcher_app/match_email.html', {'name': user1, 'datetime': datetime_obj, 'meal': meal, 'location': meal_location, 'attire': matched_meal.attire1}),
						priority='now',
					)
					mail.send(
						[user2net + '@princeton.edu'],
						'princeton.meal.matcher@gmail.com',
						subject='Your Meal Has Matched!',
						html_message=render_to_string('mealmatcher_app/match_email.html', {'name': user2, 'datetime': datetime_obj, 'meal': meal, 'location': meal_location, 'attire': matched_meal.attire2}),
						priority='now',
					)

					if (datetime_obj.hour == 1):
						mail.send(
							[username + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							html_message=render_to_string('mealmatcher_app/warn_email.html', {'name': user1, 'datetime': datetime_obj, 'meal': meal, 'location': meal_location, 'attire': matched_meal.attire1}),
							scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, 12),
						)
						mail.send(
							[user2net + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							html_message=render_to_string('mealmatcher_app/warn_email.html', {'name': user2, 'datetime': datetime_obj, 'meal': meal, 'location': meal_location, 'attire': matched_meal.attire2}),
							scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, 12),
						)
					else:
						send_hour = datetime_obj.hour - 1
						mail.send(
							[username + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							html_message=render_to_string('mealmatcher_app/warn_email.html', {'name': user1, 'datetime': datetime_obj, 'meal': meal, 'location': meal_location, 'attire': matched_meal.attire1}),
							scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, send_hour),
						)
						mail.send(
							[user2net + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							html_message=render_to_string('mealmatcher_app/warn_email.html', {'name': user2, 'datetime': datetime_obj, 'meal': meal, 'location': meal_location, 'attire': matched_meal.attire2}),
							scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, send_hour),
						)
					

				else: # no matches, make a new Meal and add it to the database
					new_meal = Meal(date = datetime_obj, location=location, meal_time=meal_time, attire1=attire1)
					new_meal.save()                     
					new_meal.users.add(my_user_profile)
					new_meal.save()

				 # HACK(drew) redirecting to my meals page after meal creation AND ALSO passing an extra arg
				return view_meals(request, new_meal=new_meal) 

			# error signing up meal at badTime or expiredTime -- render page, with errors
			else:
				today = django_timezone.now()
				# grab the open meals
				# meals = list(Meal.objects.exclude().order_by('date')) # allows own meals 
				meals = list(Meal.objects.exclude(users__user=request.user).order_by('date')) # prevents own meals
				mealsCopy = list(meals)
				for meal in mealsCopy:
					if meal.is_expired() or meal.is_matched():
						# print meal
						meals.remove(meal)

				context_dict = {
					# for find meal form:
					'form':form, 'dateObj': today, 'date': {'month':today.month, 'day':today.day}, 'badTime': badTime, 'expiredTime': expiredTime, 
					# for open meals:
					'username':request.user.username, 'meals':meals, 'user_profile': UserProfile.objects.filter(user=request.user)[0]
					}
				return render(request, 'mealmatcher_app/findmeal.html', context_dict)

		else: # form data not valid -- print errors, redirect to error
			print 'find-a-meal error: meal form was invalid ' 
			print form.errors
			today = django_timezone.now()
			# grab the open meals
			# meals = list(Meal.objects.exclude().order_by('date')) # allows own meals 
			meals = list(Meal.objects.exclude(users__user=request.user).order_by('date')) # prevents own meals
			mealsCopy = list(meals)
			for meal in mealsCopy:
				if meal.is_expired() or meal.is_matched():
					# print meal
					meals.remove(meal)

			context_dict = {
				# for find meal form:
				'form':form, 'dateObj': today, 'date': {'month':today.month, 'day':today.day}, 'badTime': badTime, 'expiredTime': expiredTime, 
				# for open meals:
				'username':request.user.username, 'meals':meals, 'user_profile': UserProfile.objects.filter(user=request.user)[0]
				}
			return render(request, 'mealmatcher_app/findmeal.html', context_dict)

	# not a GET, render the normal find-a-meal page
	else: 
		form = MealForm()
		today = django_timezone.now()
		# grab the open meals
		# meals = list(Meal.objects.exclude().order_by('date')) # allows own meals 
		meals = list(Meal.objects.exclude(users__user=request.user).order_by('date')) # prevents own meals
		mealsCopy = list(meals)
		for meal in mealsCopy:
			if meal.is_expired() or meal.is_matched():
				# print meal
				meals.remove(meal)

		context_dict = {
			# for find meal form:
			'form':form, 'dateObj': today, 'date': {'month':today.month, 'day':today.day}, 'badTime': badTime, 'expiredTime': expiredTime, 
			# for open meals:
			'username':request.user.username, 'meals':meals, 'user_profile': UserProfile.objects.filter(user=request.user)[0]
			}
		return render(request, 'mealmatcher_app/findmeal.html', context_dict)

# view-meals page -- redirects to itself, contains buttons for deleting and editing
@login_required
def view_meals(request, new_meal=None, deleted_meal=None): # HACK(drew) new_meal extra arg so we can highlight it when redirecting after form submission
	meals = list(Meal.objects.filter(users__user=request.user).order_by('date'))
	copy = list(meals)
	expired_meals = []
	removed_meals = []
	ongoing_meal = None
	ongoing_attire2 = None
	my_user_profile = UserProfile.objects.filter(user=request.user)[0]

	# generate list of meals 
	for meal in copy:
		if meal.to_be_removed():
			meals.remove(meal)
			meal.delete()
		elif meal.is_ongoing(): # or meal.is_matched(): #DEBUG: get an ongoing meal
			meals.remove(meal)
			ongoing_meal = meal
			if ongoing_meal.users.all()[0] == my_user_profile:   # user1, give attire2
				ongoing_attire2 = ongoing_meal.attire2
			elif ongoing_meal.users.all()[1] == my_user_profile: # user2, give attire1
				ongoing_attire2 = ongoing_meal.attire1
		elif meal.is_expired():
			meals.remove(meal)
			expired_meals.append(meal)
	my_user_profile = UserProfile.objects.filter(user=request.user)[0]

	# put new meals at the front of the list (disabled)
	# if new_meal and new_meal in meals:
	# 	meals.remove(new_meal)
	# 	meals.insert(0, new_meal)

	context_dict = {'username':request.user.username, 'meals':meals, 'new_meal':new_meal, 'deleted_meal':deleted_meal, 
					'user_profile': my_user_profile, 'expired_meals': expired_meals, 'removed_meals': removed_meals,
					'ongoing_meal': ongoing_meal, 'ongoing_attire2': ongoing_attire2,}
	return render(request, 'mealmatcher_app/mymeals.html', context_dict)

# unsupported now 
@login_required
def open_meals(request):
	# meals = list(Meal.objects.order_by('date'))
	meals = list(Meal.objects.exclude(users__user=request.user).order_by('date'))
	mealsCopy = list(meals)
	for meal in mealsCopy:
		if meal.is_expired():
			print meal
			meals.remove(meal)

	my_user_profile = UserProfile.objects.filter(user=request.user)[0]
	context_dict = {'username':request.user.username, 'meals':meals, 'user_profile': my_user_profile}
	return render(request, 'mealmatcher_app/openmeals.html', context_dict)

@login_required
def delete_meal(request):
	if request.method == 'POST': # http post, process the data
		form = DeleteMealForm(request.POST)

		# validate data
		if form.is_valid():
			data = form.cleaned_data
			matchingMeals = Meal.objects.filter(id=data['idToDelete'])

			if len(matchingMeals) >= 1:
				mealToDelete = matchingMeals[0]

				# expired meals, can be removed from DB 
				if mealToDelete.is_expired():
					# if it is expired and unmatched, remove from DB
					if not mealToDelete.is_matched(): 
						mealToDelete.delete()
						return view_meals(request, deleted_meal=mealToDelete)
					# otherwise shift user and attire, 
					else:
						myProfile = UserProfile.objects.filter(user=request.user)[0]
						if mealToDelete.users.all()[0] == myProfile: #user 1 
							mealToDelete.attire1 = mealToDelete.attire2
							mealToDelete.attire2 = ""
							mealToDelete.save()

						else: # user2
							mealToDelete.attire2 = ""
							mealToDelete.save()

						mealToDelete.users.remove(myProfile)
						mealToDelete.save()
						return view_meals(request, deleted_meal=mealToDelete)

				# not expired, and unmatched, delete the open meal search
				elif not mealToDelete.is_matched():
					mealToDelete.delete()

				# TODO(drew) only allow dropping out if meal isn't too soon
				else:
					myProfile = UserProfile.objects.filter(user=request.user)[0]
					status = True
					user1 = mealToDelete.users.all()[0].user.first_name
					user1net = mealToDelete.users.all()[0].user.username

					send_meal = mealToDelete.meal_time
					send_location = mealToDelete.location

					#mailer
					if (send_meal == "B"):
						send_meal = "Breakfast"
					elif (send_meal == "L"):
						send_meal = "Lunch"
					elif (send_meal == "D"):
						send_meal = "Dinner"
					else:
						send_meal = "Brunch"

					if (send_location == "BW"):
						send_location = "Butler"
					elif (send_location == "WB"):
						send_location = "Wilson"
					elif (send_location == "RM"):
						send_location = "Rocky"
					elif (send_location == "MR"):
						send_location = "Mathey"
					elif (send_location == "WH"):
						send_location = "Whitman"
					else:
						send_location = "Forbes"

					# make sure the remaining user is shifted to user1, i.e. shift the attire
					if mealToDelete.users.all()[0] == myProfile:
						#mailer
						user2 = mealToDelete.users.all()[1].user.first_name
						user2net = mealToDelete.users.all()[1].user.username

						mealToDelete.attire1 = mealToDelete.attire2

						#mailer
						mail.send(
							[user2net + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							subject='You\'ve been returned to the Match Pool',
							html_message=render_to_string('mealmatcher_app/delete_email.html', {'name': user2, 'datetime': mealToDelete.date, 'meal': send_meal, 'location': send_location}),
							priority='now',
						)
						status = False
					#mailer
					if status:
						mail.send(
							[user1net + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							subject='You\'ve been returned to the Match Pool',
							html_message=render_to_string('mealmatcher_app/delete_email.html', {'name': user1, 'datetime': mealToDelete.date, 'meal': send_meal, 'location': send_location}),
							priority='now',
						)

					mealToDelete.attire2 = ""
					mealToDelete.users.remove(myProfile)
					mealToDelete.save()
				return view_meals(request, deleted_meal=mealToDelete)

			else: # did not get a meal to delete, redirect to error
				print 'delete_meal error: no meal found with idToDelete'
				# return error(request)
				# you get here by refreshing after deleting a meal
				return view_meals(request)

		else: # errors with form -- redirect to error page
			print 'delete_meal error: delete meal form was invalid '
			print form.errors
			return error(request)

	# received a GET, redirect to my-meals 
	else: 
		return HttpResponseRedirect('/my-meals/')

# login page
def site_login(request):
	#base_url = request.build_absolute_uri()
	base_url = 'http://' + request.META['HTTP_HOST']
	print base_url
	# user is logged in, redirect to index page
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')
	# user is not logged in. go through CAS stuff
	else: 
		ticket = request.GET.get('ticket')
		if not ticket:
			return HttpResponseRedirect('https://fed.princeton.edu/cas/login?service=' + base_url + '/login/')
		else:
			source = urllib2.urlopen('https://fed.princeton.edu/cas/serviceValidate?service=' + base_url + '/login/&ticket=' + ticket)
			content = source.read()
			if 'authenticationSuccess' in content:      # success in authentication
				regexp = re.search('<cas:user>.*</cas:user>', content)
				netid = regexp.group(0)[10:-11]
				if User.objects.filter(username=netid): # in the database. Log them in
					username = netid
					password = netid
					user = authenticate(username=username, password=password)
					if user: 
						user_profile = UserProfile.objects.filter(user=user)
						if not user_profile:
							profile = UserProfile(user=user)
							print 'made the profile'
						django_login(request, user)
						return HttpResponseRedirect('')
					else:
						return HttpResponse('Fatal error trying to log in '+ netid)
				else:
					username = netid
					password = netid
					name_source = urllib2.urlopen('http://www.princeton.edu/main/tools/search/?q=' + netid)
					name_content = name_source.read()
					regexp_name = re.search('id=\"people-row-link-3\">\n.*\n      </a>', name_content)
					last_name = regexp_name.group(0).split(',')[0][30:]
					first_name = regexp_name.group(0).split(',')[1][1:-11]
					if '.' in first_name: # has a middle inital
						first_name = first_name[:-3]
					newuser = User(username=username, password=password, email= (netid + '@princeton.edu'), 
									first_name=first_name, last_name=last_name)
					newuser.save()
					newuser.set_password(newuser.password)
					newuser.save()
					profile = UserProfile(user = newuser)
					profile.save()
					newuser = authenticate(username=username, password=password)
					django_login(request, newuser)
					print first_name + ' @@ ' + last_name
					return HttpResponseRedirect('')
			else: # redirect to try again
				return HttpResponseRedirect('https://fed.princeton.edu/cas/login?service=' + base_url + '/login/')



@login_required
def site_logout(request):
	logout(request) # Log user out of our system
	return HttpResponseRedirect('https://fed.princeton.edu/cas/logout') # Log user out of CAS system

