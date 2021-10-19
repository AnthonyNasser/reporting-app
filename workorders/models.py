from django.db import models
from django.conf import settings

class Category(models.Model):
	name			= models.CharField(max_length=50)

	class Meta:
		verbose_name_plural = 'categories'

	def __str__(self):
		return 'Category Name: %s' % self.name

class Product(models.Model):
	name			= models.CharField(max_length=50)
	category 		= models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products') # Column name: category_id	

	def __str__(self):
		return 'Product Name: %s' % self.name

class Dimension(models.Model):
	name 			= models.CharField(max_length=50)
	product 		= models.ForeignKey(Product, on_delete=models.PROTECT, related_name='dimensions') # Column name: product_id

	def __str__(self):
		return 'Dimension Name: %s' % self.name

class Style(models.Model):
	name 			= models.CharField(max_length=50)
	dimension 		= models.ForeignKey(Dimension, on_delete=models.PROTECT, related_name='styles') # Column name: dimension_id	

	def __str__(self):
		return 'Style Name: %s' % self.name

class Package(models.Model):
	name			= models.CharField(max_length=50)	
	products 		= models.ManyToManyField(Product, through='Package_Products', related_name='packages')

	def __str__(self):
		return 'Package Name: %s' % self.name

class Package_Products(models.Model):
	package 		= models.ForeignKey(Package, on_delete=models.CASCADE)
	product 		= models.ForeignKey(Product, on_delete=models.CASCADE)	
	cost			= models.DecimalField(max_digits=8, decimal_places=2, blank=True) # Up to 999,999.99

class Department(models.Model):
	name			= models.CharField(max_length=50)

	def __str__(self):
		return 'Department Name: %s' % (self.name)

class User(models.Model):		
	CLIENT				= 'C'
	DESIGNER 			= 'D'
	SUPERVISOR			= 'S'

	TITLE_CHOICES = (
		(CLIENT, 		'Client'),
		(DESIGNER, 		'Designer'),
		(SUPERVISOR, 	'Supervisor'),		
	)

	# Extends User model
	# Using following columns from parent class: username, first_name, last_name, email, password
	user 			= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)	
	#sid 			= models.CharField(max_length=15, blank=True)
	phone			= models.CharField(max_length=15, blank=True)
	title 			= models.CharField(max_length=1, choices=TITLE_CHOICES, default=CLIENT)
	avatar			= models.ImageField(upload_to='avatars/') # Saves to avatars directory
	department		= models.ForeignKey(Department, on_delete=models.SET_NULL, related_name='users', blank=True, null=True) # Column name: department_id

	def __str__(self):
		return 'User: %s %s - %s' % (self.first_name, self.last_name, self.department)

class WorkOrder(models.Model):
	STATUS_PENDING_APPROVAL			= 1
	STATUS_NOT_STARTED				= 2	
	STATUS_IN_PROGRESS				= 3
	STATUS_ON_HOLD					= 4
	STATUS_COMPLETED				= 5
	STATUS_CANCELLED				= 6

	STATUS_CHOICES 					= (
		(STATUS_PENDING_APPROVAL, 	'Pending Approval'),
		(STATUS_NOT_STARTED, 		'Not Started'),
		(STATUS_IN_PROGRESS, 		'In Progress'),
		(STATUS_ON_HOLD, 			'On Hold'),
		(STATUS_COMPLETED, 			'Completed'),
		(STATUS_CANCELLED, 			'Cancelled'),
	)

	project			= models.CharField(max_length=50)
	deadline		= models.DateTimeField(blank=True, null=True)
	budget			= models.DecimalField(max_digits=8, decimal_places=2) # Up to 999,999.99
	status	 		= models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_NOT_STARTED) # Values from 0 to 32767
	event_start		= models.DateTimeField(blank=True, null=True)
	event_end		= models.DateTimeField(blank=True, null=True)
	created			= models.DateTimeField(auto_now_add=True)
	modified		= models.DateTimeField(auto_now=True)
	user 			= models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_workorders') # Column name: user_id
	designer		= models.ForeignKey(User, on_delete=models.SET_NULL, related_name='designer_workorders', blank=True, null=True) # Column name: designer_id	
	products 		= models.ManyToManyField(Product, through='WorkOrder_Products', related_name='workorders')

	class Meta:
		permissions	= (
			('approve_workorders', 'Approve work orders'),
			('decline_workorders', 'Decline work orders'),
		)

	def __str__(self):
		return 'Project Name: %s, Deadline: %s, User: %s' % (self.project, str(self.deadline), self.user)

class Asset(models.Model):
	file			= models.FileField(upload_to='uploads/%Y/') # Saves to uploads/{CURRENT_YEAR} directory
	created			= models.DateTimeField(auto_now_add=True)
	modified		= models.DateTimeField(auto_now=True)
	workorder 		= models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='assets') # Column name: workorder_id

	def __str__(self):
		return 'Image Name: %s' % (self.file.name)

class WorkOrder_Products(models.Model):
	workorder 		= models.ForeignKey(WorkOrder, on_delete=models.CASCADE) # Column name: workorder_id
	product 		= models.ForeignKey(Product, on_delete=models.CASCADE) # Column name: product_id
	quantity		= models.PositiveSmallIntegerField(default=1) # Values from 0 to 32767