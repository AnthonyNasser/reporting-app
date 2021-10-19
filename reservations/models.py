from django.db import models
from django.forms import ModelForm
from django.utils import timezone

"""
Primary keys are created automatically by Django for each model below using the following format:
	id = models.AutoField(primary_key=True)

"""

class Category(models.Model):
	name = models.CharField(max_length=30)

	def category_default():
		return Category.objects.get_or_create(name='Uncategorized')[0].pk

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']
		verbose_name_plural = 'categories'

class Item(models.Model):
	CONDITION_GOOD		= 'G'
	CONDITION_FAIR		= 'F'
	CONDITION_DAMAGE	= 'D'

	CONDITION_CHOICES 	= (
		(CONDITION_GOOD, 'Good'),
		(CONDITION_FAIR, 'Fair'),
		(CONDITION_DAMAGE, 'Damage'),
	)

	name 			= models.CharField(max_length=30)
	model 			= models.CharField(max_length=30, blank=True)
	label			= models.CharField(max_length=30, unique=True)
	serial			= models.CharField(max_length=30, blank=True)	
	condition 		= models.CharField(max_length=1, choices=CONDITION_CHOICES, default=CONDITION_GOOD)
	misc			= models.TextField(blank=True)
	category 		= models.ForeignKey(Category, on_delete=models.SET_DEFAULT, related_name='items', default=Category.category_default) # Column name: category_id	

	def __str__(self):
		return '%s - %s' % (self.name, self.label)

	class Meta:
		ordering = ['label', 'name']

class Department(models.Model):
	name 			= models.CharField(max_length=50)
	color			= models.CharField(max_length=7, default='#000') # Default: Black

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

class User(models.Model):
	# Supervisors for ACVP & 22 West Video
	ERS_ACVP_SUP = 'abby.victor-SA@csulb.edu'
	ERS_CBTV_SUP = 'sarrelskatie@gmail.com'

	# Administrators
	ERS_ADMINS = [ERS_ACVP_SUP, ERS_CBTV_SUP]
	# ERS_ADMINS = ['webmaster@asicsulb.org']

	STAFF 			= 'S'

	TITLE_CHOICES = (
		(STAFF, 	'Staff'),
	)

	first_name		= models.CharField(max_length=100)
	last_name		= models.CharField(max_length=100)
	email			= models.EmailField()
	phone			= models.CharField(max_length=10, blank=True)
	sid 			= models.CharField('Student ID', max_length=12)
	title 			= models.CharField(max_length=1, choices=TITLE_CHOICES, default=STAFF)
	department 		= models.ForeignKey(Department, on_delete=models.PROTECT, related_name='users') # Column name: department_id

	def _get_full_name(self):
		return '%s %s' % (self.first_name, self.last_name)
	
	full_name = property(_get_full_name)
	
	def is_staff(self):
		return self.title in (self.STAFF)

	def __str__(self):
		return '%s %s' % (self.first_name, self.last_name)

	class Meta:
		ordering = ['first_name', 'last_name']

class Reservation(models.Model):
	STATE_RESERVED	= 1
	STATE_APPROVED	= 2
	STATE_CHECKOUT	= 3
	STATE_CHECKIN	= 4

	STATE_CHOICES 	= (
		(STATE_RESERVED, 'Reserved'),
		(STATE_APPROVED, 'Approved'),
		(STATE_CHECKOUT, 'Checkout'),
		(STATE_CHECKIN, 'Checkin'),
	)

	project			= models.CharField(max_length=100)
	start_date		= models.DateTimeField(default=timezone.now)
	end_date		= models.DateTimeField(default=timezone.now)		
	state 			= models.IntegerField(choices=STATE_CHOICES, default=STATE_RESERVED)
	crew 	 		= models.TextField(blank=True)
	comment 		= models.TextField(blank=True)	
	user 			= models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations') # Column name: user_id
	items			= models.ManyToManyField(Item, related_name='reservations')

	class Meta:
		ordering	= ['start_date', 'project']

	def __str__(self):
		return 'Project Title: %s, Start Date: %s, End Date: %s' % (self.project, str(self.start_date), str(self.end_date))

	def get_absolute_url(self):
		from django.urls import reverse
		return reverse('reservations:reserve-edit', args=[str(self.id)])	

	def get_item_list(self):
		return self.items

	def get_crew_list(self):
		return self.crew

	EMAIL_ADMIN_RESERVATION_APPROVAL = ('Beach Pride Admins,\n\n%s has reserved the following equipment for %s '
											'from %s to %s. %s\n\n%s\n\nThe crewmembers on set are: %s\n\nThe following comment was included: %s\n\n'
											'Please visit http://asicsulb.org/apps/reservations/approve/%s to approve this reservation.')
	EMAIL_ADMIN_RESERVATION_APPROVAL_HTML = ('<p>Beach Pride Admins,</p><p>%s has reserved the following equipment for %s '
											'from %s to %s. %s</p><ol>%s</li></ol><p>The crewmembers on set are: %s</p><p>The following comment was included: %s</p>'
											'<p>Please click <a href="http://asicsulb.org/apps/reservations/approve/%s" target="_blank">here</a> to approve this reservation.</p>')
	EMAIL_STAFF_APPROVAL = ('%s,\n\nYou have successfully reserved the following equipment for %s from %s to %s.\n\n%s\n\nThe crewmembers on your set are: %s\n\n%s')
	EMAIL_STAFF_DECLINE = ('%s,\n\nYour reservation for %s from %s to %s has been declined or deleted. No equipment has been reserved.\n\n%s')
	EMAIL_ADMIN_INVENTORY_COMMENT = ('Beach Pride Admins,\n\nThe following item has received a new comment:\n\n%s - %s: "%s"')
	EMAIL_STAFF_REMINDER = ('%s,\n\nThis email is a reminder that you have an equipment reservation pickup for today at %s.\n\nIf you wish to cancel this reservation, please '
							'visit http://asicsulb.org/apps/reservations/reserve/%s/ and click the "Delete" button to cancel your reservation.')

class ReservationForm(ModelForm):
	class Meta:
		model 	= Reservation
		fields	= ['user', 'project', 'start_date', 'end_date', 'items', 'crew', 'comment']
		localized_fields = ('start_date', 'end_date')

class Log(models.Model):
	LOG_EVENT_CREATED			= 1
	LOG_EVENT_DELETED			= 2
	LOG_EVENT_APPROVED			= 3
	LOG_EVENT_DECLINED			= 4
	LOG_EVENT_CHECKED_OUT		= 5
	LOG_EVENT_CHECKED_IN		= 6
	LOG_EVENT_SAVED				= 7

	LOG_EVENT_CHOICES = (
		(LOG_EVENT_CREATED, 'Created'),
		(LOG_EVENT_DELETED, 'Deleted'),
		(LOG_EVENT_APPROVED, 'Approved'),
		(LOG_EVENT_DECLINED, 'Declined'),
		(LOG_EVENT_CHECKED_OUT, 'Checked out'),
		(LOG_EVENT_CHECKED_IN, 'Checked in'),
		(LOG_EVENT_SAVED, 'Saved'),
	)

	log_event		= models.IntegerField(choices=LOG_EVENT_CHOICES)
	message			= models.CharField(max_length=255, blank=True)
	timestamp		= models.DateTimeField(auto_now_add=True)
	reservation 	= models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, related_name='logs') # Column name: reservation_id

	def __str__(self):
		return '{:%Y-%m-%d %I:%M:%S} - Reservation {} was {}'.format(self.timestamp, self.reservation, self.get_log_event_display())

	class Meta:
		ordering = ['-timestamp']