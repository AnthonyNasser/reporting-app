from django.db import models
from django.forms import ModelForm
from django.utils.text import slugify
from api_wellness.models import Event

def qr_directory_path(instance, filename):
	return 'events/{0}-{1}'.format(slugify(instance.name), filename)

class Event_QR(Event):
    qr			= models.ImageField('QR Code', upload_to=qr_directory_path, null=True, blank=True)

class EventForm(ModelForm):
    class Meta:
        model = Event_QR
        fields = ['name', 'description', 'points', 'promote', 'active', 'location', 'poster', 'start', 'end', 'qr']
        localized_fields = ('start', 'end')