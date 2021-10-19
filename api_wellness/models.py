from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


def avatar_directory_path(instance, filename):
	return 'avatars/{0}-{1}'.format(instance.id, filename)

def badge_directory_path(instance, filename):
	return 'badges/{0}-{1}'.format(instance.name.lower(), filename)

def event_directory_path(instance, filename):
	return 'events/{0}-{1}'.format(slugify(instance.name), filename)

class CommonInfo(models.Model):
	name 		= models.CharField(max_length=75)
	description = models.TextField(blank=True)
	active 		= models.BooleanField(default=True)

	def __str__(self):
		return self.name

	class Meta:
		abstract = True
		ordering = ['name']

class Section(CommonInfo): # Inherits name and description fields
	def section_default():
		return Section.objects.get_or_create(name='Custom')[0].pk
	
	def event_default():
		return Section.objects.get_or_create(name='Events')[0].pk

class Category(CommonInfo): # Inherits name and description fields
	points 		= models.PositiveSmallIntegerField(default=1)
	section		= models.ForeignKey(Section, on_delete=models.PROTECT, related_name='categories', default=Section.section_default) # Column name: section_id

	def category_default():
		return Category.objects.get_or_create(name='Uncategorized')[0].pk

	class Meta(CommonInfo.Meta):
		verbose_name_plural = "categories"

class Activity(CommonInfo): # Inherits name and description fields
	description = None # Removes description field
	category 	= models.ForeignKey(Category, on_delete=models.PROTECT, related_name='activities', default=Category.category_default) # Column name: category_id

	class Meta(CommonInfo.Meta):
		verbose_name_plural = "activities"

class Event(CommonInfo): # Inherits name and description fields
	poster			= models.ImageField('Event Poster', upload_to=event_directory_path)
	points 			= models.PositiveSmallIntegerField(default=8)
	promote			= models.BooleanField(default=False)
	start			= models.DateTimeField()
	end 			= models.DateTimeField()
	location		= models.CharField(max_length=150)
	last_modified	= models.DateTimeField(auto_now=True)
	section			= models.ForeignKey(Section, on_delete=models.PROTECT, related_name='events', default=Section.event_default) # Column name: section_id

	class Meta:
		ordering = ['-start', 'name']

class Badge(CommonInfo):
	BADGE_LOGIN_MASTER = 'BLM'
	BADGE_SWIFT_SWIMMER = 'BSS'
	BADGE_GYM_RAT = 'BGR'
	BADGE_ROCKWALL_CHALLENGER = 'BRC'
	BADGE_INCLUSIVE_ACTIVIST = 'BIA'
	BADGE_OUTDOOR_ADVENTURER = 'BOA'
	BADGE_LEAGUE_CHAMP = 'BLC'
	BADGE_GAME_MASTER = 'BGM'
	BADGE_WELLNESS_WARRIOR = 'BWW'
	BADGE_BEACHPRIDE_CHAMPION = 'BBC'

	BADGE_CHOICES = (
		(BADGE_LOGIN_MASTER, 'Log-in Master'),
		(BADGE_SWIFT_SWIMMER, 'Swift Swimmer'),
		(BADGE_GYM_RAT, 'Gym Rat'),
		(BADGE_ROCKWALL_CHALLENGER, 'Rock Wall Challenger'),
		(BADGE_INCLUSIVE_ACTIVIST, 'Inclusive Activist'),
		(BADGE_OUTDOOR_ADVENTURER, 'Outdoor Adventurer'),
		(BADGE_LEAGUE_CHAMP, 'League Champ'),
		(BADGE_GAME_MASTER, 'Game Master'),
		(BADGE_WELLNESS_WARRIOR, 'Wellness Warrior'),
		(BADGE_BEACHPRIDE_CHAMPION, 'Beach Pride Champion'),
	)
	
	name = None # Removes name field
	code = models.CharField(max_length=3, choices=BADGE_CHOICES)
	description = models.TextField()
	message = models.TextField()
	icon = models.ImageField('Badge Icon', upload_to=badge_directory_path)
	points = models.PositiveSmallIntegerField()

	def __str__(self):
		return self.get_code_display()
	
	class Meta:
		ordering = []

class Milestone(models.Model):
	MILESTONE_1 = 'M1'
	MILESTONE_2	= 'M2'
	MILESTONE_3	= 'M3'
	MILESTONE_4	= 'M4'
	MILESTONE_5	= 'M5'

	MILESTONE_CHOICES = (
		(MILESTONE_1, 'Milestone 1'),
		(MILESTONE_2, 'Milestone 2'),
		(MILESTONE_3, 'Milestone 3'),
		(MILESTONE_4, 'Milestone 4'),
		(MILESTONE_5, 'Milestone 5'),
	)

	MILESTONE_EMAIL_SUBJECT = 'ASI Active: Your {} Reward Awaits You!'
	MILESTONE_FINAL_EMAIL_SUBJECT = 'ASI Active: YOU MADE IT!'
	MILESTONE_1_EMAIL_CONTENT = ('<p>Congratulations! You have reached your <span style="text-decoration: underline;">{}</span> milestone in ASI Active. '
								'To reward you for your hard work, your prize awaits. To claim your prize, please follow these steps:'
								'</p><ul><li>Go to Beach Balance, located on the second floor in the Student Recreation & Wellness Center during Beach Balance '
								'open hours<ul><li>10 a.m. and 8 p.m. Monday through Thursday</li><li>10 a.m. to 6 p.m. Fridays</li></ul></li>'
								'<li>Show the staff working the desk this e-mail and present your student ID</li><li>Collect your prize and celebrate your success</li></ul>'
								'<p>Keep up the good work!</p>')
	MILESTONE_2_EMAIL_CONTENT = ('<p>Congrats again, my friend! You have reached your <span style="text-decoration: underline;">{}</span> milestone in ASI Active. '
								'Focusing on maintaining a balanced lifestyle has its own benefits, but to top it off, let’s get you a prize to help celebrate your successes. '
								'To claim your prize, please follow these steps:</p><ul><li>Go to Beach Balance, located on the second floor in the Student '
								'Recreation & Wellness Center during Beach Balance open hours<ul><li>10 a.m. and 8 p.m. Monday through Thursday</li>'
								'<li>10 a.m. to 6 p.m. Fridays</li></ul></li><li>Show the staff working the desk this e-mail and present your student ID</li>'
								'<li>Collect your prize and rejoice in what you have achieved</li></ul><p>You’re doing great! Keep at it.</p>')
	MILESTONE_3_EMAIL_CONTENT = ('<p>Woah, we’re half way there! Congratulations, you have reached your <span style="text-decoration: underline;">{}</span> milestone in ASI Active. '
								'You’re are making great headway on your personal wellness. To commemorate this moment, let’s get you a reward. '
								'To claim your prize, please follow these steps:</p><ul><li>Go to Beach Balance, located on the second floor in the Student '
								'Recreation & Wellness Center during Beach Balance open hours<ul><li>10 a.m. and 8 p.m. Monday through Thursday</li>'
								'<li>10 a.m. to 6 p.m. Fridays</li></ul></li><li>Show the staff working the desk this e-mail and present your student ID</li>'
								'<li>Collect your prize and rejoice in what you have achieved</li></ul><p>Spectacular progress! Keep doing a great job.</p>')
	MILESTONE_4_EMAIL_CONTENT = ('<p>You are now a master at developing, progressing and maintaining you’re personal wellness. You have reached your '
								'<span style="text-decoration: underline;">{}</span> milestone in ASI Active. To applaud and commend your successes, '
								'your prize awaits. To claim your prize, please follow these steps:</p><ul><li>Go to Beach Balance, located on the second floor in the Student '
								'Recreation & Wellness Center during Beach Balance open hours<ul><li>10 a.m. and 8 p.m. Monday through Thursday</li>'
								'<li>10 a.m. to 6 p.m. Fridays</li></ul></li><li>Show the staff working the desk this e-mail and present your student ID</li>'
								'<li>Collect your prize and rejoice in what you have achieved</li></ul><p>Tremendous work! Don’t stop now, you’re so close '
								'to 100% completion of this program.</p>')
	MILESTONE_5_EMAIL_CONTENT = ('<p>You deserve a huge round of applause!</p><p>You have reached your {} milestone in ASI Active. Your tenacity and persistence '
								'to your health and this program has now entered you into a drawing for a chance to win one of three $500 scholarships, brought to you by '
								'ShoolsFirst Credit Union.  The drawing will take place during the spring 2018 employee recognition program. However, don’t let this slow '
								'down your forward momentum. Continue striving for a balanced lifestyle that focuses on all the dimensions of wellness. Expect an e-mail '
								'in the spring for the dates and times of the ASI student staff appreciation event.</p>')

	name = models.CharField(max_length=2, choices=MILESTONE_CHOICES)
	points = models.PositiveSmallIntegerField()

	def __str__(self):
		return self.get_name_display()
	
	def get_email_content(self, milestone):
		if milestone == self.MILESTONE_1:
			return {'milestone': 'first', 'subject': self.MILESTONE_EMAIL_SUBJECT, 'message': self.MILESTONE_1_EMAIL_CONTENT}
		elif milestone == self.MILESTONE_2:
			return {'milestone': 'second', 'subject': self.MILESTONE_EMAIL_SUBJECT, 'message': self.MILESTONE_2_EMAIL_CONTENT}
		elif milestone == self.MILESTONE_3:
			return {'milestone': 'third', 'subject': self.MILESTONE_EMAIL_SUBJECT, 'message': self.MILESTONE_3_EMAIL_CONTENT}
		elif milestone == self.MILESTONE_4:
			return {'milestone': 'fourth', 'subject': self.MILESTONE_EMAIL_SUBJECT, 'message': self.MILESTONE_4_EMAIL_CONTENT}
		elif milestone == self.MILESTONE_5:
			return {'milestone': 'final', 'subject': self.MILESTONE_FINAL_EMAIL_SUBJECT, 'message': self.MILESTONE_5_EMAIL_CONTENT}

class ProfileManager(models.Manager):
	def create_profile(self, validated_data):
		user_data = validated_data.pop('user')
		extra_fields = {
			'first_name': user_data['first_name'],
			'last_name': user_data['last_name']
        }

		# Create User - username, first_name, last_name, email, password
		user = User.objects.create_user(
			user_data['username'],
			user_data['email'],
			user_data['password'],
			**extra_fields
		)

		# Create profile
		profile = Profile(
			user=user,
			id=validated_data['id'],
			dob=validated_data.get('dob'),
			gender=validated_data.get('gender', ''),
			dept=validated_data['dept']
		)
		profile.save()

		return profile
	
	def update_profile(self, instance, validated_data):
		user_data = validated_data.pop('user')
		# Get user from instance
		user = instance.user

		# Save user data to instance
		user.first_name = user_data.get('first_name', user.first_name)
		user.last_name = user_data.get('last_name', user.last_name)
		user.email = user_data.get('email', user.email)
		user.save()
		
		# Save profile data to instance
		instance.id = validated_data.get('id', instance.id)
		instance.dob = validated_data.get('dob', instance.dob)		
		instance.gender = validated_data.get('gender', instance.gender)
		instance.dept = validated_data.get('dept', instance.dept)
		instance.save()
		
		return instance

class Profile(models.Model):	
	NOT_SPECIFIED				= ''
	
	GENDER_MALE					= 'MALE'
	GENDER_FEMALE				= 'FEMA'
	GENDER_QUEER				= 'QUEE'
	GENDER_QUEER_TMASC			= 'QTMA'
	GENDER_QUEER_TFEMI			= 'QTFE'
	GENDER_NON_BINARY			= 'NBIN'
	GENDER_ANONYMOUS			= 'ANON'

	GENDER_CHOICES		= (
		(NOT_SPECIFIED, 'Please select your gender'),
		(GENDER_MALE,	'Man'),
		(GENDER_FEMALE,	'Woman'),
		(GENDER_QUEER,	'Queer'),
		(GENDER_QUEER_TMASC, 'Queer Transmasculine'),
		(GENDER_QUEER_TFEMI, 'Queer Transfeminine'),
		(GENDER_NON_BINARY,	'Non-binary'),
		(GENDER_ANONYMOUS,	'Prefer not to disclose'),
	)

	DEPT_CDC	= 'CDC'
	DEPT_BO		= 'BO'
	DEPT_HR		= 'HR'
	DEPT_IT		= 'IT'
	DEPT_GOV	= 'GOV'
	DEPT_BPE	= 'BPE'	
	DEPT_COM	= 'COM'
	DEPT_SM		= 'SM'
	DEPT_FM		= 'FM'
	DEPT_RC		= 'RC'
	DEPT_UBM	= 'UBM'
	DEPT_CE		= 'CE'
	DEPT_MBP	= 'MBP'
	DEPT_GCI	= 'GCI'
	DEPT_FIT	= 'FIT'
	DEPT_INT	= 'INT'
	DEPT_AQU	= 'AQU'
	DEPT_MB		= 'MB'
	DEPT_RBB	= 'RBB'
	DEPT_MA		= 'MA'
	DEPT_SBM	= 'SBM'

	DEPT_CHOICES 		= (
		(NOT_SPECIFIED, 'Please select your department'),
		(DEPT_CDC, 		'Isabel Patterson Child Development Center'),
		(DEPT_BO, 		'Business Office'),
		(DEPT_HR, 		'Human Resources'),
		(DEPT_IT, 		'IT'),
		(DEPT_GOV, 		'Student Government'),
		(DEPT_BPE, 		'Beach Pride Events'),
		(DEPT_COM, 		'ASI Communications'),
		(DEPT_SM, 		'Student Media'),
		(DEPT_FM, 		'Facilities & Maintenance'),
		(DEPT_RC, 		'Recycling Center'),
		(DEPT_UBM, 		'USU - Building Managers'),
		(DEPT_CE, 		'Conference & Events'),
		(DEPT_MBP, 		'Maxson & Beach Pantry'),
		(DEPT_GCI, 		'Games, Candy, Info & Ticket Center'),
		(DEPT_FIT, 		'SRWC - Fitness'),
		(DEPT_INT, 		'SRWC - Intramurals'),
		(DEPT_AQU, 		'SRWC - Aquatics'),
		(DEPT_MB, 		'SRWC - Membership'),
		(DEPT_RBB, 		'SRWC - ROA/Beach Balance'),
		(DEPT_MA, 		'SRWC - Membership & Admin'),
		(DEPT_SBM, 		'SRWC - Building Managers'),
	)

	# Extends User model
	# Using following columns from parent class: username, first_name, last_name, email, password
	user 		= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True) # Column name: user_id
	id 			= models.CharField('Student/Employee ID', max_length=10, unique=True)
	dob			= models.DateField('Date of Birth', null=True, blank=True)
	avatar		= models.ImageField('Profile Picture', upload_to=avatar_directory_path, null=True, blank=True)
	gender		= models.CharField(max_length=4, choices=GENDER_CHOICES, blank=True)
	dept 		= models.CharField('Department', max_length=3, choices=DEPT_CHOICES)
	categories	= models.ManyToManyField(Category, through='ActivityLog', related_name='users')
	events		= models.ManyToManyField(Event, through='EventLog', related_name='users')
	badges		= models.ManyToManyField(Badge, through='UserBadge', related_name='users')
	milestones	= models.ManyToManyField(Milestone, through='UserMilestone', related_name='users')
	
	# Custom Manager
	objects = ProfileManager()
	
	def __str__(self):
		return self.user.get_full_name()
	
	def get_absolute_url(self):
		from django.urls import reverse
		return reverse('api:user-detail', args=[str(self.user_id)])

class ActivityLog(models.Model):
	profile 	= models.ForeignKey(Profile, on_delete=models.CASCADE) # Column name: profile_id
	category 	= models.ForeignKey(Category, on_delete=models.CASCADE) # Column name: category_id
	datetime 	= models.DateTimeField()

	class Meta:
		unique_together = ('profile', 'datetime')

class EventLog(models.Model):
	profile 	= models.ForeignKey(Profile, on_delete=models.CASCADE) # Column name: profile_id
	event 		= models.ForeignKey(Event, on_delete=models.CASCADE) # Column name: event_id
	datetime 	= models.DateTimeField()

	class Meta:
		unique_together = ('profile', 'event')

class UserBadge(models.Model):
	profile 	= models.ForeignKey(Profile, on_delete=models.CASCADE) # Column name: profile_id
	badge 		= models.ForeignKey(Badge, on_delete=models.CASCADE) # Column name: badge_id
	datetime 	= models.DateTimeField()

	class Meta:
		unique_together = ('profile', 'badge')

class UserMilestone(models.Model):
	profile 	= models.ForeignKey(Profile, on_delete=models.CASCADE) # Column name: profile_id
	milestone 	= models.ForeignKey(Milestone, on_delete=models.CASCADE) # Column name: milestone_id
	datetime 	= models.DateTimeField()

	class Meta:
		unique_together = ('profile', 'milestone')

class Feedback(models.Model):	
	message		= models.TextField()
	datetime 	= models.DateTimeField()
	profile 	= models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='get_user_feedback') # Column name: profile_id

	def __str__(self):
		return self.message
	
	class Meta:
		verbose_name_plural = "feedback"
