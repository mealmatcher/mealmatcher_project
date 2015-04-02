from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from mealmatcher_app.models import UserProfile, Meal
import urllib2, re

# index is the app homepage
@login_required
def index(request):
	context_dict = {'user': request.user}
	return render(request, 'mealmatcher_app/index.html', context_dict)

# find-meals page
@login_required
def find_meals(request):
	return HttpResponse("Find meals")

# view-meals page
@login_required
def view_meals(request):
	return HttpResponse("View meals")

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
					django_login(request, newuser)
					return HttpResponseRedirect('/mealmatcher_app/')
			else: # redirect to try again
				#return HttpResponse('failure')
				return HttpResponseRedirect('https://fed.princeton.edu/cas/login?service=http://localhost:8000/mealmatcher_app/login/')

@login_required
def site_logout(request):
	return HttpResponse('logout')
