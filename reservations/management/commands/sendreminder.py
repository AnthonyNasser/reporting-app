from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail
from django.utils import timezone
from reservations.models import Reservation

class Command(BaseCommand):
    help = 'Sends email reminders to producers who have reservations for today'

    def handle(self, *args, **options):
        messages = []
        # Get all reservations for today
        today = timezone.localtime(timezone.now())

        # Note: When using the field lookup below (date) and USE_TZ is True, fields are converted to the current time zone before filtering.
        reservations = Reservation.objects.filter(start_date__date=today.date(), state__gte=Reservation.STATE_APPROVED).select_related('user')

        # Loop thru today's reservations and create a message for each one
        for r in reservations:
            message = ('Equipment Reservation Reminder', Reservation.EMAIL_STAFF_REMINDER % (r.user,
                timezone.localtime(r.start_date).strftime("%I:%M %p"), r.id), 'noreply@asicsulb.org', [r.user.email])
            messages.append(message)

        # Email all messages
        if messages:
            send_mass_mail(tuple(messages))
            self.stdout.write(self.style.SUCCESS('Successfully sent %d email(s)' % len(messages)))