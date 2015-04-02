from django.shortcuts import render
from django.http import HttpResponse

# index is the app homepage
def index(request):
	return HttpResponse("Homepage")

def find_meals(request):
	return HttpResponse("Find meals")

def view_meals(request):
	return HttpResponse("View meals")