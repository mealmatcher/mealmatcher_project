from django.conf.urls import patterns, url
from mealmatcher_app import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^view-meals/', views.view_meals, name='view-meals'),
	url(r'^find-meals/', views.find_meals, name='find-meals'),
	url(r'^login/', views.site_login, name='login'),
	#url(r'^login/$', views.login, name='login'),
	)
