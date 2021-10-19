from django.conf.urls import url
from reporting.views import (ReportCreate, ReportListView, CommitteeCreate,
							CommitteeUpdate, CommitteeDelete, RepresentativeCreate,
							RepresentativeUpdate, RepresentativeDelete, MeetingCreate,
							MeetingUpdate, MeetingDelete, DashboardView, ReportDetailView,
							ReportDeleteView)

# the 'name' value as called by the {% url %} template tag
urlpatterns = [
	# Dashboard
	url(r'^$', DashboardView.as_view(), name='dashboard'),

	# Committee routes
	url(r'committee/add/$', CommitteeCreate.as_view(), name='committee-add'),
	url(r'committee/(?P<pk>[0-9]+)/$', CommitteeUpdate.as_view(), name='committee-update'),
	url(r'committee/(?P<pk>[0-9]+)/delete/$', CommitteeDelete.as_view(), name='committee-delete'),

	# Representative routes
	url(r'representative/add/$', RepresentativeCreate.as_view(), name='representative-add'),
	url(r'representative/(?P<pk>[0-9]+)/$', RepresentativeUpdate.as_view(), name='representative-update'),
	url(r'representative/(?P<pk>[0-9]+)/delete/$', RepresentativeDelete.as_view(), name='representative-delete'),

	# Meeting routes
	url(r'meeting/add/$', MeetingCreate.as_view(), name='meeting-add'),
	url(r'meeting/(?P<pk>[0-9]+)/$', MeetingUpdate.as_view(), name='meeting-update'),
	url(r'meeting/(?P<pk>[0-9]+)/delete/$', MeetingDelete.as_view(), name='meeting-delete'),

	# Reports routes
	url(r'reports/$', ReportListView.as_view(), name='report-list'),
	url(r'reports/(?P<pk>[0-9]+)/$', ReportDetailView.as_view(), name='report-detail'),
	url(r'reports/add/$', ReportCreate.as_view(), name='report-add'),
	url(r'reports/(?P<pk>[0-9]+)/delete/$', ReportDeleteView.as_view(), name='report-delete'),
]