from django.conf.urls import url


from . import views

# the 'name' value as called by the {% url %} template tag
urlpatterns = [
	# Home page
	# ex: /workorders/
	url(r'^$', views.index, name='index'),

	# New Workorder Form
	# ex: /new/
	url(r'^new/$', views.new, name='new'),
]