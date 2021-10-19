from django.dispatch import receiver
import django.dispatch
from .models import Reservation, Log

# Custom signals for Reservations app
reserve_event = django.dispatch.Signal(providing_args=['event', 'instance', 'created'])

@receiver(reserve_event, sender=Reservation)
def create_log(sender, **kwargs):
    """
    Creates a log entry for reservations that have been approve,
    decline, create, edit/save, delete, checkin or checkout.
    """
    log = None
    reservation = kwargs.get('instance', None)
    created = kwargs.get('created', False) # Check for new reservations
    event = kwargs.get('event', None)
    
    if event in [Log.LOG_EVENT_DELETED, Log.LOG_EVENT_DECLINED]:        
        log = Log(log_event=event, reservation=None)
        log.message = 'Reservation belonging to %s - "%s" was <strong>%s</strong>' % (reservation.user.full_name, reservation.project,
                                                                                     str(log.get_log_event_display()).lower())
    else:
        log = Log(log_event=event, reservation=reservation)
        log.message = 'Reservation <a href="%s">#%d</a> was <strong>%s</strong> for %s - "%s"' % (reservation.get_absolute_url(), reservation.id,
                                                                                  str(log.get_log_event_display()).lower(), reservation.user.full_name,
                                                                                  reservation.project)
    
    log.save()