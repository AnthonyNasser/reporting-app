"""asicsulb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

urlpatterns = [
    url(r'^reservations/', include('reservations.urls', namespace='reservations')),
    url(r'^workorders/', include('workorders.urls', namespace='workorders')),
    url(r'^wellness/', include('wellness.urls', namespace='wellness')),
    url(r'^reporting/', include('reporting.urls', namespace='reporting')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api_wellness.urls', namespace='api')),
	url(r'^login/$', auth_views.login, {'template_name': 'reservations/base_login.html'}, name='login'),
	url(r'^logout/$', auth_views.logout, name='logout'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)