import pytz
from datetime import timedelta

from django.core.mail import send_mass_mail
from django.core.management.base import BaseCommand
from django.db.models import Prefetch
from django.utils import timezone

from reporting.models import Committee, Representative

class Command(BaseCommand):
    help = 'Sends email to representatives that have not submitted reports after 6 and 9 days after meeting'
    
    def handle(self, *args, **options):
        messages = []

        text_email = ('Dear {},\n\nThis email is a reminder that you have missing report(s) that are {} days past due for the following committee meeting(s):\n\n{}\n\n'
					'Reports are due 6 days after the meeting. Please make your submission at https://asicsulb.org/apps/reporting/reports/add/.\n\n'
					'From,\nEmely Lopez\nChief Academic Officer\nAssociated Students, Inc. CSULB\nOffice Location: USU 311\nEmail: Emely.Lopez-SA@csulb.edu')

        # Activate current timezone
        timezone.activate(pytz.timezone('America/Los_Angeles'))
        
        # Today
        today = timezone.localdate()
        six_days_ago = today - timedelta(days=6)
        nine_days_ago = today - timedelta(days=9)

        # Get rep meetings and reports
        reps_missing_reports = Representative.objects.prefetch_related(
			Prefetch(
				'committees',
				queryset=Committee.objects.prefetch_related('meetings').exclude(meetings__isnull=True)
			),
            'rep_reports'
		)

        meetings_six_days_ago = []
        meetings_nine_days_ago = []
        rep_count = 0
        
        for rep in reps_missing_reports:
            meetings_six_days_ago.clear()
            meetings_nine_days_ago.clear()

            for c in rep.committees.all():
                for m in c.meetings.all():
                    if (m.id, rep.id) not in [(r.meeting_id, r.representative_id) for r in rep.rep_reports.all()]:
                        if timezone.localdate(m.end_time) == six_days_ago:
                            meetings_six_days_ago.append(m)
                        if timezone.localdate(m.end_time) == nine_days_ago:
                            meetings_nine_days_ago.append(m)
            
            if meetings_six_days_ago:
                message = ('Missing Report(s) - First Reminder', text_email.format(rep.full_name, 6,
                    "\n".join([str(m) for m in meetings_six_days_ago])),
                    'noreply@asicsulb.org', [rep.email])
                messages.append(message)

            if meetings_nine_days_ago:
                message = ('Missing Report(s) - Final Reminder', text_email.format(rep.full_name, 9,
                    "\n".join([str(m) for m in meetings_nine_days_ago])),
                    'noreply@asicsulb.org', [rep.email, rep.chair_email])
                messages.append(message)
            
            if meetings_six_days_ago or meetings_nine_days_ago:
                rep_count += 1

        # Deactivate current timezone
        timezone.deactivate()

        # Send all messages
        if messages:
            send_mass_mail(tuple(messages))
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully sent {} missing report reminder(s) to {} representative(s).'
                    .format(len(messages), rep_count)
                )
            )