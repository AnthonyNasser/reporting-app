import json
from io import BytesIO

import qrcode
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from api_wellness.models import Event
from api_wellness.signals import cache_event_change
from wellness.models import Event_QR, EventForm


@login_required
def index(request):

    events = Event_QR.objects.order_by('-start')
    context = { 'events': events }
    return render(request, 'wellness/base_home.html', context)

@login_required
def events(request, id=None):
    event = None
    form = None

    if request.method == 'POST' and request.POST.get('save'):
        form, event = save_event(request, id)
        # Check if event was saved successfully
        if event is not None:
            # Redirect to calendar view
            return HttpResponseRedirect(reverse('wellness:index'))
    
    # Request for existing event
    if id is not None:
        event = get_object_or_404(Event, pk=id)
    
    context = {
        'event': event,
        'form': form
    }
    return render(request, 'wellness/base_events.html', context)            
            

########################################################################
#                                                                      #
############################  Functions  ###############################
#                                                                      #
########################################################################

def save_event(request, id=None): 
    instance = None

    if id is not None: 
        instance = get_object_or_404(Event_QR, pk=id)

    form = EventForm(request.POST, request.FILES, instance=instance)

    if form.is_valid():
        # Save to database
        event = form.save()
        # Manually invalidate the event cache
        cache_event_change(sender=Event)

        # Delete qrcode if updating existing event
        if instance:
            event.qr.delete()

        # Create qrcode image
        qr = qrcode.make(json.dumps({
            'event_id': event.id,
            'name': event.name,
            'points': event.points})
        )

        # Create file stream
        file = BytesIO()
        
        try:
            # Save qr image to file stream
            qr.save(file, format='PNG')
            # Save qr image
            event.qr.save('qrcode.png', ContentFile(file.getvalue()))
        except IOError as err:
            print('IO error: {0}'.format(err))
        finally:        
            file.close()

        return form, event
    
    return form, None
