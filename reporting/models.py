import pytz

from django.db import models
from django.urls import reverse
from django.utils import timezone

class Committee(models.Model):
    ACADEMIC = 'ACAD'
    UNIVERSITY = 'UNIV'
    COMMITTEE_TYPE = (
        (ACADEMIC, 'Academic Senate Committee'),
        (UNIVERSITY, 'University Committee'),
    )

    name = models.CharField(max_length=100)
    num_of_seats = models.PositiveSmallIntegerField()
    contact = models.EmailField('Contact Email')
    committee_type = models.CharField(max_length=4, choices=COMMITTEE_TYPE, default=ACADEMIC)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('reporting:committee-detail', kwargs={'pk': self.pk})

class Representative(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=150)
    chair_email = models.EmailField('ASI Board Chair\'s Email')
    committees = models.ManyToManyField(Committee, related_name='representatives', blank=True)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('reporting:representative-detail', kwargs={'pk': self.pk})

class Meeting(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    schedule = models.TextField(default='', blank=False)
    active = models.BooleanField(default=True)
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name='meetings') # committee_id

    def __str__(self):
        # Activate current timezone
        timezone.activate(pytz.timezone('America/Los_Angeles'))

        return '%s - %s from %s to %s in %s' % (
            self.committee, timezone.localtime(self.start_time).strftime('%a, %x'),
            timezone.localtime(self.start_time).strftime('%I:%M %p'),
            timezone.localtime(self.end_time).strftime('%I:%M %p'),
            self.location
        )

        # Deactivate current timezone
        timezone.deactivate()

    def get_absolute_url(self):
        return reverse('reporting:meeting-detail', kwargs={'pk': self.pk})

class Report(models.Model):
    purpose = models.TextField()
    business = models.TextField()
    description = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)
    submitted_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='meeting_reports') # meeting_id
    representative = models.ForeignKey(Representative, on_delete=models.SET_NULL, null=True, related_name='rep_reports') # representative_id

    def get_absolute_url(self):
        return reverse('reporting:report-detail', kwargs={'pk': self.pk})