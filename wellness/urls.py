from django.conf.urls import url


from . import views

# the 'name' value as called by the {% url %} template tag
urlpatterns = [
	# Home page: shows Home page
	# ex: /wellness/
	url(r'^$', views.index, name='index'),
	url(r'^events/$', views.events, name='events'),
	url(r'^events/(?P<id>[0-9]+)/$', views.events, name='events'),
]