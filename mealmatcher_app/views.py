from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as django_login
from mealmatcher_app.models import UserProfile, Meal
from mealmatcher_app.forms import MealForm
import datetime, random
from django.utils import timezone
import urllib2, re

# index is the app homepage
@login_required
def index(request):
	context_dict = {'user': request.user}
	return render(request, 'mealmatcher_app/index.html', context_dict)

# find-meals page
'''
@login_required
def find_meals(request):
	context_dict = {
		'date': {'month': "4", 'day': "10"},
	}
	return render(request, 'mealmatcher_app/findmeal.html', context_dict)
	# return HttpResponse("Find meals")
'''

@login_required
def find_meals(request):
	username = request.user.username
	my_user_profile = UserProfile.objects.filter(user=request.user)[0]
	if request.method == 'POST': # http post, process the data
		print 'received a post'
		form = MealForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			year = 2015
			date_md = data['date_mdy'].split('/')
			print date_md[0]
			month = int(date_md[0])
			day = int(date_md[1])

			date_time = data['date_time'].split('-')[0].split(':')
			hour = int(date_time[0])
			minute = int(date_time[1])

			datetime_obj = datetime.datetime(year, month, day, hour, minute)

			location = data['location']
			meal_time = data['meal_time']
			attire1 = data['attire1']

			possible_matches = Meal.objects.filter(date=datetime_obj, location=location, meal_time=meal_time).exclude(users__user=User.objects.filter(username=username))
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
				matched_meal.users.add(my_user_profile)
				#return HttpResponse('Made a match!')
			else: # no matches, make a new Meal and add it to the database
				new_meal = Meal(date = datetime_obj, location=location, meal_time=meal_time, attire1=attire1)
				new_meal.save()                        # bug somewhere here
				new_meal.users.add(my_user_profile)
				new_meal.save()
				#return HttpResponse('Made a new meal!')
		else:
			print form.errors
	else:
		print 'received a GET'
		form = MealForm()
		confirmed = False
	today = timezone.now()
	context_dict = {'form':form, 'date': {'month':today.month, 'day':today.day}}
	return render(request, 'mealmatcher_app/findmeal.html', context_dict)
		# return HttpResponse("Find meals")

# view-meals page
@login_required
def view_meals(request):
	meals = Meal.objects.filter(users__user=request.user)
	context_dict = {'username':request.user.username, 'meals':meals}
	return render(request, 'mealmatcher_app/mymeals.html', context_dict)
	# return HttpResponse("View meals")

# login page
def site_login(request):
	# user is logged in, redirect to index page
	if request.user.is_authenticated():
		return HttpResponseRedirect('/mealmatcher_app/')
	# user is not logged in. go through CAS stuff
	else: 
		ticket = request.GET.get('ticket')
		if not ticket:
			return HttpResponseRedirect('https://fed.princeton.edu/cas/login?service=http://localhost:8000/mealmatcher_app/login/')
		else:
			source = urllib2.urlopen('https://fed.princeton.edu/cas/serviceValidate?service=http://localhost:8000/mealmatcher_app/login/&ticket=' + ticket)
			content = source.read()
			if 'authenticationSuccess' in content:      # success in authentication
				regexp = re.search('<cas:user>.*</cas:user>', content)
				netid = regexp.group(0)[10:-11]
				if User.objects.filter(username=netid): # in the database. Log them in
					username = netid
					password = netid
					user = authenticate(username=username, password=password)
					if user: 
						django_login(request, user)
						return HttpResponseRedirect('/mealmatcher_app/')
					else:
						return HttpResponse('Fatal error trying to log in '+ netid)
				else:
					username = netid
					password = netid
					newuser = User(username=username, password=password, email= (netid + '@princeton.edu'))
					newuser.save()
					newuser.set_password(newuser.password)
					newuser.save()
					profile = UserProfile(user = newuser)
					profile.save()
					newuser = authenticate(username=username, password=password)
					django_login(request, newuser)
					return HttpResponseRedirect('/mealmatcher_app/')
			else: # redirect to try again
				#return HttpResponse('failure')
				return HttpResponseRedirect('https://fed.princeton.edu/cas/login?service=http://localhost:8000/mealmatcher_app/login/')

@login_required
def site_logout(request):
	logout(request) # Log user out of our system
	return HttpResponseRedirect('https://fed.princeton.edu/cas/logout') # Log user out of CAS system

