from django.conf.urls import url


from . import views

# the 'name' value as called by the {% url %} template tag
urlpatterns = [
	# Home page: shows instructions page
	# ex: /reservations/
	url(r'^$', views.index, name='index'),

	# Test route for reservation packages (Not production ready)
	url(r'^most-popular$', views.most_popular, name='most-popular'),

	# URL to monthly calendar view
	# ex: /reservations/calendar
	url(r'^calendar/$', views.calendar, name='calendar'),

	# Take user to reservation form with preloaded date field after clicking a day cell on the calendar
	# ex: /reservations/reserve/YYYY-MM-DD/
	url(r'^reserve/(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$', views.reserve, name='reserve-with-date'),

	# Take user to reservation form with pre-populated reservation after clicking an event on the calendar
	# ex: /reservations/reserve/id
	url(r'^reserve/(?P<id>[0-9]+)/$', views.reserve, name='reserve-edit'),

	# URL to POST reservations or show reservation form
	# ex: /reservations/reserve
	url(r'^reserve/$', views.reserve, name='reserve'),

	# URL to approve a reservation
	# ex: /reservations/approve/id
	url(r'^approve/(?P<id>[0-9]+)/$', views.approve, name='approve'),
	
	# Retrieve monthly/weekly/daily feed for calendar views
	# ex: /reservations/feed?start=YYYY-MM-DD&end=YYYY-MM-DD
	url(r'^feed$',views.get_reservations_for_month, name='monthly-reservations'),

	# Edit inventory item after selecting the edit action on a item
	# ex: /reservations/inventory/id
	url(r'^inventory/(?P<id>[0-9]+)/$', views.inventory, name='inventory-edit'),
	
	# Take user to inventory list page after selecting the inventory menu item
	# ex: /reservations/inventory/
	url(r'^inventory/$', views.inventory, name='inventory'),

	# Take user to activity log page after selecting the activity log menu item
	# ex: /reservations/activity-log/
	url(r'^activity-log/$', views.activity_log, name='activity-log'),
]