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
	base_url = request.build_absolute_uri()
	print base_url
	first_name = request.user.first_name

	context_dict = {'user': request.user, 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'username': request.user.username}
	return render(request, 'mealmatcher_app/index_new.html', context_dict)

@login_required
def edit_attire(request): #TODO: add email support
	if request.method == "POST":
		print "received an edit post method"
		form = EditAttireForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			newAttire = data['newAttire']
			if len(newAttire) > 100: newAttire = newAttire[0:100]
			print('meal id being edited ' + data['idToEdit'])
			matchingMeals = Meal.objects.filter(id=data['idToEdit'])
			if len(matchingMeals) >= 1:
				mealToEdit = matchingMeals[0]
				my_user_profile = UserProfile.objects.filter(user=request.user)[0]
				if mealToEdit.users.all()[0] == my_user_profile: # the one being edited is user 1
					mealToEdit.attire1 = newAttire
					mealToEdit.save()
				else: # change user2
					mealToEdit.attire2 = newAttire
					mealToEdit.save()
				return HttpResponseRedirect('/my-meals/')
		else:
			print form.errors
		#return view_meals(request)
	return HttpResponseRedirect('/my-meals/')

def match_meal(attire1, my_user_profile, matched_meal):
	matched_meal.attire2 = attire1
	matched_meal.save()
	#mailer user
	matchedUsers = matched_meal.users.all()
	# TODO error if not found
	# if len(matchedUsers) > 0:
	user2 = matchedUsers[0].user.username

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

	matched_meal.users.add(my_user_profile)

	#mailer
	'''if not EmailTemplate.objects.all():
		EmailTemplate.objects.create(
			name='match_email',
			subject='Good Day from MealMatcher!',
			content='MEAL INCOMING, {{ name }}!',
			html_content=get_template('templates_path/match_email.html'),
			#'MEAL INCOMING, {{ name }}! DATE - {{ datetime }} MEAL - {{ meal }} LOCATION - {{ location }} YOUR GUEST ATTIRE - {{ attire }}',
		)
		EmailTemplate.objects.create(
			name='warn_email',
			subject='Good Day from MealMatcher!',
			content='Meal incoming, {{ name }}!',
			html_content=get_template('templates_path/warn_email.html'),
			#html_content='Meal incoming, {{ name }}! Your {{ meal }} on {{ datetime }} at {{ location }} has been unmatched, but we put you back in the pool for other matches!',
		)
		EmailTemplate.objects.create(
			name='delete_email',
			subject='Good Day from MealMatcher!',
			content='MEAL INCOMING, {{ name }}!',
			html_content=get_template('templates_path/match_email.html'),
			#'MEAL INCOMING, {{ name }}! Your {{ meal }} on {{ datetime }} at {{ location }} has been unmatched, but we put you back in the pool for other matches!',
		)


	# #html_content=render_to_string('match_email_html.html'),

	#mailer view
	mail.send(
		['<' + username + '@princeton.edu' + '>'],
		'princeton.meal.matcher@gmail.com',
		template='match_email',
		context={'name': username, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire1},
		priority='now',
	)
	mail.send(
		[user2 + '@princeton.edu'],
		'princeton.meal.matcher@gmail.com',
		template='match_email',
		context={'name': user2, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire2},
		priority='now',
	)

	if (datetime_obj.hour == 1):
		mail.send(
			[username + '@princeton.edu'],
			'princeton.meal.matcher@gmail.com',
			template='warn_email',
			context={'name': username, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire1},
			scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, 12),
		)
		mail.send(
			[user2 + '@princeton.edu'],
			'princeton.meal.matcher@gmail.com',
			template='warn_email',
			context={'name': user2, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire2},
			scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, 12),
		)
	else:
		mail.send(
			[username + '@princeton.edu'],
			'princeton.meal.matcher@gmail.com',
			template='warn_email',
			context={'name': username, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire1},
			scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, (datetime_obj.hour - 1)),
		)
		mail.send(
			[user2 + '@princeton.edu'],
			'princeton.meal.matcher@gmail.com',
			template='warn_email',
			context={'name': user2, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire2},
			scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, (datetime_obj.hour - 1)),
		)'''

	print matched_meal.attire2
	matched_meal.users.add(my_user_profile)
	matched_meal.save()

@login_required
def join_meal(request):
	if request.method == 'POST': # http post, process the data
		print 'received a join meal post'
		form = JoinMealForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			join_attire = data['newAttire'] # attire of the person signing up
			print('attempting to join ' + data['idToJoin'])
			matchingMeals = Meal.objects.filter(id=data['idToJoin'])
			if len(matchingMeals) >= 1:
				mealToJoin = matchingMeals[0]
				my_user_profile = UserProfile.objects.filter(user=request.user)[0]
				match_meal(join_attire, my_user_profile, mealToJoin)
				return view_meals(request, new_meal=mealToJoin)
				# return view_meals(request)
		else:
			print form.errors
		#return view_meals(request)
	return HttpResponseRedirect('/my-meals/')

# find-meals page
@login_required
def find_meals(request):
	username = request.user.username
	my_user_profile = UserProfile.objects.filter(user=request.user)[0]
	badTime = False
	expiredTime = False
	if request.method == 'POST': # http post, process the data
		form = MealForm(request.POST)

		if form.is_valid():
			data = form.cleaned_data
			year = 2015
			location = data['location']
			meal_time = data['meal_time']
			attire1 = data['attire1']
			date_md = data['date_mdy'].split('/')
			print date_md[0]
			month = int(date_md[0])
			day = int(date_md[1])

			date_time = data['date_time'].split('-')[0].split(':')
			hour = int(date_time[0])
			if meal_time == 'L' and hour <= 3:
				hour += 12
			elif meal_time == 'D':
				hour += 12
			elif meal_time == 'R' and hour <= 3:
				hour += 12
			# hack for timezone to avoid confusion of objects -- DANGER
			#hour = int(date_time[0]) - 4 
			#if hour < 0: hour = hour + 12
			minute = int(date_time[1])
			
			datetime_obj = datetime.datetime(year, month, day, hour, minute)
			print timezone.get_default_timezone_name()
			datetime_obj = pytz.timezone(timezone.get_default_timezone_name()).localize(datetime_obj)
			#eastern = pytz.timezone('US/Eastern') # attempt at timezones, did not work
			#fmt = '%Y-%m-%d %H:%M %Z%z'
			#datetime_obj = eastern.localize(datetime_obj)
			#print datetime_obj.strftime(fmt)
			

			# check for multiple meals at the same mealtime -- prevent signup 
			same_time = list(Meal.objects.filter(meal_time=meal_time, users__user=User.objects.filter(username=username)))
			for meal in same_time:
				if (meal.date.month == month and meal.date.day == day):
					print 'Attempted signup at a time that already has a meal the user is in.'
					badTime = True

			# check if meal is going to be at an expired time -- prevent signup
			check_exp = Meal(date = datetime_obj, location=location, meal_time=meal_time, attire1=attire1)
			if check_exp.is_expired():
				print 'Attempted signup at an expired time.'
				expiredTime = True


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
					matched_meal = random.choice(possible_matches)
					matched_meal.attire2 = attire1

					#mailer user
					user2 = matched_meal.users.all()[0].user.username

					matched_meal.users.add(my_user_profile)
					new_meal = None

					#mailer
					if not EmailTemplate.objects.all():
						EmailTemplate.objects.create(
							name='match_email',
							subject='Good Day from MealMatcher!',
							html_content=get_template('templates_path/match_email.html'),
							#'MEAL INCOMING, {{ name }}! DATE - {{ datetime }} MEAL - {{ meal }} LOCATION - {{ location }} YOUR GUEST ATTIRE - {{ attire }}',
						)
						EmailTemplate.objects.create(
							name='warn_email',
							subject='Good Day from MealMatcher!',
							html_content=get_template('templates_path/warn_email.html'),
							#html_content='Meal incoming, {{ name }}! Your {{ meal }} on {{ datetime }} at {{ location }} has been unmatched, but we put you back in the pool for other matches!',
						)
						EmailTemplate.objects.create(
							name='delete_email',
							subject='Good Day from MealMatcher!',
							html_content=get_template('templates_path/match_email.html'),
							#'MEAL INCOMING, {{ name }}! Your {{ meal }} on {{ datetime }} at {{ location }} has been unmatched, but we put you back in the pool for other matches!',
						)


					#html_content=render_to_string('match_email_html.html'),

					#mailer view
					mail.send(
						[username + '@princeton.edu'],
						'princeton.meal.matcher@gmail.com',
						template='match_email',
						context={'name': username, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire1},
						priority='now',
					)
					mail.send(
						[user2 + '@princeton.edu'],
						'princeton.meal.matcher@gmail.com',
						template='match_email',
						context={'name': user2, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire2},
						priority='now',
					)

					if (datetime_obj.hour == 1):
						mail.send(
							[username + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							template='warn_email',
							context={'name': username, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire1},
							scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, 12),
						)
						mail.send(
							[user2 + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							template='warn_email',
							context={'name': user2, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire2},
							scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, 12),
						)
					else:
						hour = datetime_obj.hour - 1
						mail.send(
							[username + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							template='warn_email',
							context={'name': username, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire1},
							scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, hour),
						)
						mail.send(
							[user2 + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							template='warn_email',
							context={'name': user2, 'datetime': datetime_obj, 'meal': meal_time, 'location': location, 'attire': matched_meal.attire2},
							scheduled_time=datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day, hour),
						)


					print matched_meal.attire2
					matched_meal.users.add(my_user_profile)
					new_meal = matched_meal
					new_meal.save()

					match_meal(attire1, my_user_profile, matched_meal)

					#return HttpResponse('Made a match!')
				else: # no matches, make a new Meal and add it to the database
					new_meal = Meal(date = datetime_obj, location=location, meal_time=meal_time, attire1=attire1)
					new_meal.save()                     
					new_meal.users.add(my_user_profile)
					new_meal.save()
					#return HttpResponse('Made a new meal!')

				return view_meals(request, new_meal=new_meal)  # HACK(drew) redirecting to my meals page after meal creation AND ALSO passing an extra arg
		else: # for debugging only
			print form.errors
	else:
		form = MealForm()
	today = django_timezone.now()
	context_dict = {'form':form, 'dateObj': today, 'date': {'month':today.month, 'day':today.day}, 'badTime': badTime, 'expiredTime': expiredTime}
	return render(request, 'mealmatcher_app/findmeal.html', context_dict)
		# return HttpResponse("Find meals")

# view-meals page

@login_required
def view_meals(request, new_meal=None, deleted_meal=None): # HACK(drew) new_meal extra arg so we can highlight it when redirecting after form submission
	meals = list(Meal.objects.filter(users__user=request.user).order_by('date'))
	copy = list(meals)
	expired_meals = []
	removed_meals = []
	for meal in copy:
		#if meal.to_be_removed():
		#	meals.remove(meal)
		#	removed_meals.append(meal)
		if meal.is_expired():
			#print meal
			meals.remove(meal)
			expired_meals.append(meal)
	my_user_profile = UserProfile.objects.filter(user=request.user)[0]
	if new_meal and new_meal in meals:
		meals.remove(new_meal)
		meals.insert(0, new_meal)
	context_dict = {'username':request.user.username, 'meals':meals, 'new_meal':new_meal, 'deleted_meal':deleted_meal, 
					'user_profile': my_user_profile, 'expired_meals': expired_meals, 'removed_meals': removed_meals,
					}
	return render(request, 'mealmatcher_app/mymeals.html', context_dict)
	# return HttpResponse("View meals")

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
		print 'received a delete meal post'
		form = DeleteMealForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			print(data['idToDelete'])
			matchingMeals = Meal.objects.filter(id=data['idToDelete'])
			if len(matchingMeals) >= 1:
				mealToDelete = matchingMeals[0]

				if mealToDelete.is_expired():
					if not mealToDelete.is_matched():
						mealToDelete.delete()
						return view_meals(request, deleted_meal=mealToDelete)
					else:
						myProfile = UserProfile.objects.filter(user=request.user)[0]
						if mealToDelete.users.all()[0] == myProfile: #user 1 
							mealToDelete.attire1 = mealToDelete.attire2
							mealToDelete.attire2 = ""
							mealToDelete.save()
						mealToDelete.users.remove(myProfile)
						return view_meals(request, deleted_meal=mealToDelete)

				elif not mealToDelete.is_matched():
					mealToDelete.delete()
				# TODO(drew) only allow dropping out if meal isn't too soon
				else:
					myProfile = UserProfile.objects.filter(user=request.user)[0]
					status = True
					user1 = mealToDelete.users.all()[0].user.username

					# make sure the remaining user is shifted to user1, i.e. shift the attire
					if mealToDelete.users.all()[0] == myProfile:
						#mailer
						user2 = mealToDelete.users.all()[1].user.username

						mealToDelete.attire1 = mealToDelete.attire2
						
						#mailer
						mail.send(
							[user2 + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							template='delete_email',
							context={'name': user2, 'datetime': mealToDelete.date, 'meal': mealToDelete.meal_time, 'location': mealToDelete.location},
							priority='now',
						)
						status = False
					#mailer
					if status:
						mail.send(
							[user1 + '@princeton.edu'],
							'princeton.meal.matcher@gmail.com',
							template='delete_email',
							context={'name': user1, 'datetime': mealToDelete.date, 'meal': mealToDelete.meal_time, 'location': mealToDelete.location},
							priority='now',
						)

					mealToDelete.attire2 = ""
					mealToDelete.users.remove(myProfile)
					mealToDelete.save()
				return view_meals(request, deleted_meal=mealToDelete)
		else:# errors with form -- redirect to error page?
			print form.errors
		return HttpResponseRedirect('/my-meals/')
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
					newuser = User(username=username, password=password, email= (netid + '@princeton.edu'))
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

